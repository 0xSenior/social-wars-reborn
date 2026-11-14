const { app, BrowserWindow, Menu, globalShortcut } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const http = require('http');

// Configure PPAPI Flash Player plugin
const flashPluginPath = path.join(__dirname, '..', 'plugins', 'pepflashplayer64.dll');
app.commandLine.appendSwitch('ppapi-flash-path', flashPluginPath);
app.commandLine.appendSwitch('ppapi-flash-version', '34.0.0.376');
app.commandLine.appendSwitch('no-sandbox');
app.commandLine.appendSwitch('disable-renderer-backgrounding');

let mainWindow = null;
let pythonProcess = null;
const SERVER_PORT = 5055;
const SERVER_URL = `http://127.0.0.1:${SERVER_PORT}/`;

function startPythonServer() {
  console.log('[Launcher] Starting Python backend server...');
  const repoRoot = path.join(__dirname, '..');
  
  pythonProcess = spawn('python', ['server.py', '--port', String(SERVER_PORT)], {
    cwd: repoRoot,
    windowsHide: true,
    stdio: ['ignore', 'pipe', 'pipe']
  });

  pythonProcess.stdout.on('data', (data) => {
    console.log(`[Server] ${data.toString().trim()}`);
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`[Server Error] ${data.toString().trim()}`);
  });

  pythonProcess.on('exit', (code) => {
    console.log(`[Launcher] Python server stopped with code ${code}`);
  });
}

function waitForServer(callback, attempts = 40) {
  if (attempts <= 0) {
    console.error('[Launcher] Server failed to start in time.');
    return callback(false);
  }

  http.get(SERVER_URL, (res) => {
    if (res.statusCode >= 200 && res.statusCode < 400) {
      console.log('[Launcher] Server is online and ready!');
      callback(true);
    } else {
      setTimeout(() => waitForServer(callback, attempts - 1), 300);
    }
  }).on('error', () => {
    setTimeout(() => waitForServer(callback, attempts - 1), 300);
  });
}

function createMainWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 820,
    minWidth: 1024,
    minHeight: 720,
    title: 'Social Wars: Reborn',
    icon: path.join(__dirname, '..', 'templates', 'img', 'icon.png'),
    backgroundColor: '#1a1f16',
    autoHideMenuBar: false,
    webPreferences: {
      plugins: true,
      nodeIntegration: false,
      contextIsolation: true
    }
  });

  // Custom Gaming Menu
  const menuTemplate = [
    {
      label: '⚔️ Game',
      submenu: [
        {
          label: 'Restart Game',
          accelerator: 'F5',
          click: () => mainWindow.reload()
        },
        {
          label: 'Home / Profile Selection',
          click: () => mainWindow.loadURL(SERVER_URL)
        },
        { type: 'separator' },
        {
          label: 'Toggle Fullscreen',
          accelerator: 'F11',
          click: () => mainWindow.setFullScreen(!mainWindow.isFullScreen())
        },
        { type: 'separator' },
        {
          label: 'Exit Game',
          accelerator: 'Alt+F4',
          click: () => app.quit()
        }
      ]
    },
    {
      label: '🛠️ Developer',
      submenu: [
        {
          label: 'Open DevTools',
          accelerator: 'F12',
          click: () => mainWindow.webContents.toggleDevTools()
        },
        {
          label: 'Open Save Folder',
          click: async () => {
            const { shell } = require('electron');
            shell.openPath(path.join(__dirname, '..', 'saves'));
          }
        },
        {
          label: 'Open Config Folder',
          click: async () => {
            const { shell } = require('electron');
            shell.openPath(path.join(__dirname, '..', 'config'));
          }
        }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(menuTemplate);
  Menu.setApplicationMenu(menu);

  // Loading Screen HTML while waiting for server
  const loadingHtml = `
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="utf-8">
        <title>Social Wars: Reborn - Loading</title>
        <style>
          body {
            margin: 0;
            background: #11140e;
            color: #d6e865;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100vh;
            text-align: center;
          }
          h1 { margin-bottom: 8px; font-size: 28px; text-shadow: 0 0 10px rgba(214,232,101,0.5); }
          p { color: #aaa; font-size: 14px; margin-top: 0; }
          .spinner {
            width: 50px;
            height: 50px;
            border: 4px solid #333;
            border-top: 4px solid #d6e865;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 20px;
          }
          @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        </style>
      </head>
      <body>
        <div class="spinner"></div>
        <h1>SOCIAL WARS: REBORN</h1>
        <p>Starting local battle engine and loading resources...</p>
      </body>
    </html>
  `;

  mainWindow.loadURL('data:text/html;charset=utf-8,' + encodeURI(loadingHtml));

  waitForServer((ready) => {
    if (ready && mainWindow) {
      mainWindow.loadURL(SERVER_URL);
    } else if (mainWindow) {
      mainWindow.loadURL('data:text/html;charset=utf-8,<h2>Failed to connect to game server. Please check python environment.</h2>');
    }
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// App lifecycle
app.whenReady().then(() => {
  startPythonServer();
  createMainWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createMainWindow();
  });
});

function cleanup() {
  if (pythonProcess) {
    console.log('[Launcher] Stopping python process...');
    try {
      if (process.platform === 'win32') {
        spawn('taskkill', ['/pid', pythonProcess.pid, '/f', '/t']);
      } else {
        pythonProcess.kill();
      }
    } catch (e) {
      console.error(e);
    }
    pythonProcess = null;
  }
}

app.on('will-quit', cleanup);
app.on('window-all-closed', () => {
  cleanup();
  if (process.platform !== 'darwin') app.quit();
});
