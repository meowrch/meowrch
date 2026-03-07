import subprocess
import traceback

from loguru import logger

from .base import AppConfigurer
from ..package_manager import PackageManager


class MewlineConfigurer(AppConfigurer):
    def setup(self) -> None:
        if PackageManager.check_package_installed("mewline"):
            try:
                self._create_default_config()
                self._create_hotkeys()
            except Exception:
                logger.error(f"Mewline main setup error: {traceback.format_exc()}")

    def _create_hotkeys(self) -> None:
        """Логика создания горячих клавиш для mewline"""
        logger.info("Configuring mewline keybindings...")
        subprocess.run(
            ["mewline", "--create-keybindings"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        logger.success("Mewline keybindings configured successfully!")

    def _create_default_config(self) -> None:
        """Логика создания дефолтной конфигурации mewline"""
        logger.info("Configuring mewline...")

        subprocess.run(
            ["mewline", "--generate-default-config"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
