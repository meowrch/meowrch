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
        error_msg = "Error installing Visual Studio Code extension: {err}"
        try:
            subprocess.run(
                [
                    "code",
                    "--install-extension",
                    "dimflix-official.meowrch-theme",
                ],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            logger.error(error_msg.format(err=e.stderr))
        except Exception:
            logger.error(error_msg.format(err=traceback.format_exc()))
