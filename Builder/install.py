import json
import os
import subprocess
import traceback
from datetime import datetime
from pathlib import Path

import inquirer
from loguru import logger
from managers.apps_manager import AppsManager
from managers.chaotic_aur_manager import ChaoticAurManager
from managers.drivers_manager import ChdwManager
from managers.filesystem_manager import FileSystemManager
from managers.package_manager import PackageManager
from managers.post_install_manager import PostInstallation
from packages import BASE, CUSTOM
from question import Question
from utils.config_backup import ConfigBackup
from utils.schemes import BuildOptions, NotInstalledPackages, TerminalShell

__VERSION__ = "3.0.4"


class Builder:
    not_installed_packages = NotInstalledPackages()

    def run(self) -> None:
        logger.success(
            "The program has been launched successfully. We are starting the survey."
        )
        self.build_options: BuildOptions = Question.get_answers()
        logger.info(f"User Responses to Questions: {self.build_options}")

        # Убираем пакеты в зависимости от выбора пользователя
        if self.build_options.terminal_shell != TerminalShell.ZSH:
            BASE.pacman.common.remove("zsh")
            BASE.pacman.common.remove("zsh-syntax-highlighting")
            BASE.pacman.common.remove("zsh-autosuggestions")
            BASE.pacman.common.remove("zsh-history-substring-search")

        if self.build_options.terminal_shell != TerminalShell.FISH:
            BASE.pacman.common.remove("fish")

        if not self.build_options.install_grub:
            BASE.aur.common.remove("update-grub")

        if not self.build_options.install_plymouth:
            BASE.pacman.common.remove("plymouth")

        if not self.build_options.install_sddm:
            BASE.pacman.common.remove("sddm")
        
        # If dracut is already installed on the system, avoid installing mkinitcpio
        if PackageManager.check_package_installed("dracut"):
            if "mkinitcpio" in BASE.pacman.common:
                BASE.pacman.common.remove("mkinitcpio")
                logger.info("Detected dracut; skipping mkinitcpio installation.")

        # Проверка существующей установки
        if self._check_existing_installation():
            logger.warning("Meowrch is already installed for this user!")
            if not inquirer.confirm(
                "Continue anyway? This will update the installation."
            ):
                return

        # Создаём временный маркер начала установки
        self._create_installation_marker()

        try:
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

            # Backup all critical system configs before any modifications
            ConfigBackup.backup_all()

            # Включаем multilib и обновляем базу данных
            PackageManager.update_pacman_conf(enable_multilib=True)
            PackageManager.update_database()

            # Установка Chaotic AUR
            if self.build_options.use_chaotic_aur:
                logger.info("Setting up Chaotic AUR...")
                ChaoticAurManager.install()

            PackageManager.install_aur_helper(self.build_options.aur_helper)

            self.packages_installation()

            # Установка драйверов через chwd
            ChdwManager().install()

            if self.build_options.install_grub:
                AppsManager.configure_grub()

            if self.build_options.install_sddm:
                AppsManager.configure_sddm()

            if self.build_options.install_plymouth:
                AppsManager.configure_plymouth(
                    allow_grub_config=self.build_options.install_grub
                )

            AppsManager.configure_firefox(
                darkreader=self.build_options.ff_darkreader,
                ublock=self.build_options.ff_ublock,
                twp=self.build_options.ff_twp,
                unpaywall=self.build_options.ff_unpaywall,
                vot=self.build_options.ff_vot,
            )
            AppsManager.configure_code()

            if self.build_options.install_hyprland:
                AppsManager.configure_mewline()

            AppsManager.configure_pawlette()

            self.daemons_setting()
            PostInstallation.apply(self.build_options)

            self._write_installation_metadata(__VERSION__)

            logger.warning(
                "The script was unable to automatically install these packages."
                "Try installing them manually."
            )
            logger.warning("Pacman: " + ", ".join(self.not_installed_packages.pacman))
            logger.warning("Aur: " + ", ".join(self.not_installed_packages.aur))
            logger.success(
                "Meowrch has been successfully installed! Restart your PC to apply the changes."
            )
        except BaseException:
            logger.error(f"Installation failed: {traceback.format_exc()}")
            self._cleanup_failed_installation()
            raise

        is_reboot = inquirer.confirm("Do you want to reboot?")
        if is_reboot:
            subprocess.run("sudo reboot", shell=True)

    def packages_installation(self) -> None:
        logger.info("Starting the package installation process")
        pacman, aur = self._collect_selected_packages()

        # Устанавливаем pacman пакеты
        self.not_installed_packages.pacman.extend(
            PackageManager.install_packages(pacman)
        )

        # Устанавливаем aur пакеты
        self.not_installed_packages.aur.extend(
            PackageManager.install_packages(aur, aur=self.build_options.aur_helper)
        )

        logger.success("The installation process of all packages is complete!")

    def _collect_selected_packages(self):
        pacman: list[str] = []
        aur: list[str] = []

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

        # Deduplicate while preserving order
        pacman = list(dict.fromkeys(pacman))
        aur = list(dict.fromkeys(aur))
        return pacman, aur

    def daemons_setting(self) -> None:
        logger.info("The daemons are starting to run...")

        daemons = {
            "enable": ["NetworkManager", "bluetooth.service"],
            "start": ["bluetooth.service"],
        }

        if self.build_options.install_sddm:
            daemons["enable"].append("sddm.service")

        user_daemons = {
            "enable": ["battery-monitor.timer"],
            "start": ["battery-monitor.timer"],
        }

        error_msg = 'Daemon "{name}" {action} error: {err}'

        for action, dmns in daemons.items():
            for d in dmns:
                try:
                    subprocess.run(["sudo", "systemctl", action, d], check=True)
                except subprocess.CalledProcessError as e:
                    logger.error(error_msg.format(action=action, name=d, err=e.stderr))
                except Exception:
                    logger.error(
                        error_msg.format(
                            action=action, name=d, err=traceback.format_exc()
                        )
                    )

        for action, dmns in user_daemons.items():
            for d in dmns:
                try:
                    subprocess.run(["systemctl", "--user", action, d], check=True)
                except subprocess.CalledProcessError as e:
                    logger.error(error_msg.format(action=action, name=d, err=e.stderr))
                except Exception:
                    logger.error(
                        error_msg.format(
                            action=action, name=d, err=traceback.format_exc()
                        )
                    )

        logger.success("The setting of the daemons is complete!")

    def _write_installation_metadata(self, version: str) -> None:
        metadata = {
            "version": version,
            "installed_at": datetime.now().isoformat(),
            "user": os.getenv("USER"),
            "install_type": "full",
            "dotfiles_applied": True,
        }

        base_dir = Path(f"/usr/local/share/meowrch/users/{os.getenv('USER')}")
        subprocess.run(["sudo", "mkdir", "-p", str(base_dir)], check=True)

        # Записываем версию
        subprocess.run(
            ["sudo", "tee", str(base_dir / "version")],
            input=version.encode(),
            stdout=subprocess.DEVNULL,
            check=True,
        )

        # Записываем метаданные
        subprocess.run(
            ["sudo", "tee", str(base_dir / ".installed")],
            input=json.dumps(metadata, indent=2).encode(),
            stdout=subprocess.DEVNULL,
            check=True,
        )

        # Устанавливаем права: только чтение для пользователя
        subprocess.run(["sudo", "chmod", "444", str(base_dir / "version")], check=True)
        subprocess.run(
            ["sudo", "chmod", "444", str(base_dir / ".installed")], check=True
        )

        # Удаляем временный маркер установки
        subprocess.run(["sudo", "rm", "-f", str(base_dir / ".installing")], check=False)

        logger.success(f"Version metadata protected: {version}")

    def _check_existing_installation(self) -> bool:
        version_file = Path(
            f"/usr/local/share/meowrch/users/{os.getenv('USER')}/version"
        )
        return version_file.exists()

    def _create_installation_marker(self) -> None:
        base_dir = Path(f"/usr/local/share/meowrch/users/{os.getenv('USER')}")
        subprocess.run(["sudo", "mkdir", "-p", str(base_dir)], check=True)

        # Временный файл для отслеживания процесса
        subprocess.run(
            ["sudo", "tee", str(base_dir / ".installing")],
            input=b"installation_in_progress",
            stdout=subprocess.DEVNULL,
            check=True,
        )

    def _cleanup_failed_installation(self) -> None:
        base_dir = Path(f"/usr/local/share/meowrch/users/{os.getenv('USER')}")

        # Удаляем временный маркер
        subprocess.run(["sudo", "rm", "-f", str(base_dir / ".installing")], check=False)

        logger.warning("Installation markers cleaned up due to failure")


if __name__ == "__main__":
    logger.add(
        sink="build_debug.log",
        format="{time} | {level} | {message}",
        level="DEBUG",
        encoding="utf-8",
    )

    builder = Builder()
    builder.run()
