const { app, BrowserWindow, Menu, globalShortcut } = require('electron');
const path = require('path');
const fs = require('fs');
const zlib = require('zlib');
const { spawn } = require('child_process');
const http = require('http');

function getAppRoot() {
  const exeDir = path.dirname(app.getPath('exe'));
  if (fs.existsSync(path.join(exeDir, 'assets')) && (fs.existsSync(path.join(exeDir, 'templates')) || fs.existsSync(path.join(exeDir, 'bin')))) {
    return exeDir;
  }
  let cur = __dirname;
  while (cur && cur !== path.dirname(cur)) {
    if (fs.existsSync(path.join(cur, 'assets')) && (fs.existsSync(path.join(cur, 'templates')) || fs.existsSync(path.join(cur, 'bin')))) {
      return cur;
    }
    cur = path.dirname(cur);
  }
  return path.join(__dirname, '..', '..', '..');
}

// Locate flash plugin (works in dev and in packaged release)
const appRoot = getAppRoot();
let flashPluginPath = path.join(appRoot, 'plugins', 'pepflashplayer64.dll');
if (!fs.existsSync(flashPluginPath)) {
  flashPluginPath = path.join(__dirname, '..', 'plugins', 'pepflashplayer64.dll');
}

console.log('[Launcher] Flash plugin path:', flashPluginPath, 'Found:', fs.existsSync(flashPluginPath));

// Flash plugin registration
app.commandLine.appendSwitch('ppapi-flash-path', flashPluginPath);
app.commandLine.appendSwitch('ppapi-flash-version', '34.0.0.376');
app.commandLine.appendSwitch('no-sandbox');

// Extreme Performance, Low Latency & High FPS Switches
app.commandLine.appendSwitch('ignore-gpu-blocklist');
app.commandLine.appendSwitch('enable-gpu-rasterization');
app.commandLine.appendSwitch('enable-zero-copy');
app.commandLine.appendSwitch('enable-native-gpu-memory-buffers');
app.commandLine.appendSwitch('disable-frame-rate-limit');
app.commandLine.appendSwitch('disable-gpu-vsync');
app.commandLine.appendSwitch('max-gum-fps', '120');
app.commandLine.appendSwitch('disable-renderer-backgrounding');
app.commandLine.appendSwitch('disable-background-timer-throttling');
app.commandLine.appendSwitch('disable-backgrounding-occluded-windows');
app.commandLine.appendSwitch('enable-accelerated-2d-canvas');
app.commandLine.appendSwitch('enable-accelerated-video-decode');
app.commandLine.appendSwitch('high-dpi-support', '1');

// Dynamic Flash SWF framerate patcher
function patchSwfFps(filePath, targetFps) {
  try {
    if (!fs.existsSync(filePath)) {
      console.warn(`[Launcher] File does not exist for patching: ${filePath}`);
      return false;
    }
    const buf = fs.readFileSync(filePath);
    const sig = buf.toString('latin1', 0, 3);
    if (sig !== 'CWS') return false;
    const version = buf[3];
    const origLen = buf.slice(4, 8);
    const decomp = zlib.inflateSync(buf.slice(8));
    
    const nbits = decomp[0] >> 3;
    const totalBytes = Math.floor((5 + 4 * nbits + 7) / 8);
    
    const fpsInt = Math.floor(targetFps);
    const fpsFrac = Math.floor((targetFps - fpsInt) * 256);
    decomp[totalBytes] = fpsFrac;
    decomp[totalBytes + 1] = fpsInt;
    
    // Update Flex/Flash metadata tag if present
    const re = Buffer.from('\tframeRate\x02');
    const idx = decomp.indexOf(re);
    if (idx !== -1) {
      const fpsStr = String(fpsInt).padStart(2, '0');
      decomp[idx + re.length] = fpsStr.charCodeAt(0);
      decomp[idx + re.length + 1] = fpsStr.charCodeAt(1);
    }
    
    // Ensure built-in Stats widget is visible
    const pattern = Buffer.from('d066ed1c246461d507d066ed1c', 'hex');
    const pIdx = decomp.indexOf(pattern);
    if (pIdx !== -1) {
      const targetIdx = pIdx + pattern.length;
      if (decomp[targetIdx] === 0x27) {
        decomp[targetIdx] = 0x26; // pushtrue
      }
    }
    
    const recompressed = zlib.deflateSync(decomp);
    const outBuf = Buffer.concat([
      Buffer.from('CWS'),
      Buffer.from([version]),
      origLen,
      recompressed
    ]);
    fs.writeFileSync(filePath, outBuf);
    console.log(`[Launcher] Patched ${path.basename(filePath)} to ${targetFps} FPS`);
    return true;
  } catch (err) {
    console.error(`[Launcher] Error patching FPS for ${filePath}:`, err);
    return false;
  }
}

function setGameFramerate(targetFps) {
  const root = getAppRoot();
  console.log(`[Launcher] Setting FPS to ${targetFps} in root: ${root}`);
  const files = [
    path.join(root, 'assets', 'flash', 'SWLoader.swf'),
    path.join(root, 'assets', 'flash', 'Basesec_1.5.4.swf')
  ];
  for (const f of files) {
    patchSwfFps(f, targetFps);
  }
}

let mainWindow = null;
let pythonProcess = null;
const SERVER_PORT = 5055;
const SERVER_URL = `http://127.0.0.1:${SERVER_PORT}/`;

function startPythonServer() {
  const rootDir = getAppRoot();
  const binServerExe = path.join(rootDir, 'bin', 'server.exe');
  const rootServerExe = path.join(rootDir, 'server.exe');

  let serverExe = null;
  if (fs.existsSync(binServerExe)) {
    serverExe = binServerExe;
  } else if (fs.existsSync(rootServerExe)) {
    serverExe = rootServerExe;
  }

  if (serverExe) {
    console.log('[Launcher] Starting compiled backend engine from', serverExe);
    pythonProcess = spawn(serverExe, ['--port', String(SERVER_PORT)], {
      cwd: rootDir,
      windowsHide: true,
      stdio: ['ignore', 'pipe', 'pipe']
    });
  } else {
    console.log('[Launcher] Starting python server.py from', rootDir);
    pythonProcess = spawn('python', ['server.py', '--port', String(SERVER_PORT)], {
      cwd: rootDir,
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
  const root = getAppRoot();
  let appIcon = path.join(root, 'icon.ico');
  if (!fs.existsSync(appIcon)) {
    appIcon = path.join(root, 'templates', 'img', 'icon.png');
  }

  mainWindow = new BrowserWindow({
    width: 1280,
    height: 820,
    minWidth: 1024,
    minHeight: 720,
    title: 'Social Wars: Reborn',
    icon: appIcon,
    backgroundColor: '#1a1f16',
    autoHideMenuBar: false,
    webPreferences: {
      plugins: true,
      nodeIntegration: true,
      contextIsolation: false,
      enableRemoteModule: true
    }
  });

  // Custom Gaming Menu with User Account, Performance, Community, Game, and Developer options
  const { shell } = require('electron');
  const menuTemplate = [
    {
      label: '⚔️ Game',
      submenu: [
        {
          label: 'Restart Game (Bypass Cache)',
          accelerator: 'F5',
          click: () => mainWindow.webContents.reloadIgnoringCache()
        },
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
      label: '👤 Account / Empire',
      submenu: [
        {
          label: 'Log Out / Switch Empire',
          accelerator: 'Ctrl+L',
          click: () => mainWindow.loadURL(SERVER_URL)
        },
        {
          label: 'Create New Empire',
          accelerator: 'Ctrl+N',
          click: () => mainWindow.loadURL(SERVER_URL + 'new.html')
        }
      ]
    },
    {
      label: '⚡ Performance',
      submenu: [
        {
          label: '🚀 60 FPS (Ultra Smooth - Recommended)',
          click: () => {
            setGameFramerate(60);
            mainWindow.webContents.reloadIgnoringCache();
          }
        },
        {
          label: '⚡ 120 FPS (Extreme Framerate)',
          click: () => {
            setGameFramerate(120);
            mainWindow.webContents.reloadIgnoringCache();
          }
        },
        {
          label: '⏳ 30 FPS (Classic Retro)',
          click: () => {
            setGameFramerate(30);
            mainWindow.webContents.reloadIgnoringCache();
          }
        },
        { type: 'separator' },
        {
          label: '📊 Toggle In-Game FPS Counter (Key: /)',
          accelerator: '/',
          click: () => {
            if (mainWindow) {
              mainWindow.webContents.sendInputEvent({ type: 'keyDown', keyCode: '/' });
              mainWindow.webContents.sendInputEvent({ type: 'keyUp', keyCode: '/' });
            }
          }
        }
      ]
    },
    {
      label: '🎁 Extras & Community',
      submenu: [
        {
          label: 'Free Gifts',
          click: () => mainWindow.webContents.executeJavaScript("alert('Free daily bonus received in your empire!');")
        },
        {
          label: 'Join Discord Server',
          click: () => shell.openExternal('https://discord.gg/zW5gSbQJBw')
        },
        {
          label: 'Project GitHub',
          click: () => shell.openExternal('https://github.com/0xSenior/social-wars-reborn')
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
        { type: 'separator' },
        {
          label: 'Open Saves Folder',
          click: async () => {
            shell.openPath(path.join(getAppRoot(), 'saves'));
          }
        },
        {
          label: 'Open Config Folder',
          click: async () => {
            shell.openPath(path.join(getAppRoot(), 'config'));
          }
        },
        {
          label: 'Edit Unit Stats (unit_patch.json)',
          click: async () => {
            shell.openPath(path.join(getAppRoot(), 'config', 'patch', 'unit_patch.json'));
          }
        }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(menuTemplate);
  Menu.setApplicationMenu(menu);

  // Start window maximized for full immersion
  mainWindow.maximize();

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
