import os
import subprocess
import traceback

from loguru import logger

from .base import AppConfigurer


class GrubConfigurer(AppConfigurer):
    def __init__(self):
        self.grub_config_file = "/etc/default/grub"
        self.temp_config_path = "/tmp/grub"
        self.theme_path = "/boot/grub/themes/meowrch"
        self.theme_setting = f"GRUB_THEME={self.theme_path}/theme.txt\n"

    def setup(self) -> None:
        logger.info("Starting the GRUB installation process")
        if not os.path.exists(self.grub_config_file):
            logger.error("GRUB is not installed. Skipping theme installation.")
            return

        error_msg = "The installation of the grub theme failed: {err}"

        try:
            self._update_grub_config()
            self._install_theme()
            self._update_grub()
            logger.success("The GRUB theme has been successfully installed!")
        except subprocess.CalledProcessError as e:
            logger.error(error_msg.format(err=e.stderr))
        except Exception:
            logger.error(error_msg.format(err=traceback.format_exc()))

    def _update_grub_config(self) -> None:
        with open(self.grub_config_file, "r") as f:
            lines = [line for line in f if not line.startswith("GRUB_THEME")]

        lines.append(self.theme_setting)

        with open(self.temp_config_path, "w") as f:
            f.writelines(lines)

        subprocess.run(
            ["sudo", "mv", self.temp_config_path, self.grub_config_file], check=True
        )

    def _install_theme(self) -> None:
        subprocess.run(
            ["sudo", "cp", "-r", "./misc/grub_theme", self.theme_path], check=True
        )

    def _update_grub(self) -> None:
        subprocess.run(["sudo", "update-grub"], check=True)
