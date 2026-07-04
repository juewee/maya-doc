const fs = require('fs');
const path = require('path');
const cheerio = require('cheerio');

// 解析 CLI 参数
const args = process.argv.slice(2);
const versionArg = args.find(a => a.startsWith('--version='));
const VERSION = versionArg ? versionArg.split('=')[1] : '2025';

const BASE_URL = `https://help.autodesk.com/cloudhelp/${VERSION}/CHS/Maya-Tech-Docs`;
const COMMANDS_INDEX = `${BASE_URL}/Commands/index_all.html`;
const PYTHON_CMDS_DIR = `${BASE_URL}/CommandsPython`;
const OUTPUT_DIR = path.join(__dirname, '..', 'output', VERSION);
const OUTPUT_FILE = path.join(OUTPUT_DIR, 'maya_commands_python.json');
const CONCURRENCY = 15;
const BATCH_DELAY = 1000;

async function getCommandList() {
  console.log(`[Maya ${VERSION}] 正在获取命令列表...`);
  const resp = await fetch(COMMANDS_INDEX);
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
  const html = await resp.text();
  const $ = cheerio.load(html);

  const commands = [];

  // 2025+ 版本使用 target="contentFrame"，老版本没有
  const v = parseInt(VERSION);
  const selector = v >= 2025
    ? 'a[href$=".html"][target="contentFrame"]'
    : 'a[href$=".html"]';

  $(selector).each((i, el) => {
    const name = $(el).text().trim();
    const href = $(el).attr('href');
    if (name && href && href !== 'index.html') {
      commands.push({ name, href });
    }
  });

  console.log(`共找到 ${commands.length} 个命令`);
  return commands;
}

async function scrapeCommand(command, index, total) {
  const url = `${PYTHON_CMDS_DIR}/${command.href}`;
  try {
    const resp = await fetch(url);
    if (!resp.ok) {
      return { name: command.name, description: '', examples: '', error: `HTTP ${resp.status}` };
    }
    const html = await resp.text();
    const $ = cheerio.load(html);
    const funcName = $('h1').first().text().trim() || command.name;

    // 提取简介
    let description = '';
    const bodyText = $('body').text();

    $('h2').each((i, el) => {
      if (description) return;
      if ($(el).text().trim() === 'Synopsis') {
        let next = $(el).next();
        let passedSynopsis = false;
        let passedUndoable = false;
        let descParts = [];
        while (next.length) {
          if (next.prop('tagName') === 'H2') break;
          const tag = next.prop('tagName');
          const txt = (next.text() || '').trim();

          if (tag === 'P' && next.attr('id') === 'synopsis') {
            passedSynopsis = true;
            const noteIdx = txt.indexOf('This is not depicted in the synopsis.');
            if (noteIdx > -1) {
              const afterNote = txt.slice(noteIdx + 37).trim();
              if (afterNote) descParts.push(afterNote);
            }
          } else if (tag === 'P' && /is (NOT )?undoable/i.test(txt)) {
            passedUndoable = true;
          } else if (passedSynopsis && passedUndoable && txt) {
            descParts.push(txt);
          } else if (passedSynopsis && !passedUndoable && tag !== 'P') {
            passedUndoable = true;
            if (txt) descParts.push(txt);
          }
          next = next.next();
        }
        if (descParts.length > 0) {
          description = descParts.join(' ').trim();
        }
      }
    });

    // 兜底：用 bodyText 提取
    if (!description) {
      const synopsisIdx = bodyText.indexOf('Synopsis\n');
      if (synopsisIdx > -1) {
        const afterSynopsis = bodyText.slice(synopsisIdx + 9);
        const endMarkers = ['Return value', 'Keywords', 'Related\n'];
        let endIdx = afterSynopsis.length;
        for (const m of endMarkers) {
          const idx = afterSynopsis.indexOf(m);
          if (idx > -1) endIdx = Math.min(endIdx, idx);
        }
        const lines = afterSynopsis.slice(0, endIdx).split('\n').filter(l => l.trim());
        const cleanLines = lines.map(l => {
          const noteEnd = l.indexOf('This is not depicted in the synopsis.');
          if (noteEnd > -1) {
            const afterNote = l.slice(noteEnd + 37).trim();
            if (afterNote) return afterNote;
            return '';
          }
          return l;
        }).filter(l => {
          const t = l.trim();
          return t &&
            !t.match(/^Note: Strings representing object names/) &&
            !t.match(/^[a-zA-Z][a-zA-Z0-9]* is (NOT )?undoable/i);
        });
        const finalLines = cleanLines.filter(l =>
          !l.trim().match(/^[a-zA-Z][a-zA-Z0-9]*\s*\(\[.*\]\s*\)\s*$/)
        );
        description = finalLines.join(' ').trim();
      }
    }
    description = description.replace(/\s+/g, ' ').trim().slice(0, 1500);

    // 提取 Python 示例
    let examples = '';
    $('h2').each((i, el) => {
      if ($(el).text().includes('Python examples')) {
        let next = $(el).next();
        while (next.length) {
          if (next.prop('tagName') === 'PRE') examples += next.text().trim() + '\n\n';
          if (['H2', 'HR'].includes(next.prop('tagName'))) break;
          next = next.next();
        }
      }
    });
    if (!examples) {
      const peIdx = bodyText.indexOf('Python examples');
      if (peIdx > -1) {
        const afterPE = bodyText.slice(peIdx + 16).trim();
        if (!afterPE.startsWith('Synopsis')) {
          const endMarkers = ['\n\n\n', 'Related topics', 'Copyright ', 'Creative Commons'];
          let endIdx = afterPE.length;
          for (const m of endMarkers) {
            const idx = afterPE.indexOf(m);
            if (idx > -1) endIdx = Math.min(endIdx, idx);
          }
          examples = afterPE.slice(0, endIdx).trim();
          if (examples.length < 30) examples = '';
        }
      }
    }
    examples = examples.slice(0, 3000).trim();

    console.log(`[${index + 1}/${total}] \u2713 ${command.name}`);
    return { name: funcName, description, examples, url };
  } catch (err) {
    return { name: command.name, description: '', examples: '', error: err.message };
  }
}

async function batchExecute(tasks, batchSize) {
  const results = [];
  for (let i = 0; i < tasks.length; i += batchSize) {
    const batch = tasks.slice(i, i + batchSize);
    const batchResults = await Promise.all(batch.map((t, j) => t(i + j)));
    results.push(...batchResults);
    if (i + batchSize < tasks.length) {
      await new Promise(r => setTimeout(r, 200));
    }
    if (Math.floor((i + batchSize) / 100) > Math.floor(i / 100)) {
      console.log(`进度: ${Math.min(i + batchSize, tasks.length)}/${tasks.length}`);
    }
  }
  return results;
}

async function main() {
  console.log(`=== Maya ${VERSION} Python 命令爬虫 ===\n`);
  const commands = await getCommandList();
  if (commands.length === 0) return;

  const tasks = commands.map((cmd, i) => {
    return async (idx) => {
      return await scrapeCommand(cmd, idx, commands.length);
    };
  });

  console.log(`\n开始爬取 ${commands.length} 个命令 (并发: ${CONCURRENCY})...\n`);
  const results = await batchExecute(tasks, CONCURRENCY);

  const successCount = results.filter(r => !r.error).length;
  const withDesc = results.filter(r => r.description).length;
  const withExamples = results.filter(r => r.examples).length;
  const errorCount = results.filter(r => r.error).length;

  const output = {
    meta: {
      source: BASE_URL,
      version: `Maya ${VERSION}`,
      total: commands.length,
      success: successCount,
      withDescription: withDesc,
      withExamples: withExamples,
      errors: errorCount,
      timestamp: new Date().toISOString()
    },
    commands: results
  };

  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  fs.writeFileSync(OUTPUT_FILE, JSON.stringify(output, null, 2), 'utf-8');
  console.log(`\n=== 爬取完成 ===`);
  console.log(`总计: ${commands.length} | 成功: ${successCount} | 有简介: ${withDesc} | 有示例: ${withExamples} | 错误: ${errorCount}`);
  console.log(`结果: ${OUTPUT_FILE}`);
}

main().catch(console.error);
