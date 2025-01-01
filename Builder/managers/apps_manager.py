import glob
import os
import shutil
import subprocess
import time
import traceback

from loguru import logger

from .package_manager import PackageManager


class AppsManager:
    @staticmethod
    def configure_code() -> str:
        try:
            result = subprocess.run(
                ["code", "--version"], capture_output=True, text=True
            )
            code_exists = result.returncode == 0
        except FileNotFoundError:
            code_exists = False

        if not code_exists:
            PackageManager.install_packages(packages_list=["code"])

        try:
            subprocess.run(
                [
                    "code",
                    "--install-extension",
                    "./misc/apps/vscode/meowrch-theme-1.0.0.vsix",
                ],
                check=True,
            )
        except Exception:
            logger.error(
                f"Error installing Visual Studio Code extension: {traceback.format_exc()}"
            )

    @staticmethod
    def configure_firefox(darkreader: bool, ublock: bool, twp: bool, unpaywall: bool, tampermonkey: bool) -> None:
        logger.info("Start installing Firefox")

        try:
            subprocess.Popen(["timeout", "2", "firefox", "--headless"])
            time.sleep(3)
            path_profile = glob.glob(
                os.path.expanduser("~/.mozilla/firefox/*.default-release")
            )[0]
            shutil.copytree(
                "./misc/apps/firefox/firefox-profile", path_profile, dirs_exist_ok=True
            )
        except Exception:
            logger.error(f"Error installing firefox: {traceback.format_exc()}")

        plugins = [
            (darkreader, "addon@darkreader.org.xpi"),
            (ublock, "uBlock0@raymondhill.net.xpi"),
            (twp, "{036a55b4-5e72-4d05-a06c-cba2dfcc134a}.xpi"),
            (unpaywall, "{f209234a-76f0-4735-9920-eb62507a54cd}.xpi"),
            (tampermonkey, "firefox@tampermonkey.net.xpi")
        ]

        for p in plugins:
            if not p[0]:
                try:
                    os.remove(path_profile + f"/extensions/{p[1]}")
                except Exception:
                    ...

        logger.success("Firefox has been successfully installed!")

    @staticmethod
    def configure_sddm() -> None:
        logger.info("Starting the SDDM installation process")
        theme_name = "meowrch"
        sddm_config_file = "/etc/sddm.conf"
        temp_sddm_config_path = "/tmp/sddm.conf"
        path_to_theme = f"/usr/share/sddm/themes/{theme_name}"
        avatars_folder = "/var/lib/AccountsService/icons/"

        with open(temp_sddm_config_path, "w") as file:
            file.write(
                f"[Theme]\nCurrent={theme_name}\nFacesDir={avatars_folder}\nCursorTheme=Bibata-Modern-Classic\n"
            )

        try:
            username = subprocess.check_output("whoami", text=True).strip()
            subprocess.run(
                [
                    "sudo",
                    "mv",
                    "./misc/.face.icon",
                    f"{avatars_folder}{username}.face.icon",
                ],
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["sudo", "mv", temp_sddm_config_path, sddm_config_file], check=True
            )
            subprocess.run(
                ["sudo", "cp", "-r", "./misc/sddm_theme", path_to_theme], check=True
            )
            logger.success("The SDDM theme has been successfully installed!")
        except Exception:
            logger.error(
                f"The installation of the SDDM theme failed: {traceback.format_exc()}"
            )

    @staticmethod
    def configure_grub() -> None:
        logger.info("Starting the GRUB installation process")
        grub_config_file = "/etc/default/grub"
        temp_grub_config_path = "/tmp/grub"
        path_to_theme = "/boot/grub/themes/meowrch"
        grub_theme_setting = f"GRUB_THEME={path_to_theme}/theme.txt\n"

        if not os.path.exists(grub_config_file):
            logger.error("GRUB is not installed. Skipping theme installation.")
            return

        with open(grub_config_file, "r") as file:
            grub_config = [
                line for line in file.readlines() if not line.startswith("GRUB_THEME")
            ]

        grub_config.append(grub_theme_setting)

        with open(temp_grub_config_path, "w") as file:
            file.writelines(grub_config)

        try:
            subprocess.run(
                ["sudo", "cp", "-r", "./misc/grub_theme", path_to_theme], check=True
            )
            subprocess.run(
                ["sudo", "mv", temp_grub_config_path, grub_config_file], check=True
            )
            subprocess.run(["sudo", "update-grub"], check=True)
            logger.success("The GRUB theme has been successfully installed!")
        except Exception:
            logger.error(
                f"The installation of the grub theme failed: {traceback.format_exc()}"
            )
