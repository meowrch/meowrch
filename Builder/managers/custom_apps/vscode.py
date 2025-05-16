import subprocess
import traceback

from loguru import logger

from ..package_manager import PackageManager
from .base import AppConfigurer


class VSCodeConfigurer(AppConfigurer):
    def setup(self) -> None:
        self._install_vscode()
        self._install_theme_extension()

    def _install_vscode(self) -> None:
        try:
            result = subprocess.run(
                ["code", "--version"], capture_output=True, text=True
            )
            code_exists = result.returncode == 0
        except FileNotFoundError:
            code_exists = False

        if not code_exists:
            PackageManager.install_packages(packages_list=["code"])

    def _install_theme_extension(self) -> None:
        try:
            subprocess.run(
                [
                    "code",
                    "--install-extension",
                    "dimflix-official.meowrch-theme",
                ],
                check=True,
            )
        except Exception:
            logger.error(
                f"Error installing Visual Studio Code extension: {traceback.format_exc()}"
            )
