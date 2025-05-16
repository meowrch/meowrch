import os
import subprocess
import traceback
from typing import List

from loguru import logger
from utils.schemes import AurHelper


class PackageManager:
    @staticmethod
    def update_database() -> None:
        logger.info("Starting to update the package database.")
        error_msg = "Error updating package database: {err}"
        try:
            subprocess.run(["sudo", "pacman", "-Sy"], check=True)
            logger.success("The package database update was successful!")
        except subprocess.CalledProcessError as e:
            logger.error(error_msg.format(err=e.stderr))
        except Exception:
            logger.error(error_msg.format(err=traceback.format_exc()))

    @staticmethod
    def check_package_installed(package: str) -> bool:
        try:
            subprocess.run(
                ["pacman", "-Q", package],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            return True
        except Exception:
            return False

    @staticmethod
    def clone_repository(repo_url: str, target_path: str) -> bool:
        error_msg = 'Error while cloning repository "{repo_url}": {err}'
        try:
            os.makedirs(os.path.dirname(target_path), exist_ok=True)

            subprocess.run(
                ["git", "clone", repo_url, target_path],
                check=True,
            )
            return True
        except subprocess.CalledProcessError as e:
            logger.error(error_msg.format(repo_url=repo_url, err=e.stderr))
            return False
        except Exception:
            logger.error(error_msg.format(repo_url=repo_url, err=traceback.format_exc()))
            return False

    @staticmethod
    def install_aur_manager() -> None:
        logger.info('Starting the "yay" package manager installation process.')
        target_path = "/tmp/yay"
        error_msg = 'Error while installing "yay": {err}'
        try:
            PackageManager.install_packages(["git", "base-devel"])

            if not PackageManager.check_package_installed("yay"):
                if not os.path.exists(target_path):
                    cloned = PackageManager.clone_repository(
                        repo_url="https://aur.archlinux.org/yay.git",
                        target_path=target_path,
                    )

                    if not cloned:
                        return

                subprocess.run(["makepkg", "-si"], cwd=target_path, check=True)
        except subprocess.CalledProcessError as e:
            logger.error(error_msg.format(err=e.stderr))
            exit(1)
        except Exception:
            logger.error(error_msg.format(err=traceback.format_exc()))
            exit(1)

        logger.success('Package "yay" has been successfully installed!')

    @staticmethod
    def install_paru_manager() -> None:
        logger.info('Starting the "paru" package manager installation process.')
        target_path = "/tmp/paru"
        error_msg = 'Error while installing "paru": {err}'
        try:
            PackageManager.install_packages(["git", "base-devel"])

            if not PackageManager.check_package_installed("paru"):
                if not os.path.exists(target_path):
                    cloned = PackageManager.clone_repository(
                        repo_url="https://aur.archlinux.org/paru.git",
                        target_path=target_path,
                    )

                    if not cloned:
                        return

                subprocess.run(["makepkg", "-si"], cwd=target_path, check=True)
        except subprocess.CalledProcessError as e:
            logger.error(error_msg.format(err=e.stderr))
            exit(1)
        except Exception:
            logger.error(error_msg.format(err=traceback.format_exc()))
            exit(1)

        logger.success('Package "paru" has been successfully installed!')

    @staticmethod
    def install_i3lock_color() -> bool:
        dir_name = "i3lock-color"
        target_path = f"/tmp/{dir_name}"

        try:
            PackageManager.install_packages(["git", "base-devel"])

            if os.path.exists(target_path):
                subprocess.run(["sudo", "rm", "-rf", target_path], check=True)

            cloned = PackageManager.clone_repository(
                "https://github.com/Raymo111/i3lock-color.git", target_path
            )

            if not cloned:
                return False

            subprocess.run(
                ["sh", "./install-i3lock-color.sh"], cwd=target_path, check=True
            )
            return True
        except Exception:
            return False

    @staticmethod
    def install_package(
        package: str, aur: AurHelper = None, error_retries: int = 3
    ) -> bool:
        """Installs the package with pacman or some aur helper

        Args:
            package (str): Name of the package to be installed
            aur (AurHelper, optional): If you need to install via the AUR helper, you need to specify it here. Defaults to None.
            error_retries (int, optional): How many times will the function attempt to install the package. Defaults to 3.

        Returns:
            bool: Status, whether the package is installed or not
        """

        error_msg = 'Error while installing package "{package}": {err}'

        for _ in range(error_retries):
            try:
                if aur is not None:
                    subprocess.run(
                        [aur.value, "-S", "--noconfirm", "--needed", package],
                        check=True,
                    )
                else:
                    subprocess.run(
                        ["sudo", "pacman", "-S", "--noconfirm", "--needed", package],
                        check=True,
                    )
                logger.success(f'Package "{package}" has been successfully installed!')
                return True
            except subprocess.CalledProcessError as e:
                # Для проблемных пакетов
                if package == "i3lock-color":
                    if PackageManager.install_i3lock_color():
                        return True

                logger.error(error_msg.format(package=package, err=e.stderr))
            except Exception:
                # Для проблемных пакетов
                if package == "i3lock-color":
                    if PackageManager.install_i3lock_color():
                        return True

                logger.error(error_msg.format(package=package, err=traceback.format_exc()))

            continue

        return False

    @staticmethod
    def install_packages(packages_list: List[str], aur: AurHelper = None) -> List[str]:
        """Installs a lot of packages via pacman or some aur helper

        Args:
            packages_list (List[str]): List of package names
            aur (AurHelper, optional): If you need to install via the AUR helper, you need to specify it here. Defaults to None.

        Returns:
            List[str]: List of packages that could not be installed
        """
        not_installed_packages = []

        for package in packages_list:
            installed = PackageManager.install_package(package=package, aur=aur)

            if not installed:
                not_installed_packages.append(package)

        return not_installed_packages

    @staticmethod
    def update_pacman_conf(*, enable_multilib: bool = False):
        pacman_config_path = "/etc/pacman.conf"
        temp_pacman_config_path = "/tmp/meowrhc-pacman.conf"

        updated_lines = []
        multilib_found = False
        multilib_section = "[multilib]"
        multilib_repo = "Include = /etc/pacman.d/mirrorlist"
        options = {
            "ParallelDownloads": "5",
            "VerbosePkgLists": "",
            "ILoveCandy": "",
            "Color": "",
        }

        if os.path.isfile(pacman_config_path):
            with open(pacman_config_path, "r") as file:
                lines = file.readlines()

            for line in lines:
                if line.startswith("#") and any(opt in line for opt in options.keys()):
                    line = line[1:]

                for key, value in options.items():
                    if key in line:
                        if value == "":
                            line = f"{key}\n"
                        else:
                            line = f"{key} = {value}\n"
                        break

                if line.startswith(multilib_section):
                    multilib_found = True

                updated_lines.append(line)

            if not multilib_found and enable_multilib:
                updated_lines.append(f"\n{multilib_section}\n{multilib_repo}\n")

            with open(temp_pacman_config_path, "w") as file:
                file.writelines(updated_lines)

            error_msg = "Error while configuring pacman: {err}"
            try:
                subprocess.run(
                    ["sudo", "mv", temp_pacman_config_path, pacman_config_path],
                    check=True,
                )
                logger.success("Pacman has been successfully configured!")
            except subprocess.CalledProcessError as e:
                logger.error(err=error_msg.format(e.stderr))
            except Exception:
                logger.error(err=error_msg.format(traceback.format_exc()))
        else:
            logger.warning("Pacman configuration skipped... (file not found)")
