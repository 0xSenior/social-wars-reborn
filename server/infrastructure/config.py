import os
import sys
from dataclasses import dataclass
from typing import Optional


def resolve_base_dir() -> str:
    """
    Resolves the base root directory whether running from source or
    bundled inside PyInstaller (in bin/ or root).
    """
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(os.path.abspath(sys.executable))
        if os.path.basename(exe_dir).lower() == 'bin':
            return os.path.dirname(exe_dir)
        return exe_dir
    # When running from source, base dir is the repository root
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up two levels: server/infrastructure -> repo root
    return os.path.abspath(os.path.join(current_dir, "..", ".."))


BASE_DIR = resolve_base_dir()

ASSETS_DIR = os.path.join(BASE_DIR, "assets")
STUB_DIR = os.path.join(BASE_DIR, "stub")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
VILLAGES_DIR = os.path.join(BASE_DIR, "villages")
QUESTS_DIR = os.path.join(VILLAGES_DIR, "quest")
CONFIG_DIR = os.path.join(BASE_DIR, "config")
CONFIG_PATCH_DIR = os.path.join(CONFIG_DIR, "patch")
MODS_DIR = os.path.join(BASE_DIR, "mods")
SAVES_DIR = os.path.join(BASE_DIR, "saves")


@dataclass
class ServerConfig:
    host: str = "127.0.0.1"
    port: int = 5055
    public_url: Optional[str] = None
    debug: bool = False
    secret_key: Optional[bytes] = None

    @property
    def resolved_public_url(self) -> str:
        if self.public_url:
            return self.public_url.rstrip("/")
        return f"http://{self.host}:{self.port}"
