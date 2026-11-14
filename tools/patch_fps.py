#!/usr/bin/env python3
import sys
import os
import struct
import zlib

def patch_swf(path, target_fps):
    if not os.path.exists(path):
        print(f"[!] File not found: {path}")
        return False
        
    with open(path, 'rb') as f:
        data = f.read()
        
    sig = data[:3].decode('latin1', errors='ignore')
    if sig != 'CWS':
        print(f"[!] Only CWS compressed SWF supported: {path} (got {sig})")
        return False
        
    version = data[3]
    orig_len = data[4:8]
    decomp = bytearray(zlib.decompress(data[8:]))
    
    # Calculate FrameSize RECT size
    first_byte = decomp[0]
    nbits = first_byte >> 3
    total_bits = 5 + 4 * nbits
    total_bytes = (total_bits + 7) // 8
    
    # Read old FPS
    old_fps = decomp[total_bytes + 1] + decomp[total_bytes] / 256.0
    
    # Set new FPS
    fps_int = int(target_fps)
    fps_frac = int((target_fps - fps_int) * 256)
    decomp[total_bytes] = fps_frac
    decomp[total_bytes + 1] = fps_int
    
    # Update Flex/Flash metadata tag if present
    meta_tag = b'\tframeRate\x02'
    idx = decomp.find(meta_tag)
    if idx != -1:
        fps_str = f"{fps_int:02d}".encode()
        decomp[idx + len(meta_tag):idx + len(meta_tag) + 2] = fps_str
        
    recompressed = zlib.compress(decomp)
    out_data = b'CWS' + bytes([version]) + orig_len + recompressed
    
    with open(path, 'wb') as f:
        f.write(out_data)
        
    print(f"[+] Patched {os.path.basename(path)}: {old_fps} FPS -> {target_fps} FPS")
    return True

def main():
    target_fps = 60.0
    if len(sys.argv) > 1:
        try:
            target_fps = float(sys.argv[1])
        except ValueError:
            print(f"Usage: {sys.argv[0]} [target_fps (e.g. 60, 120, 30)]")
            sys.exit(1)
            
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_files = [
        os.path.join(base_dir, "assets", "flash", "SWLoader.swf"),
        os.path.join(base_dir, "assets", "flash", "Basesec_1.5.4.swf"),
        os.path.join(base_dir, "release", "Social Wars Reborn", "assets", "flash", "SWLoader.swf"),
        os.path.join(base_dir, "release", "Social Wars Reborn", "assets", "flash", "Basesec_1.5.4.swf")
    ]
    
    print(f"[*] Setting Social Wars framerate to {target_fps} FPS...")
    for f in target_files:
        if os.path.exists(f):
            patch_swf(f, target_fps)

if __name__ == "__main__":
    main()
