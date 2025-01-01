import os
import shutil
import subprocess
import traceback
from pathlib import Path

from loguru import logger


class FileSystemManager:
    @staticmethod
    def create_default_folders() -> None:
        logger.success("Starting the process of creating default directories")

        default_folders = [
            ".config",
            "Desktop",
            "Downloads",
            "Templates",
            "Public",
            "Documents",
            "Music",
            "Pictures",
            "Videos",
        ]

        expanded_folders = [str(Path.home() / folder) for folder in default_folders]

        try:
            subprocess.run(["mkdir", "-p", *expanded_folders], check=True)
        except Exception:
            logger.error(
                f"Error creating default directories: {traceback.format_exc()}"
            )

        logger.success("The process of creating default directories is complete!")

    @staticmethod
    def copy_with_exclusions(src: Path, dst: Path, exclusions: list) -> None:
        os.makedirs(dst, exist_ok=True)

        for item in os.listdir(src):
            item_path = os.path.join(src, item)
            if item in exclusions:
                continue

            if os.path.isdir(item_path):
                FileSystemManager.copy_with_exclusions(
                    item_path, 
                    os.path.join(dst, item), 
                    exclusions
                )
            else:
                shutil.copy2(item_path, dst)

    @staticmethod
    def copy_dotfiles(exclude_bspwm: bool, exclude_hyprland: bool) -> None:
        logger.success("Starting the process of copying dotfiles")
        home = Path.home()

        ##==> Копирование дотфайлов
        ##############################################
        config_folders_exclusions = []
        if exclude_bspwm:
            config_folders_exclusions.extend(["bspwm", "polybar"])
        if exclude_hyprland:
            config_folders_exclusions.extend(["hypr", "swaylock", "waybar"])

        FileSystemManager.copy_with_exclusions(
            src=Path("./home/.config"),
            dst=home / ".config",
            exclusions=config_folders_exclusions
        )

        shutil.copytree(src=Path("./home/bin"), dst=home / "bin", dirs_exist_ok=True)
        shutil.copytree(
            src=Path("./home/.local/share/nemo"),
            dst=home / ".local" / "share" / "nemo",
            dirs_exist_ok=True,
        )
        shutil.copy(src=Path("./home/.bashrc"), dst=home / ".bashrc")
        shutil.copy(src=Path("./home/.env"), dst=home / ".env")

        if not exclude_bspwm:
            shutil.copy(src=Path("./home/.Xresources"), dst=home / ".Xresources")
            shutil.copy(src=Path("./home/.xinitrc"), dst=home / ".xinitrc")

        destination = home / ".icons" / "default" / "index.theme"
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src=Path("./home/.icons/default/index.theme"), dst=destination)

        ##==> Выдаем права
        ##############################################
        for path in [home / ".config", home / "bin"]:
            try:
                subprocess.run(["sudo", "chmod", "-R", "700", str(path)], check=True)
            except Exception:
                logger.error(
                    f"[!] Error while making {path} executable: {traceback.format_exc()}"
                )
