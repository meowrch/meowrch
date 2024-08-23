import yaml
import logging
import traceback
import subprocess
from pathlib import Path
from os.path import expandvars
from typing import List, Union, Optional

from .other import parse_wallpapers
from .schemes import Theme
from .exceptions import InvalidSession, NoConfigFile
from vars import (
	SESSION_TYPE, MEOWRCH_DIR, MEOWRCH_CONFIG,
	WALLPAPER_SYMLINC, MEOWRCH_ASSETS
)


class Config:
	__slots__ = ()
	symlink_wallpapers = Path.home() / ".config" / "meowrch" / "current_wallpaper"

	@classmethod
	def __load_yaml(cls) -> dict:
		"""
		Loads data from a YML file and returns it as a dictionary.
		
		Returns:
			dict: Data from a YML file in the form of a dictionary.
		"""
		if not MEOWRCH_CONFIG.exists():
			raise NoConfigFile()

		with open(MEOWRCH_CONFIG, 'r') as f:
			data = yaml.load(f, Loader=yaml.FullLoader)

		return data
	
	@classmethod
	def __dump_yaml(cls, data: dict) -> None:
		"""
		Saves the data to a YAML file.
		
		Args:
			data (dict): The data to be saved in a YAML file.
		"""

		if not MEOWRCH_CONFIG.exists():
			raise NoConfigFile()
			
		with open(MEOWRCH_CONFIG, 'w') as f:
			yaml.dump(data, f)

	@classmethod
	def get_current_wallpaper(cls) -> Optional[str]:
		data = Config.__load_yaml()

		if SESSION_TYPE == "x11":
			wallpaper = data.get('current-xwallpaper', None)
		elif SESSION_TYPE == "wayland":
			wallpaper = data.get('current-wwallpaper', None)
		else:
			raise InvalidSession(session=SESSION_TYPE)

		if wallpaper is not None and isinstance(wallpaper, str):
			wallpaper = str(Path(expandvars(wallpaper.strip())).expanduser())

		return wallpaper

	@classmethod
	def get_current_xtheme(cls) -> Optional[str]:
		data = Config.__load_yaml()
		theme = data.get('current-xtheme', None)
		return theme

	@classmethod
	def get_current_wtheme(cls) -> Optional[str]:
		data = Config.__load_yaml()
		theme = data.get('current-wtheme', None)
		return theme

	@staticmethod
	def _validate_theme(theme_name: str, wallpapers: List[str]) -> Optional[Theme]:
		"""
		Проверяет, правильно ли укомплектована тема. 
		Если да, то возвращает Theme
		В противном случае возвращает None

		Args:
			theme_name: str - Название темы, которую нужно проверить.
			wallpapers: List[str] - Список путей до обоев
		"""
		path_to_theme: Path = MEOWRCH_DIR / "themes" / theme_name
		icon = MEOWRCH_ASSETS / "default-theme-icon.png"

		##==> Проверка наличия обоев
		###########################################
		wallpapers = [wp for wp in wallpapers if Path(wp).exists()]
		if len(wallpapers) == 0:
			logging.error(f"No available wallpapers for theme {theme_name}")
			return

		##==> Проверка наличия иконки
		###########################################
		path_to_theme_icon: Path = path_to_theme/f"{theme_name}.png"
		if path_to_theme_icon.exists():
			icon = path_to_theme_icon	

		return Theme(
			name=theme_name,
			available_wallpapers=wallpapers,
			icon=icon
		)

	@classmethod
	def get_all_themes(cls) -> List[Theme]:
		themes = []
		data = Config.__load_yaml()
		custom_wallpapers = data.get('custom-wallpapers', [])

		if custom_wallpapers is None:
			custom_wallpapers = []
			
		custom_wallpapers = parse_wallpapers(custom_wallpapers)

		if 'themes' not in data or data["themes"] is None or len(data['themes']) < 1:
			return []

		for theme_name, params in data['themes'].items():
			if params is None:
				continue
			
			wallpapers = []
			available_wallpapers = params.get('available_wallpapers', [])

			if available_wallpapers is None:
				continue 

			available_wallpapers = parse_wallpapers(available_wallpapers)
			wallpapers.extend(custom_wallpapers)
			wallpapers.extend(available_wallpapers)

			theme: Optional[Theme] = cls._validate_theme(theme_name=theme_name, wallpapers=wallpapers)

			if theme is not None:
				themes.append(theme)

		return themes

	@classmethod
	def _set_theme(cls, theme_name: str) -> None:
		"""
		We strongly recommend installing the theme using theming.ThemeManager.set_theme
		"""
		data = Config.__load_yaml()

		if SESSION_TYPE == "x11":
			data['current-xtheme'] = theme_name
		elif SESSION_TYPE == "wayland":
			data['current-wtheme'] = theme_name
		else:
			raise InvalidSession(session=SESSION_TYPE)
		
		Config.__dump_yaml(data)

	@classmethod
	def _set_wallpaper(cls, wallpaper_path: Union[str, Path]) -> None:
		"""
		We strongly recommend installing the wallpaper using theming.ThemeManager.set_wallpaper
		"""
		data = Config.__load_yaml()

		if SESSION_TYPE == "x11":
			data['current-xwallpaper'] = str(wallpaper_path)
		elif SESSION_TYPE == "wayland":
			data['current-wwallpaper'] = str(wallpaper_path)
		else:
			raise InvalidSession(session=SESSION_TYPE)

		try:
			subprocess.run(["ln", "-sf", str(wallpaper_path), str(WALLPAPER_SYMLINC)], check=True)
			logging.debug(f"Symlink for wallpaper created: {WALLPAPER_SYMLINC} -> {wallpaper_path}")
		except Exception:
			logging.error(f"Failed to create symlink for wallpaper \"{wallpaper_path}\": {traceback.format_exc()}")

		Config.__dump_yaml(data)
		