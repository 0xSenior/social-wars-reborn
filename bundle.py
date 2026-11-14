import sys
import os

# Base directory for executable or script
if getattr(sys, 'frozen', None):
    exe_dir = os.path.dirname(os.path.abspath(sys.executable))
    # If placed in bin/, root is parent folder
    if os.path.basename(exe_dir).lower() == 'bin':
        BASE_DIR = os.path.dirname(exe_dir)
    else:
        BASE_DIR = exe_dir
else:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

ASSETS_DIR = os.path.join(BASE_DIR, "assets")
STUB_DIR = os.path.join(BASE_DIR, "stub")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
VILLAGES_DIR = os.path.join(BASE_DIR, "villages")
QUESTS_DIR = os.path.join(VILLAGES_DIR, "quest")
CONFIG_DIR = os.path.join(BASE_DIR, "config")
CONFIG_PATCH_DIR = os.path.join(CONFIG_DIR, "patch")

MODS_DIR = os.path.join(BASE_DIR, "mods")
SAVES_DIR = os.path.join(BASE_DIR, "saves")
AUCTIONS_DIR = os.path.join(BASE_DIR, "auctions")
