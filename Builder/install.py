import os
import subprocess
import traceback

import inquirer
from loguru import logger
from managers.apps_manager import AppsManager
from managers.drivers_manager import DriversManager
from managers.filesystem_manager import FileSystemManager
from managers.package_manager import PackageManager
from packages import BASE, CUSTOM
from question import Question
from utils.schemes import BuildOptions, NotInstalledPackages, AurHelper


class Builder:
    not_installed_packages = NotInstalledPackages()

    def run(self) -> None:
        logger.success(
            "The program has been launched successfully. We are starting the survey."
        )
        self.build_options: BuildOptions = Question.get_answers()
        logger.info(f"User Responses to Questions: {self.build_options}")
        
        if self.build_options.make_backup:
            logger.info(
                "The process of creating a backup of configurations is started!"
            )
            FileSystemManager.make_backup()
            logger.warning(
                "A backup of all your configuration files is located "
                "in the root of the meowrch at the path \"./backup/\""
            )
            logger.warning("Check the backup before you start the installation")
            input("Press Enter to continue with the installation: ")

        FileSystemManager.create_default_folders()
        FileSystemManager.copy_dotfiles(
            exclude_bspwm=not self.build_options.install_bspwm,
            exclude_hyprland=not self.build_options.install_hyprland,
        )

        PackageManager.update_pacman_conf(
            enable_multilib=self.build_options.enable_multilib
        )

        if self.build_options.aur_helper == AurHelper.PARU:
            PackageManager.install_paru_manager()
        elif self.build_options.aur_helper == AurHelper.YAY:
            PackageManager.install_aur_manager()
        else:
            logger.error("Unsupported AUR helper!")
            exit(1)

        if self.build_options.update_arch_database:
            PackageManager.update_database()

        self.packages_installation()
        self.drivers_installation()

        AppsManager.configure_grub()
        AppsManager.configure_sddm()
        AppsManager.configure_firefox(
            darkreader=self.build_options.ff_darkreader,
            ublock=self.build_options.ff_ublock,
            twp=self.build_options.ff_twp,
            unpaywall=self.build_options.ff_unpaywall,
            tampermonkey=self.build_options.ff_tampermonkey
        )
        AppsManager.configure_code()

        self.daemons_setting()
        self.post_conf()
        logger.warning(
            "The script was unable to automatically install these packages." 
            "Try installing them manually."
        )
        logger.warning("Pacman: " + ", ".join(self.not_installed_packages.pacman))
        logger.warning("Aur: " + ", ".join(self.not_installed_packages.aur))
        logger.success(
            "Meowch has been successfully installed! Restart your PC to apply the changes."
        )

        is_reboot = inquirer.confirm("Do you want to reboot?")
        if is_reboot:
            subprocess.run("sudo reboot", shell=True)

    def packages_installation(self) -> None:
        logger.info("Starting the package installation process")
        pacman, aur = [], []

        pacman.extend(BASE.pacman.common)
        aur.extend(BASE.aur.common)

        for category in CUSTOM.keys():
            for package, info in CUSTOM[category].items():
                if not info.selected:
                    continue
                if info.aur:
                    aur.append(package)
                else:
                    pacman.append(package)

        for wm in ["bspwm", "hyprland"]:
            if getattr(self.build_options, f"install_{wm}"):
                pacman.extend(getattr(BASE.pacman, f"{wm}_packages"))
                aur.extend(getattr(BASE.aur, f"{wm}_packages"))

        # Устанавливаем pacman пакеты
        self.not_installed_packages.pacman.extend(
            PackageManager.install_packages(pacman)
        )
        
        # Устанавливаем aur пакеты
        self.not_installed_packages.aur.extend(
            PackageManager.install_packages(aur, aur=self.build_options.aur_helper)
        )
    
        logger.success("The installation process of all packages is complete!")

    def drivers_installation(self) -> None:
        logger.info("Starting the driver installation process")

        if self.build_options.intel_driver:
            DriversManager.install_intel_drivers()
        if self.build_options.nvidia_driver:
            DriversManager.install_nvidia_drivers()
        if self.build_options.amd_driver:
            DriversManager.install_amd_drivers()

        logger.success("The installation process of all drivers is complete!")

    def daemons_setting(self) -> None:
        logger.info("The daemons are starting to run...")

        daemons = {
            "enable": ["NetworkManager", "bluetooth.service", "sddm.service"],
            "start": ["bluetooth.service"],
        }

        for d in daemons["enable"]:
            try:
                subprocess.run(["sudo", "systemctl", "enable", d], check=True)
            except Exception:
                logger.error(
                    f'Error starting the "{d}" daemon: {traceback.format_exc()}'
                )

        for d in daemons["start"]:
            try:
                subprocess.run(["sudo", "systemctl", "start", d], check=True)
            except Exception:
                logger.error(
                    f'Error starting the "{d}" daemon: {traceback.format_exc()}'
                )

        logger.success("The setting of the daemons is complete!")

    def post_conf(self) -> None:
        logger.info("The post-installation configuration is starting...")

        try:
            subprocess.run(["chsh", "-s", "/usr/bin/fish"], check=True)
            logger.success("The shell is changed to fish!")
        except Exception:
            logger.error(f"Error changing shell: {traceback.format_exc()}")

        if (
            "games" in CUSTOM
            and "gamemode" in CUSTOM["games"]
            and CUSTOM["games"]["gamemode"].selected
        ):
            try:
                username = os.getenv("USER") or os.getenv("LOGNAME")
                subprocess.run(
                    ["sudo", "usermod", "-a", username, "-G", "gamemode"], check=True
                )
                logger.success("The user is added to the gamemode group!")
            except Exception:
                logger.error(
                    f"Error adding user to group for gamemode: {traceback.format_exc()}"
                )

        try:
            subprocess.run(
                [
                    "gsettings",
                    "set",
                    "org.cinnamon.desktop.default-applications.terminal",
                    "exec",
                    "kitty",
                ],
                check=True,
            )
            logger.success("The default terminal is set to kitty!")
        except Exception:
            logger.error(f"Error setting default terminal: {traceback.format_exc()}")

        logger.info("The post-installation configuration is complete!")


if __name__ == "__main__":
    logger.add(
        sink="build_debug.log",
        format="{time} | {level} | {message}",
        level="DEBUG",
        encoding="utf-8",
    )

    builder = Builder()
    builder.run()
