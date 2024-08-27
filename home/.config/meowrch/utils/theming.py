import json
import random
import logging
import traceback
import subprocess
from pathlib import Path
from typing import Dict, Optional, Union

from .config import Config
from .other import notify
from .selecting import Selector
from .exceptions import InvalidSession, NoThemesToInstall
from .schemes import Theme
from vars import SESSION_TYPE
from .loader import theme_options


class ThemeManager:
	__slots__ = ('themes', 'current_theme')
	themes: Dict[str, Theme]
	current_theme: Theme

	def __init__(self) -> None:
		self.themes: Dict[str, Theme] = {theme.name: theme for theme in Config.get_all_themes()}

		if len(self.themes) < 1:
			raise NoThemesToInstall()

		if SESSION_TYPE == "x11":
			cur_theme = Config.get_current_xtheme()
		elif SESSION_TYPE == "wayland":
			cur_theme = Config.get_current_wtheme()
		else:
			raise InvalidSession(session=SESSION_TYPE)

		if cur_theme in self.themes:
			self.current_theme = self.themes[cur_theme]
			wallpaper = Config.get_current_wallpaper()
			if wallpaper is None or not Path(wallpaper).exists():
				logging.warning(f"Theme \"{cur_theme}\" does not support the wallpaper set. We set random wallpapers.")
				self.set_random_wallpaper()
		else:
			logging.warning(f"The installed theme \"{cur_theme}\" is not in the list of themes in the config")
			self.set_random_theme()


	def set_theme(self, theme: Union[str, Theme]) -> None:
		##==> Проверка входящих данных
		##########################################
		if isinstance(theme, str):
			logging.debug(f"The process of installing the \"{theme}\" theme has begun")
			obj: Optional[Theme] = self.themes.get(theme, None)

			if obj is None:
				logging.error(f"[X] Theme named \"{theme.name}\" not found")
				return

			theme = obj

		elif isinstance(theme, Theme):
			logging.debug(f"The process of installing the \"{theme.name}\" theme has begun")
			
		##==> Применение темы
		##########################################
		for option in theme_options:
			try:
				option.apply(theme.name)
			except:
				logging.error(f"[X] Unknown error when applying the \"{option._id}\" config: {traceback.format_exc()}")

		self.current_theme = theme
		Config._set_theme(theme_name=theme.name)

		##==> Устанавливаем подходящие обои
		##########################################
		current_wallpaper = Config.get_current_wallpaper()
		if current_wallpaper is None or not Path(current_wallpaper).exists():
			self.set_random_wallpaper()
		else:
			if current_wallpaper not in [str(i) for i in self.current_theme.available_wallpapers]:
				self.set_random_wallpaper()

		logging.debug(f"The theme has been successfully installed: {theme.name}")

	def set_current_theme(self) -> None:
		logging.debug("The process of setting a current theme has begun")
		self.set_theme(self.current_theme)

	def set_random_theme(self) -> None:
		logging.debug("The process of setting a random theme has begun")
		th = list(self.themes.values())

		if len(th) < 1:
			notify("Critical error!", f"There are no themes available to install for session \"{SESSION_TYPE}\"")
			raise NoThemesToInstall()

		random_theme: Theme = random.choice(list(self.themes.values()))
		self.set_theme(random_theme.name)

	def select_theme(self):
		logging.debug("The process of selecting theme using the rofi menu has begun")

		try:
			theme = Selector.select_theme(list(self.themes.values()))
		except:
			logging.error(f"An error occurred while selecting theme using rofi: {traceback.format_exc()}")
			return

		if theme is not None:
			self.set_theme(theme)

	def set_wallpaper(self, wallpaper: Path) -> None:
		logging.debug(f"The process of setting a wallpaper \"{wallpaper}\" has begun")
		
		if SESSION_TYPE == "wayland":
			transition_fps = 60
			cursor_pos = "0,0"
			
			try:
				output = subprocess.check_output(
					['wlr-randr', '--json'],
					stderr=subprocess.DEVNULL, 
					universal_newlines=True,
				)
				for output_info in json.loads(output):
					for mode in output_info['modes']:
						if mode.get('current'):
							transition_fps = int(round(mode['refresh']))
							break
					else:
						continue
					break
			except Exception:
				logging.warning(f"Couldn't get the screen frequency using wlr-randr: {traceback.format_exc()}")

			try:
				output = subprocess.check_output(
					['hyprctl', 'cursorpos'],
					 universal_newlines=True,
				).strip()

				if output:
					cursor_pos = output
			except Exception:
				logging.warning(f"Couldn't get the cursor position: {traceback.format_exc()}")

			try:
				subprocess.run([
					'swww', 'img', str(wallpaper),
					'--transition-bezier', '.43,1.19,1,.4',
					'--transition-type', 'grow',
					'--transition-duration', '0.4',
					'--transition-fps', str(transition_fps),
					'--invert-y',
					'--transition-pos', cursor_pos
				], check=True)
			except Exception:
				logging.error(f"Unknown error when installing wallpaper (swww): {traceback.format_exc()}")
				return

		elif SESSION_TYPE == "x11":
			try:
				subprocess.run(['feh', '--no-fehbg', '--bg-fill', str(wallpaper)], check=True)
			except Exception:
				logging.error(f"Unknown error when installing wallpaper (feh): {traceback.format_exc()}")
				return
		else:
			logging.error(f"Unsupported XDG_SESSION_TYPE: {SESSION_TYPE}")
			return

		Config._set_wallpaper(wallpaper)
		logging.debug("The process of selecting a wallpaper has finished")

	def set_current_wallpaper(self) -> None:
		logging.debug("The process of setting a current wallpaper has begun")
		wallpaper = Config.get_current_wallpaper()

		if wallpaper is not None and wallpaper in [str(wp) for wp in self.current_theme.available_wallpapers]:
			wallpaper = Path(wallpaper)
			if wallpaper.exists():
				self.set_wallpaper(wallpaper)
				return
				
		self.set_random_wallpaper()
		logging.debug("The process of setting a current wallpaper has finished")

	def set_random_wallpaper(self) -> None:
		wallpaper = random.choice(self.current_theme.available_wallpapers)

		if wallpaper:
			self.set_wallpaper(wallpaper)
			return

		logging.error("There are no wallpapers available...")
		notify(f"There are no wallpapers available for \"{self.current_theme.name}\"...", critical=True)

	def select_wallpaper(self):
		logging.debug("The process of selecting wallpapers using the rofi menu has begun")

		try:
			wallpaper = Selector.select_wallpaper(self.current_theme)
		except:
			logging.error(f"An error occurred while selecting wallpapers using rofi: {traceback.format_exc()}")
			return

		if wallpaper is not None:
			self.set_wallpaper(wallpaper)
			return
