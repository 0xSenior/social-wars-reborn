const { app, BrowserWindow } = require('electron');
const path = require('path');
const fs = require('fs');

const {
  getAppRoot,
  applyChromiumSwitches,
  SERVER_PORT,
  SERVER_URL
} = require('./config');
const { buildApplicationMenu } = require('./menu');
const { startServer, waitForServer, stopServer } = require('./server_manager');

// Initialize Chromium hardware acceleration & Flash switches
applyChromiumSwitches(app);

let mainWindow = null;
const appRoot = getAppRoot(app);

function createMainWindow() {
  let appIcon = path.join(appRoot, 'icon.ico');
  if (!fs.existsSync(appIcon)) {
    appIcon = path.join(appRoot, 'templates', 'img', 'icon.png');
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

  // Attach clean application menu
  buildApplicationMenu(mainWindow, app, appRoot, SERVER_URL);

  // Full-screen desktop immersion
  mainWindow.maximize();

  // Polished game loading screen
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

  waitForServer(SERVER_URL, (ready) => {
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

// Application Lifecycle
app.whenReady().then(() => {
  startServer(appRoot, SERVER_PORT);
  createMainWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createMainWindow();
  });
});

app.on('will-quit', stopServer);
app.on('window-all-closed', () => {
  stopServer();
  if (process.platform !== 'darwin') app.quit();
});
