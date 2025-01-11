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
                    src=item_path, 
                    dst=os.path.join(dst, item), 
                    exclusions=exclusions
                )
            else:
                shutil.copy2(item_path, dst)

    @staticmethod
    def make_backup(dst: Path = Path("./backup")) -> None:
        os.makedirs(dst, exist_ok=True)
        home = Path.home()

        config_path = home / ".config"
        bin_path = home / "bin"
        nemo_path = home / ".local" / "share" / "nemo"
        bashrc_path = home / ".bashrc"
        env_path = home / ".env"
        xresources_path = home / ".Xresources"
        xinitrc_path = home / ".xinitrc"
        index_theme_path = home / ".icons" / "default" / "index.theme"

        if config_path.exists():
            logger.info("Starting to back up the \".config\" folder.")
            try:
                shutil.copytree(src=config_path, dst=dst / ".config", dirs_exist_ok=True)
                logger.success("Successfully backed up the \".config\" folder")
            except Exception:
                logger.error(f"An error occurred during copying: {traceback.format_exc()}")

        if bin_path.exists():
            logger.info("Starting to back up the \"bin\" folder.")
            try:
                shutil.copytree(src=bin_path, dst=dst / "bin", dirs_exist_ok=True)
                logger.success("Successfully backed up the \"bin\" folder")
            except Exception:
                logger.error(f"An error occurred during copying: {traceback.format_exc()}")

        if nemo_path.exists():
            logger.info("Starting to back up the \".local/share/nemo\" folder.")
            try:
                nemo_dest = dst / ".local" / "share" / "nemo"
                nemo_dest.mkdir(parents=True, exist_ok=True)
                shutil.copytree(
                    src=nemo_path,
                    dst=dst / ".local" / "share" / "nemo",
                    dirs_exist_ok=True,
                )
                logger.success("Successfully backed up the \".local/share/nemo\" folder")
            except Exception:
                logger.error(f"An error occurred during copying: {traceback.format_exc()}")

        if bashrc_path.exists():
            logger.info("Starting to back up the \".bashrc\" file.")
            try:
                shutil.copy(src=bashrc_path, dst=dst / ".bashrc")
                logger.success("Successfully backed up the \".bashrc\" file")
            except Exception:
                logger.error(f"An error occurred during copying: {traceback.format_exc()}")

        if env_path.exists():
            logger.info("Starting to back up the \".env\" file.")
            try:
                shutil.copy(src=env_path, dst=dst / ".env")
                logger.success("Successfully backed up the \".env\" file")
            except Exception:
                logger.error(f"An error occurred during copying: {traceback.format_exc()}")

        if xresources_path.exists():
            logger.info("Starting to back up the \".Xresources\" file.")
            try:
                shutil.copy(src=xresources_path, dst=dst / ".Xresources")
                logger.success("Successfully backed up the \".Xresources\" file")
            except Exception:
                logger.error(f"An error occurred during copying: {traceback.format_exc()}")

        if xinitrc_path.exists():
            logger.info("Starting to back up the \".xinitrc\" file.")
            try:
                shutil.copy(src=xinitrc_path, dst=dst / ".xinitrc")
                logger.success("Successfully backed up the \".xinitrc\" file")
            except Exception:
                logger.error(f"An error occurred during copying: {traceback.format_exc()}")

        if index_theme_path.exists():
            logger.info("Starting to back up the \".icons/default/index.theme\" file.")
            try:
                dest = dst / ".icons" / "default" / "index.theme"
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(src=index_theme_path, dst=dest)
                logger.success("Successfully backed up the \".icons/default/index.theme\" file")
            except Exception:
                logger.error(f"An error occurred during copying: {traceback.format_exc()}")

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
            exclusions=config_folders_exclusions,
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
