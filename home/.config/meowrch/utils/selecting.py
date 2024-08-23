import random
import logging
import subprocess
from PIL import Image
from pathlib import Path
import multiprocessing as mp
from dataclasses import dataclass
from typing import List, Optional, Dict

from .schemes import Theme
from vars import (
	MEOWRCH_ASSETS, ROFI_SELECTING_THEME, 
	WALLPAPERS_CACHE_DIR, THEMES_CACHE_DIR
)


@dataclass
class RofiResponse:
	exit_code: int
	selected_item: Optional[str]


class Selector:
	@staticmethod
	def _create_thumbnail(image_path: Path, thumbnail_path: Path):
		if thumbnail_path.exists():
			return

		image = Image.open(image_path)
		width, height = image.size

		if width <= 500 and height <= 500:
			image.save(thumbnail_path)
			return

		if width > height:
			new_height = 500
			new_width = int(width * 500 / height)
		else:
			new_width = 500
			new_height = int(height * 500 / width)

		img = image.resize((new_width, new_height))
		img = img.crop((new_width // 2 - 500 // 2, new_height // 2 - 500 // 2, new_width // 2 + 500 // 2, new_height // 2 + 500 // 2))
		img.save(thumbnail_path)

	@classmethod
	def _generate_rofi_list(cls, elements: Dict[str, Path], cache_dir: Path, random_el_text: str) -> list[str]:
		"""
		args:
			elements: Словарь, в котором ключ - заголовок, а значение - путь к иконке.
			cache_dir: Path - Путь до папки, в которую будут кэшироваться изображения
		"""

		cache_dir.mkdir(parents=True, exist_ok=True)
		rofi_list = [f"{random_el_text}\x00icon\x1f{str(MEOWRCH_ASSETS / 'random.png')}"]

		image_paths = []
		thumbnails = []

		for name, icon in elements.items():
			if icon.is_file():
				thumbnail = cache_dir / f"{icon.stem}.png"
				thumbnails.append(thumbnail)
				image_paths.append(icon)

		with mp.Pool(processes=4) as pool:
			pool.starmap(cls._create_thumbnail, zip(image_paths, thumbnails))

		for name, icon, thumbnail in zip(elements.keys(), elements.values(), thumbnails):
			if thumbnail.is_file():
				rofi_list.append(f"{name}\x00icon\x1f{str(thumbnail)}")

		return rofi_list

	@classmethod
	def _selection(cls, title: str, input_list: list, override_theme: str = None) -> RofiResponse:
		command = ["rofi", "-dmenu", "-i", "-p", title, "-theme", str(ROFI_SELECTING_THEME)]

		if override_theme is not None:
			command.extend(["-theme-str", override_theme])

		selection = subprocess.run(
			command,
			input="\n".join(input_list), 
			capture_output=True, 
			text=True
		)

		return RofiResponse(
			exit_code=selection.returncode,
			selected_item=selection.stdout.strip().split("\x00")[0]
		)

	@classmethod
	def select_wallpaper(cls, theme: Theme) -> Optional[Path]:
		elements: Dict[str, Path] = {wall.name: wall for wall in theme.available_wallpapers}
		response = cls._selection(
			title="Choose a wallpaper:",
			input_list=cls._generate_rofi_list(
				elements=elements,
				cache_dir=WALLPAPERS_CACHE_DIR,
				random_el_text="Random Wallpaper"
			)
		)

		if response.exit_code != 0:
			logging.debug("The wallpaper selection has been canceled")
			return None

		if response.selected_item == "Random Wallpaper":
			return random.choice(theme.available_wallpapers)
		
		wall_selection_path = next((p for p in theme.available_wallpapers if p.name == response.selected_item), None)

		if wall_selection_path is not None:
			return wall_selection_path

		logging.debug("The wallpaper is not selected")
		return None

	@classmethod
	def select_theme(cls, all_themes: List[Theme]) -> None:
		elements: Dict[str, Path] = {theme.name: theme.icon for theme in all_themes}

		response = cls._selection(
			title="Choose a theme:",
			input_list=cls._generate_rofi_list(
				elements=elements,
				cache_dir=THEMES_CACHE_DIR,
				random_el_text="Random Theme",
			)
		)

		if response.exit_code != 0:
			logging.debug("Theme selection has been canceled")
			return None

		if response.selected_item == "Random Theme":
			return random.choice(all_themes)
		
		theme_selection = next((th for th in all_themes if th.name == response.selected_item), None)

		if theme_selection is not None:
			return theme_selection

		logging.debug("Theme is not selected")
		return None
