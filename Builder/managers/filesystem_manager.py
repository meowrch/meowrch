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
            ".themes",
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

        error_msg = "Error creating default directories: {err}"
        try:
            subprocess.run(["mkdir", "-p", *expanded_folders], check=True)
        except subprocess.CalledProcessError as e:
            logger.error(error_msg.format(err=e.stderr))
        except Exception:
            logger.error(error_msg.format(err=traceback.format_exc()))

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
                    src=item_path, dst=os.path.join(dst, item), exclusions=exclusions
                )
            else:
                shutil.copy2(item_path, dst)

    @staticmethod
    def make_backup(dst: Path = Path("./backup")) -> None:
        dst.mkdir(parents=True, exist_ok=True)
        home = Path.home()

        backup_items = [
            ".config",
            ".local/bin",
            ".gnome2",
            ".local/share/nemo",
            ".bashrc",
            ".Xresources",
            ".xinitrc",
            ".icons/default/index.theme",
        ]

        for item in backup_items:
            src_path = home / item
            dst_path = dst / item

            if not src_path.exists():
                continue

            logger.info(f'Starting to back up "{item}".')
            
            try:
                dst_path.parent.mkdir(parents=True, exist_ok=True)

                if src_path.is_dir():
                    shutil.copytree(src=src_path, dst=dst_path, dirs_exist_ok=True)
                else:
                    shutil.copy(src=src_path, dst=dst_path)
                
                logger.success(f'Successfully backed up "{item}"')
            
            except Exception:
                logger.error(
                    f"An error occurred during copying: {traceback.format_exc()}"
                )

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
            config_folders_exclusions.extend(["hypr", "waybar"])

        FileSystemManager.copy_with_exclusions(
            src=Path("./home/.config"),
            dst=home / ".config",
            exclusions=config_folders_exclusions,
        )

        shutil.copytree(
            src=Path("./home/.local"),
            dst=home / ".local",
            dirs_exist_ok=True,
        )
        shutil.copytree(
            src=Path("./home/.gnome2"),
            dst=home / ".gnome2",
            dirs_exist_ok=True,
        )
        shutil.copy(src=Path("./home/.bashrc"), dst=home / ".bashrc")
        shutil.copy(src=Path("./home/.face.icon"), dst=home / ".face.icon")

        if not exclude_bspwm:
            shutil.copy(src=Path("./home/.Xresources"), dst=home / ".Xresources")
            shutil.copy(src=Path("./home/.xinitrc"), dst=home / ".xinitrc")

        destination = home / ".icons" / "default" / "index.theme"
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src=Path("./home/.icons/default/index.theme"), dst=destination)

        ##==> Выдаем права файлам в bin
        ##############################################
        error_msg = "[!] Error while making {path} executable: {err}"
        for path in [home / ".config", home / ".local" / "bin"]:
            try:
                subprocess.run(["sudo", "chmod", "-R", "755", str(path)], check=True)
            except subprocess.CalledProcessError as e:
                logger.error(error_msg.format(path=path, err=e.stderr))
            except Exception:
                logger.error(error_msg.format(path=path, err=traceback.format_exc()))
