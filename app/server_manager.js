const fs = require('fs');
const path = require('path');
const http = require('http');
const { spawn } = require('child_process');

let pythonProcess = null;

function startServer(appRoot, port = 5055) {
  const binServerExe = path.join(appRoot, 'bin', 'server.exe');
  const rootServerExe = path.join(appRoot, 'server.exe');

  let serverExe = null;
  if (fs.existsSync(binServerExe)) {
    serverExe = binServerExe;
  } else if (fs.existsSync(rootServerExe)) {
    serverExe = rootServerExe;
  }

  if (serverExe) {
    console.log('[ServerManager] Launching compiled backend engine:', serverExe);
    pythonProcess = spawn(serverExe, ['--port', String(port)], {
      cwd: appRoot,
      windowsHide: true,
      stdio: ['ignore', 'pipe', 'pipe']
    });
  } else {
    console.log('[ServerManager] Launching python server.py from root:', appRoot);
    pythonProcess = spawn('python', ['server.py', '--port', String(port)], {
      cwd: appRoot,
      windowsHide: true,
      stdio: ['ignore', 'pipe', 'pipe']
    });
  }

  pythonProcess.stdout.on('data', (data) => {
    console.log(`[Server] ${data.toString().trim()}`);
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`[Server Error] ${data.toString().trim()}`);
  });

  pythonProcess.on('exit', (code) => {
    console.log(`[ServerManager] Backend engine stopped (code: ${code})`);
  });

  return pythonProcess;
}

function waitForServer(serverUrl, callback, maxAttempts = 40) {
  if (maxAttempts <= 0) {
    console.error('[ServerManager] Backend engine timed out starting.');
    return callback(false);
  }

  http.get(serverUrl, (res) => {
    if (res.statusCode >= 200 && res.statusCode < 400) {
      console.log('[ServerManager] Backend engine is ready and responsive!');
      callback(true);
    } else {
      setTimeout(() => waitForServer(serverUrl, callback, maxAttempts - 1), 300);
    }
  }).on('error', () => {
    setTimeout(() => waitForServer(serverUrl, callback, maxAttempts - 1), 300);
  });
}

function stopServer() {
  if (pythonProcess) {
    console.log('[ServerManager] Terminating backend process...');
    try {
      if (process.platform === 'win32') {
        spawn('taskkill', ['/pid', String(pythonProcess.pid), '/f', '/t']);
      } else {
        pythonProcess.kill();
      }
    } catch (e) {
      console.error('[ServerManager] Error killing process:', e);
    }
    pythonProcess = null;
  }
}

module.exports = {
  startServer,
  waitForServer,
  stopServer
};
