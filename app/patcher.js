const fs = require('fs');
const path = require('path');
const zlib = require('zlib');

function patchSwfFps(filePath, targetFps) {
  try {
    if (!fs.existsSync(filePath)) {
      console.warn(`[Patcher] File does not exist for patching: ${filePath}`);
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
    console.log(`[Patcher] Successfully patched ${path.basename(filePath)} to ${targetFps} FPS`);
    return true;
  } catch (err) {
    console.error(`[Patcher] Error patching FPS for ${filePath}:`, err);
    return false;
  }
}

function setGameFramerate(appRoot, targetFps) {
  console.log(`[Patcher] Applying FPS ${targetFps} across SWF binaries in: ${appRoot}`);
  const files = [
    path.join(appRoot, 'assets', 'flash', 'SWLoader.swf'),
    path.join(appRoot, 'assets', 'flash', 'Basesec_1.5.4.swf')
  ];
  for (const f of files) {
    patchSwfFps(f, targetFps);
  }
}

module.exports = {
  patchSwfFps,
  setGameFramerate
};
