const { Menu, shell } = require('electron');
const path = require('path');
const { setGameFramerate } = require('./patcher');

function buildApplicationMenu(mainWindow, app, appRoot, serverUrl) {
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
          label: '🔍 Zoom In',
          accelerator: 'Equal',
          click: () => mainWindow.webContents.executeJavaScript("var s = document.getElementById('swf'); if (s && typeof s.zoomMap === 'function') s.zoomMap(1);")
        },
        {
          label: '🔍 Zoom Out',
          accelerator: 'Minus',
          click: () => mainWindow.webContents.executeJavaScript("var s = document.getElementById('swf'); if (s && typeof s.zoomMap === 'function') s.zoomMap(-1);")
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
          click: () => mainWindow.loadURL(serverUrl)
        },
        {
          label: 'Create New Empire',
          accelerator: 'Ctrl+N',
          click: () => mainWindow.loadURL(serverUrl + 'new.html')
        }
      ]
    },
    {
      label: '⚡ Performance',
      submenu: [
        {
          label: '🚀 60 FPS (Ultra Smooth - Recommended)',
          click: () => {
            setGameFramerate(appRoot, 60);
            mainWindow.webContents.reloadIgnoringCache();
          }
        },
        {
          label: '⚡ 120 FPS (Extreme Framerate)',
          click: () => {
            setGameFramerate(appRoot, 120);
            mainWindow.webContents.reloadIgnoringCache();
          }
        },
        {
          label: '⏳ 30 FPS (Classic Retro)',
          click: () => {
            setGameFramerate(appRoot, 30);
            mainWindow.webContents.reloadIgnoringCache();
          }
        },
        { type: 'separator' },
        {
          label: '✨ Graphics: Medium (Smooth 60 FPS - Recommended)',
          click: () => {
            if (mainWindow) {
              mainWindow.webContents.executeJavaScript("if (window.setFlashQuality) window.setFlashQuality('medium');");
            }
          }
        },
        {
          label: '🎨 Graphics: High (Full Anti-Aliasing)',
          click: () => {
            if (mainWindow) {
              mainWindow.webContents.executeJavaScript("if (window.setFlashQuality) window.setFlashQuality('high');");
            }
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
            shell.openPath(path.join(appRoot, 'saves'));
          }
        },
        {
          label: 'Open Config Folder',
          click: async () => {
            shell.openPath(path.join(appRoot, 'config'));
          }
        },
        {
          label: 'Edit Unit Stats (unit_patch.json)',
          click: async () => {
            shell.openPath(path.join(appRoot, 'config', 'patch', 'unit_patch.json'));
          }
        }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(menuTemplate);
  Menu.setApplicationMenu(menu);
}

module.exports = {
  buildApplicationMenu
};
