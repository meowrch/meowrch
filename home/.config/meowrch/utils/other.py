import os
import shutil
import subprocess
from pathlib import Path
from os.path import expandvars
from typing import List, Optional

from vars import OOMOX_TEMPLATES, THEME_GEN_SCRIPT


def parse_wallpapers(paths: List[str]):
		"""
		Accepts a list of strings with paths to the wallpaper and returns a list of all found files.
		Supports:
		- Tilde for the home directory
		- Masks of the form *.png, *.jpg, etc.
		"""
		all_wallpapers = []

		for path_str in paths:
			path = Path(expandvars(path_str.strip())).expanduser()

			if path.is_absolute() and path.parts[0] == "~":
				path = Path.home().joinpath(*path.parts[1:])
	
			if "*" in path.name:
				all_wallpapers.extend(list(path.parent.glob(path.name)))
			elif path.exists():
				all_wallpapers.append(path)
		
		return all_wallpapers
		
def notify(title: str, message: str, critical=False) -> None:
	subprocess.run(['dunstify', title, message, '-u', 'critical' if critical else 'normal'])

def overcopy(src: Path, dst: Path) -> None:
	if dst.exists():
		if dst.is_dir():
			shutil.rmtree(dst)
		else:
			os.remove(str(dst))

	if src.is_dir():
		shutil.copytree(src, dst)
	else:
		shutil.copy(src, dst)

def generate_theme(template_name: str, oomox_colors: Path) -> Optional[str]:
	template = OOMOX_TEMPLATES / template_name
	if not template.exists():
		return None

	try:
		theme = subprocess.run(
			["python", str(THEME_GEN_SCRIPT), str(template), str(oomox_colors)], 
			stdout=subprocess.PIPE,
			check=True
		).stdout.decode().strip()
		return theme
	except subprocess.CalledProcessError:
		return None