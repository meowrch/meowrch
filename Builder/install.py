import subprocess
import traceback

import inquirer
from loguru import logger
from managers.apps_manager import AppsManager
from managers.chaotic_aur_manager import ChaoticAurManager
from managers.drivers_manager import DriversManager
from managers.filesystem_manager import FileSystemManager
from managers.package_manager import PackageManager
from managers.post_install_manager import PostInstallation
from packages import BASE, CUSTOM
from question import Question
from utils.schemes import BuildOptions, NotInstalledPackages, TerminalShell


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
                'in the root of the meowrch at the path "./backup/"'
            )
            logger.warning("Check the backup before you start the installation")
            input("Press Enter to continue with the installation: ")

        FileSystemManager.create_default_folders()
        FileSystemManager.copy_dotfiles(
            exclude_bspwm=not self.build_options.install_bspwm,
            exclude_hyprland=not self.build_options.install_hyprland,
        )

        # Включаем multilib и обновляем базу данных
        PackageManager.update_pacman_conf(enable_multilib=True)
        PackageManager.update_database()
        
        # Установка Chaotic AUR 
        if self.build_options.use_chaotic_aur:
            logger.info("Setting up Chaotic AUR...")
            ChaoticAurManager.install()
            
        PackageManager.install_aur_helper(self.build_options.aur_helper)

        self.packages_installation()
        self.drivers_installation()
        
        # Настройка модулей GPU для ранней загрузки (критично для Plymouth)
        DriversManager.setup_gpu_modules_for_early_boot()

        AppsManager.configure_grub()
        AppsManager.configure_sddm()
        AppsManager.configure_plymouth()
        AppsManager.configure_firefox(
            darkreader=self.build_options.ff_darkreader,
            ublock=self.build_options.ff_ublock,
            twp=self.build_options.ff_twp,
            unpaywall=self.build_options.ff_unpaywall,
            tampermonkey=self.build_options.ff_tampermonkey,
        )
        AppsManager.configure_code()
        AppsManager.configure_pawlette()

        if self.build_options.install_hyprland:
            AppsManager.configure_mewline()

        self.daemons_setting()
        PostInstallation.apply(self.build_options.terminal_shell)
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

        if self.build_options.terminal_shell == TerminalShell.ZSH:
            pacman.extend(["zsh", "zsh-syntax-highlighting", "zsh-autosuggestions", "zsh-history-substring-search"])
        else:
            pacman.append("fish")

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
            "disable": ["sddm.service"],
            "enable": ["NetworkManager", "bluetooth.service"],
            "start": ["bluetooth.service"],
        }

        error_msg = "Daemon \"{name}\" {action} error: {err}"

        for action, dmns in daemons.items():
            for d in dmns:
                try:
                    subprocess.run(["sudo", "systemctl", action, d], check=True)
                except subprocess.CalledProcessError as e:
                    logger.error(error_msg.format(action=action, name=d, err=e.stderr))
                except Exception:
                    logger.error(error_msg.format(action=action, name=d, err=traceback.format_exc()))

        logger.success("The setting of the daemons is complete!")


if __name__ == "__main__":
    logger.add(
        sink="build_debug.log",
        format="{time} | {level} | {message}",
        level="DEBUG",
        encoding="utf-8",
    )

    builder = Builder()
    builder.run()
