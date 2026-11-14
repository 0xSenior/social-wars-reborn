const path = require('path');
const fs = require('fs');

function getAppRoot(app) {
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
  return path.resolve(__dirname, '..');
}

function getFlashPluginPath(appRoot) {
  let pluginPath = path.join(appRoot, 'plugins', 'pepflashplayer64.dll');
  if (!fs.existsSync(pluginPath)) {
    pluginPath = path.resolve(__dirname, '..', 'plugins', 'pepflashplayer64.dll');
  }
  return pluginPath;
}

function applyChromiumSwitches(app) {
  const appRoot = getAppRoot(app);
  const flashPluginPath = getFlashPluginPath(appRoot);

  console.log('[Launcher] App Root:', appRoot);
  console.log('[Launcher] Flash plugin path:', flashPluginPath, 'Found:', fs.existsSync(flashPluginPath));

  // Pepper Flash Registration
  app.commandLine.appendSwitch('ppapi-flash-path', flashPluginPath);
  app.commandLine.appendSwitch('ppapi-flash-version', '34.0.0.376');
  app.commandLine.appendSwitch('ppapi-flash-args', 'enable_gpu=1,enable_stage3d=1');
  app.commandLine.appendSwitch('no-sandbox');

  // Extreme GPU Acceleration & High FPS Switches
  app.commandLine.appendSwitch('ignore-gpu-blocklist');
  app.commandLine.appendSwitch('enable-pepper-3d');
  app.commandLine.appendSwitch('enable-gpu-rasterization');
  app.commandLine.appendSwitch('force-gpu-rasterization');
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
}

const SERVER_PORT = 5055;
const SERVER_URL = `http://127.0.0.1:${SERVER_PORT}/`;

module.exports = {
  getAppRoot,
  getFlashPluginPath,
  applyChromiumSwitches,
  SERVER_PORT,
  SERVER_URL
};
