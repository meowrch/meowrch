import logging
from typing import List
from logging.handlers import RotatingFileHandler
from pathlib import Path

from utils.schemes import BaseOption
from utils.options import (
	CopyOption, CopyOrGenOption, TmuxCfgOption, GTKOption, FishOption, 
	WaybarCfgOption, KittyOption, DunstOption, CavaOption
)
from vars import HOME, MEOWRCH_DIR, GTK2_CFG, GTK3_CFG, GTK4_CFG	


##==> Настройки применения тем для конфигураций
###################################################
theme_options: List[BaseOption] = [
	##==> Копирование конфигов
	###############################################
	CopyOption(_id="polybar", name="polybar.ini", path_to=HOME / ".config" / "polybar" / "config.ini", wayland_needed=False),
	CopyOption(_id="picom", name="picom.conf", path_to=HOME / ".config" / "bspwm" / "picom.conf", wayland_needed=False),
	CopyOption(_id="tmux_theme", is_dir=True, name="tmux-theme", path_to=HOME / ".config" / "tmux" / "theme"),
	CopyOption(_id="starship", name="starship.toml", path_to=HOME / ".config" / "starship.toml"),
	CopyOption(_id="rofi", name="rofi.rasi", path_to=HOME / ".config" / "rofi" / "theme.rasi"),
	CopyOption(_id="btop", name="btop.theme", path_to=HOME / ".config" / "btop" / "themes" / "meowrch.theme"),
	CopyOption(_id="micro", name="theme.micro", path_to=HOME / ".config" / "micro" / "colorschemes" / "meowrch.micro"),
	CopyOption(_id="hyprland", name="hyprland-custom-prefs.conf", path_to=HOME / ".config" / "hypr" / "custom-prefs.conf", xorg_needed=False),
	CopyOption(_id="waybar_css", name="waybar.css", path_to=HOME / ".config" / "waybar" / "style.css", xorg_needed=False),


	##==> Копирование / Генерация конфигов
	###############################################
	CopyOrGenOption(
		_id="alacritty",
		name="alacritty.toml",
		path_to=HOME / ".config" / "alacritty" / "themes" / "meowrch.toml",
		template_name="alacritty.mustache"
	),
	CopyOrGenOption(
		_id="qt5ct",
		name="qt5ct-colors.conf",
		path_to=HOME / ".config" / "qt5ct" / "colors" / "meowrch.conf",
		template_name="qt5ct-colors.mustache"
	),
	CopyOrGenOption(
		_id="qt6ct",
		name="qt6ct-colors.conf",
		path_to=HOME / ".config" / "qt6ct" / "colors" / "meowrch.conf",
		template_name="qt6ct-colors.mustache"
	),

	##==> Кастомные действия 
	###############################################
	DunstOption(
		_id="dunst", 
		name="dunstrc", 
		path_to=HOME / ".config" / "dunst" / "dunstrc",
		apply_theme=True
	),
	CavaOption(
		_id="cava", 
		name="cava", 
		path_to=HOME / ".config" / "cava" / "config",
		apply_theme=True
	),
	FishOption(
		_id="fish", 
		name="fish-theme.theme", 
		path_to=HOME / ".config" / "fish" / "themes" / "meowrch.theme",
		apply_theme=True
	),
	KittyOption(
		_id="kitty",
		name="kitty.conf",
		path_to=HOME / ".config" / "kitty" / "themes" / "meowrch.conf",
		template_name="kitty.mustache",
		apply_theme=True
	),
	WaybarCfgOption(
		_id="waybar_cfg", 
		name="waybar.jsonc", 
		path_to=HOME / ".config" / "waybar" / "config.jsonc",
		reload=True
	),
	TmuxCfgOption(
		_id="tmux_config",
		name="tmux-custom-prefs.conf", 
		path_to=HOME / ".config" / "tmux" / "tmux.conf",
		base_config_name="tmux.conf"
	),
	GTKOption(
		_id="gtk_theme",
		gtk4_template_name="gtk4-oodwaita.mustache",
		gtk2_cfg=GTK2_CFG,
		gtk3_cfg=GTK3_CFG,
		gtk4_cfg=GTK4_CFG
	)
]

for vscode in [".vscode", ".vscode-oss"]:
	if Path(HOME / vscode).exists():
		theme_options.append(
			CopyOrGenOption(
				_id="vscode",
				name="vscode.json",
				path_to=HOME / vscode / "extensions" / "dimflix-official.meowrch-theme-1.0.0" / "themes" / "meowrch-theme.json",
				template_name="vscode.mustache"
			)
		)

##==> Логирование
###############################################
log_file = MEOWRCH_DIR / "logs.log"

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s',
    level=logging.DEBUG,
	handlers=[
		RotatingFileHandler(
			filename=log_file,
			mode='a',
			maxBytes=5 * 1024 * 1024,
			backupCount=1
		), # Настройка логирования с ротацией по размеру
        logging.StreamHandler()
	],
)

with open(log_file, 'a') as f:
    f.write('\n')
