import shutil
import traceback
import subprocess
from pathlib import Path
from loguru import logger



class FileSystemManager:
	@staticmethod
	def create_default_folders() -> None:
		logger.success("Starting the process of creating default directories")
		
		default_folders = [
			"~/.config", "~/Desktop", "~/Downloads", "~/Templates", "~/Public",
			"~/Documents", "~/Music", "~/Pictures", "~/Videos"
		]

		expanded_folders = [str(Path.home() / folder) for folder in default_folders]

		try:
			subprocess.run(["mkdir", "-p", *expanded_folders], check=True)
		except Exception:
			logger.error(f"Error creating default directories: {traceback.format_exc()}")

		logger.success("The process of creating default directories is complete!")

	@staticmethod
	def copy_dotfiles(remove_bspwm: bool, remove_hyprland: bool) -> None:
		logger.success("Starting the process of copying dotfiles")
		home = Path.home()

		def make_executable(directory):
			for path in Path(directory).rglob('*.sh'):
				try:
					subprocess.run(["sudo", "chmod", "-R", "700", str(path)], check=True)
				except Exception:
					logger.error(f"[!] Error while making {path} executable: {traceback.format_exc()}")
					continue
	
				logger.info(f"Made {path} executable")

		##==> Копирование дотфайлов
		##############################################
		shutil.copytree(src=Path("./home/.config"), dst=home / ".config", dirs_exist_ok=True)
		shutil.copytree(src=Path("./home/bin"), dst=home, dirs_exist_ok=True)
		shutil.copytree(src=Path("./home/.local/share/nemo"), dst=home / ".local" / "share" / "nemo", dirs_exist_ok=True)
		shutil.copy(src=Path("./home/.bashrc"), dst=home / ".bashrc")
		shutil.copy(src=Path("./home/.env"), dst=home / ".env")
		shutil.copy(src=Path("./home/.face.icon"), dst=home / ".face.icon")
		shutil.copy(src=Path("./home/.Xresources"), dst=home / ".Xresources")
		shutil.copy(src=Path("./home/.xinitrc"), dst=home / ".xinitrc")

		destination = home / ".icons" / "default" / "index.theme"
		destination.parent.mkdir(parents=True, exist_ok=True)
		shutil.copy(src=Path("./home/icons/default/index.theme"), dst=destination)

		##==> Удаляем лишнее
		##############################################
		if remove_bspwm:
			shutil.rmtree(home / ".config" / "bspwm", ignore_errors=True)
			shutil.rmtree(home / ".config" / "polybar", ignore_errors=True)
		if remove_hyprland:
			shutil.rmtree(home / ".config" / "hypr", ignore_errors=True)
			shutil.rmtree(home / ".config" / "swaylock", ignore_errors=True)
			shutil.rmtree(home / ".config" / "waybar", ignore_errors=True)

		##==> Делаем исполняемыми
		##############################################
		make_executable("./home/config")
		make_executable("./home/bin")

	
