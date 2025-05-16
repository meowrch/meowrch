import glob
import os
import shutil
import subprocess
import time
import traceback

from loguru import logger

from .base import AppConfigurer


class FirefoxConfigurer(AppConfigurer):
    def __init__(
        self,
        darkreader: bool,
        ublock: bool,
        twp: bool,
        unpaywall: bool,
        tampermonkey: bool,
    ):
        self.plugins = [
            (darkreader, "addon@darkreader.org.xpi"),
            (ublock, "uBlock0@raymondhill.net.xpi"),
            (twp, "{036a55b4-5e72-4d05-a06c-cba2dfcc134a}.xpi"),
            (unpaywall, "{f209234a-76f0-4735-9920-eb62507a54cd}.xpi"),
            (tampermonkey, "firefox@tampermonkey.net.xpi")
        ]

    def setup(self) -> None:
        logger.info("Start installing Firefox")
        try:
            self._init_firefox_profile()
            self._copy_profile()
            self._cleanup_plugins()
            logger.success("Firefox has been successfully installed!")
        except Exception:
            logger.error(f"Error installing firefox: {traceback.format_exc()}")

    def _init_firefox_profile(self) -> None:
        subprocess.Popen(["timeout", "2", "firefox", "--headless"])
        time.sleep(3)

    def _copy_profile(self) -> None:
        path_profile = glob.glob(
            os.path.expanduser("~/.mozilla/firefox/*.default-release")
        )[0]
        shutil.copytree(
            "./misc/apps/firefox/firefox-profile", path_profile, dirs_exist_ok=True
        )

    def _cleanup_plugins(self) -> None:
        path_profile = glob.glob(
            os.path.expanduser("~/.mozilla/firefox/*.default-release")
        )[0]
        for enabled, plugin_file in self.plugins:
            if not enabled:
                try:
                    os.remove(os.path.join(path_profile, "extensions", plugin_file))
                except Exception:
                    pass
