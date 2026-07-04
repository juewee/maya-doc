const cheerio = require('cheerio');
const fs = require('fs');
const path = require('path');

// 解析 CLI 参数
const args = process.argv.slice(2);
const versionArg = args.find(a => a.startsWith('--version='));
const VERSION = versionArg ? versionArg.split('=')[1] : '2025';

const BASE = `https://help.autodesk.com/cloudhelp/${VERSION}/CHS/Maya-Tech-Docs/Commands`;
const OUTPUT_DIR = path.join(__dirname, '..', 'output', VERSION);
const OUTPUT_FILE = path.join(OUTPUT_DIR, 'index.json');

const CAT_PAGES = [
  'cat_General', 'cat_Language', 'cat_Modeling', 'cat_Animation',
  'cat_Rendering', 'cat_Effects', 'cat_System', 'cat_Windows',
];

const cmdIndex = {};

async function scrapeCatPage(catName) {
  const url = `${BASE}/${catName}.html`;
  console.log(`Fetching ${catName}...`);
  const resp = await fetch(url);
  const html = await resp.text();
  const $ = cheerio.load(html);

  const mainCat = $('h2').first().text().trim();
  let cmdCount = 0;

  // 所有版本（2020/2025）的 cat 页面都使用 javascript:go(...) 链接
  $('table').each((i, table) => {
    const $table = $(table);

    // 找前一个文本节点或 h2 作为子分类
    let subCat = mainCat;
    let prev = table.previousSibling;
    while (prev) {
      if (prev.type === 'text') {
        const txt = prev.data.trim();
        if (txt && txt.length < 200 && !txt.includes('Copyright') && !txt.includes('\u00a9')) {
          subCat = txt;
          break;
        }
      } else if (prev.type === 'tag' && prev.name === 'h2') {
        break;
      }
      prev = prev.previousSibling;
    }

    $table.find('a[href^="javascript:go("]').each((j, a) => {
      const $a = $(a);
      const name = $a.text().trim();
      if (!name) return;

      const parentHtml = $a.parent().html() || '';
      const isMelScript = parentHtml.includes('MEL.gif');
      cmdCount++;

      if (!cmdIndex[name]) {
        cmdIndex[name] = { category: mainCat, subcategory: subCat, isMelScript };
      } else {
        const existing = cmdIndex[name];
        if (!existing.categories) {
          cmdIndex[name] = {
            categories: [
              { category: existing.category, subcategory: existing.subcategory },
              { category: mainCat, subcategory: subCat }
            ],
            isMelScript: existing.isMelScript || isMelScript
          };
        } else {
          existing.categories.push({ category: mainCat, subcategory: subCat });
          existing.isMelScript = existing.isMelScript || isMelScript;
        }
      }
    });
  });

  console.log(`  ${mainCat}: ${cmdCount} commands`);
  return mainCat;
}

async function main() {
  console.log(`=== Maya ${VERSION} 命令分类索引爬虫 ===\n`);

  for (const catName of CAT_PAGES) {
    await scrapeCatPage(catName);
  }

  // 统计
  console.log('\n=== Command Index Summary ===');
  const stats = {};
  for (const [name, info] of Object.entries(cmdIndex)) {
    let cat = info.categories ? info.categories[0].category : info.category;
    if (!stats[cat]) stats[cat] = { total: 0, subs: {} };
    stats[cat].total++;
    const sub = info.categories ? info.categories[0].subcategory : info.subcategory;
    if (!stats[cat].subs[sub]) stats[cat].subs[sub] = 0;
    stats[cat].subs[sub]++;
  }

  for (const [cat, data] of Object.entries(stats)) {
    console.log(`  ${cat} (${data.total} commands)`);
    for (const [sub, count] of Object.entries(data.subs)) {
      console.log(`    - ${sub}: ${count}`);
    }
  }
  console.log(`\n  Total unique: ${Object.keys(cmdIndex).length}`);

  // 保存
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  fs.writeFileSync(OUTPUT_FILE, JSON.stringify(cmdIndex, null, 2), 'utf-8');
  console.log(`${OUTPUT_FILE} saved`);
}

main().catch(e => console.error(e));
