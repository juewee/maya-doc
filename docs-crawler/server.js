const http = require('http');
const https = require('https');
const fs = require('fs');
const path = require('path');
const url = require('url');

const PORT = 3000;
const ROOT = path.join(__dirname, '..');

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript',
  '.json': 'application/json',
  '.css': 'text/css',
  '.png': 'image/png',
  '.svg': 'image/svg+xml',
};

http.createServer((req, res) => {
  const parsedUrl = url.parse(req.url, true);

  // Proxy endpoint: /proxy?url=https://help.autodesk.com/...
  if (parsedUrl.pathname === '/proxy' && parsedUrl.query.url) {
    return proxyAutodesk(parsedUrl.query.url, res);
  }

  // Static file serving
  const defaultFile = req.url === '/' ? '/browse.html' : req.url.split('?')[0];
  let filePath = path.join(ROOT, defaultFile);
  filePath = path.normalize(filePath);

  if (!filePath.startsWith(ROOT)) {
    res.writeHead(403);
    return res.end('Forbidden');
  }

  const ext = path.extname(filePath);
  const mime = MIME[ext] || 'application/octet-stream';

  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404);
      res.end('Not Found');
      return;
    }
    res.writeHead(200, { 'Content-Type': mime });
    res.end(data);
  });
}).listen(PORT, () => {
  console.log(`Maya Command Browser ready at http://localhost:${PORT}`);
});

function proxyAutodesk(targetUrl, res) {
  const parsed = url.parse(targetUrl);
  const proto = parsed.protocol === 'https:' ? https : http;

  proto.get(targetUrl, { headers: { 'User-Agent': 'Mozilla/5.0' } }, (proxyRes) => {
    if (proxyRes.statusCode >= 300 && proxyRes.statusCode < 400 && proxyRes.headers.location) {
      // Follow redirect
      return proxyAutodesk(proxyRes.headers.location, res);
    }

    if (proxyRes.statusCode !== 200) {
      res.writeHead(proxyRes.statusCode);
      return res.end(`Proxy error: HTTP ${proxyRes.statusCode}`);
    }

    let body = '';
    proxyRes.on('data', chunk => body += chunk);
    proxyRes.on('end', () => {
      // Remove frameset redirect JavaScript
      body = body.replace(
        /<script[\s\S]*?location\s*=\s*['"][^'"]*?index\.html[^'"]*?['"][\s\S]*?<\/script>/gi,
        '<!-- frameset redirect removed -->'
      );
      body = body.replace(
        /<script[\s\S]*?window\.top\.location[\s\S]*?<\/script>/gi,
        '<!-- frameset redirect removed -->'
      );
      body = body.replace(
        /<script[\s\S]*?top\.location[\s\S]*?<\/script>/gi,
        '<!-- frameset redirect removed -->'
      );
      body = body.replace(
        /<script[\s\S]*?window\.location\.replace[\s\S]*?<\/script>/gi,
        '<!-- frameset redirect removed -->'
      );

      // Inject base so relative resources load correctly
      body = body.replace('<head>', `<head><base href="${targetUrl}">`);

      res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
      res.end(body);
    });
  }).on('error', (err) => {
    res.writeHead(502);
    res.end(`Proxy error: ${err.message}`);
  });
}
