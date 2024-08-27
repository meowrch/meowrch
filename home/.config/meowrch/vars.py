from pathlib import Path
from typing import Optional
from os.path import expandvars

HOME = Path.home()
MEOWRCH_DIR = Path(__file__).resolve().parent
MEOWRCH_THEMES: Path = MEOWRCH_DIR / "themes"
OOMOX_TEMPLATES = MEOWRCH_DIR / "oomox_templates"
BASE_CONFIGS: Path = MEOWRCH_DIR / "base_configs" 
MEOWRCH_ASSETS: Path = MEOWRCH_DIR / "utils" / "assets"

MEOWRCH_CONFIG: Path = MEOWRCH_DIR / "config.yaml"
WALLPAPER_SYMLINC: Path = MEOWRCH_DIR / "current_wallpaper"

ROFI_SELECTING_THEME: Path = Path.home() / ".config" / "rofi" / "selecting.rasi"

WALLPAPERS_CACHE_DIR: Path = HOME / ".cache" / "meowrch" / "wallpaper_thumbnails"
THEMES_CACHE_DIR: Path = HOME / ".cache" / "meowrch" / "themes_thumbnails"

OOMOX_COLORS: Path = lambda theme_name: MEOWRCH_THEMES / theme_name / "oomox-colors"  # noqa: E731

THEME_GEN_SCRIPT: Path = Path("/opt/oomox/plugins/base16/cli.py")

SESSION_TYPE: Optional[str] = (lambda s: s if s != "$XDG_SESSION_TYPE" else None)(expandvars("$XDG_SESSION_TYPE"))

GTK2_CFG: Path = HOME / ".config" / "gtk-2.0" / "gtkrc"
GTK3_CFG: Path = HOME / ".config" / "gtk-3.0" / "settings.ini"
GTK4_CFG: Path = HOME / ".config" / "gtk-4.0" / "settings.ini"