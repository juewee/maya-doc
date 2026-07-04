const http = require('http');
const WebSocket = require('ws');
const net = require('net');

const MAYA_HOST = '127.0.0.1';
const MAYA_PORT = 6000;
const WS_PORT = 8080;

const server = http.createServer((req, res) => {
  if (req.url === '/') {
    res.writeHead(200, { 'Content-Type': 'text/html' });
    const fs = require('fs');
    fs.readFile(__dirname + '/maya-control.html', (err, data) => {
      if (err) {
        res.writeHead(500);
        res.end('Error loading HTML');
      } else {
        res.end(data);
      }
    });
  } else {
    res.writeHead(404);
    res.end();
  }
});

const wss = new WebSocket.Server({ server });

let mayaSocket = null;
let isMayaConnected = false;
let reconnectTimer = null;
let pendingCommands = [];

function connectToMaya() {
  if (mayaSocket) {
    mayaSocket.destroy();
    mayaSocket = null;
  }

  mayaSocket = new net.Socket();
  mayaSocket.setTimeout(5000);

  mayaSocket.connect(MAYA_PORT, MAYA_HOST, () => {
    isMayaConnected = true;
    console.log('[Maya] Connected to port', MAYA_PORT);
    while (pendingCommands.length > 0) {
      const cmd = pendingCommands.shift();
      mayaSocket.write(cmd.command + '\n');
      if (cmd.resolve) cmd.resolve('');
    }
  });

  mayaSocket.on('data', () => {});

  mayaSocket.on('close', () => {
    isMayaConnected = false;
    console.log('[Maya] Disconnected');
    scheduleReconnect();
  });

  mayaSocket.on('timeout', () => {
    isMayaConnected = false;
    mayaSocket.destroy();
    console.log('[Maya] Connection timeout');
    scheduleReconnect();
  });

  mayaSocket.on('error', (err) => {
    isMayaConnected = false;
    console.log('[Maya] Error:', err.message);
    scheduleReconnect();
  });
}

function scheduleReconnect() {
  if (reconnectTimer) clearTimeout(reconnectTimer);
  reconnectTimer = setTimeout(() => {
    console.log('[Maya] Reconnecting...');
    connectToMaya();
  }, 2000);
}

function sendToMaya(command) {
  return new Promise((resolve, reject) => {
    if (!isMayaConnected || !mayaSocket) {
      pendingCommands.push({ command, resolve, reject });
      return;
    }

    try {
      mayaSocket.write(command + '\n');
      resolve('');
    } catch (err) {
      reject(err);
    }
  });
}

connectToMaya();

wss.on('connection', (ws) => {
  console.log('[WS] Browser connected');

  ws.send(JSON.stringify({ type: 'status', connected: isMayaConnected }));

  ws.on('message', async (message) => {
    try {
      const data = JSON.parse(message.toString());
      if (data.type === 'command') {
        console.log(`[CMD] ${data.command}`);
        await sendToMaya(data.command);
        ws.send(JSON.stringify({ type: 'result', result: '' }));
      } else if (data.type === 'query') {
        console.log(`[QRY] ${data.command}`);
        const result = await sendToMaya(data.command);
        ws.send(JSON.stringify({ type: 'result', result }));
      }
    } catch (err) {
      console.error('[ERR]', err.message);
      ws.send(JSON.stringify({ type: 'error', error: err.message }));
    }
  });

  ws.on('close', () => {
    console.log('[WS] Browser disconnected');
  });
});

server.listen(WS_PORT, () => {
  console.log(`\n=== Maya WebSocket Proxy ===`);
  console.log(`WebSocket server running on ws://localhost:${WS_PORT}`);
  console.log(`HTTP server serving HTML at http://localhost:${WS_PORT}`);
  console.log(`Forwarding commands to Maya at ${MAYA_HOST}:${MAYA_PORT}`);
  console.log(`\nMake sure Maya has commandPort open:`);
  console.log(`  cmds.commandPort(name=":6000", sourceType="python")`);
});