import os
import subprocess
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

from loguru import logger


class PackageManager:
    @staticmethod
    def update_database() -> None:
        logger.info("Starting to update the package database.")

        try:
            subprocess.run(["sudo", "pacman", "-Sy"], check=True)
            logger.success("The package database update was successful!")
        except Exception:
            logger.error(f"Error updating package database: {traceback.format_exc()}")

    @staticmethod
    def check_yay_installed() -> bool:
        try:
            subprocess.run(
                ["yay", "--version"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            return True
        except subprocess.CalledProcessError:
            return False
        except FileNotFoundError:
            return False

    @staticmethod
    def clone_repository(repo_url: str, target_path: str) -> bool:
        try:
            os.makedirs(os.path.dirname(target_path), exist_ok=True)

            subprocess.run(
                ["git", "clone", repo_url, target_path],
                check=True,
            )
            return True
        except Exception as e:
            logger.error(f'Error while cloning repository "{repo_url}": {e}')
            return False

    @staticmethod
    def install_aur_manager() -> None:
        logger.info("Starting the yay package manager installation process.")
        target_path = "/tmp/yay"

        try:
            subprocess.run(
                ["sudo", "pacman", "-S", "--noconfirm", "--needed", "git"], check=True
            )

            if not PackageManager.check_yay_installed():
                if not os.path.exists(target_path):
                    cloned = PackageManager.clone_repository(
                        repo_url="https://aur.archlinux.org/yay.git",
                        target_path=target_path,
                    )

                    if not cloned:
                        return

                subprocess.run(["makepkg", "-si"], cwd=target_path, check=True)
        except Exception:
            logger.error(f"Error while installing yay: {traceback.format_exc()}")
            exit(1)

        logger.success('Package "yay" has been successfully installed!')

    @staticmethod
    def install_i3lock_color() -> bool:
        dir_name = "i3lock-color"
        target_path = f"/tmp/{dir_name}"

        try:
            subprocess.run(
                ["sudo", "pacman", "-S", "--noconfirm", "--needed", "git"], check=True
            )

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
    def install_package(package: str, aur: bool) -> None:
        try:
            if aur:
                subprocess.run(
                    ["yay", "-S", "--noconfirm", "--needed", package], check=True
                )
            else:
                subprocess.run(
                    ["sudo", "pacman", "-S", "--noconfirm", "--needed", package],
                    check=True,
                )
            logger.success(f'Package "{package}" has been successfully installed!')
        except Exception:
            # Для проблемных пакетов
            if package == "i3lock-color":
                if PackageManager.install_i3lock_color():
                    return  # Установка прошла успешно, выходим из функции

            logger.error(
                f'Error while installing package "{package}": {traceback.format_exc()}'
            )

    @staticmethod
    def install_packages(packages_list: List[str], aur: bool = False) -> None:
        max_workers = 5
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(PackageManager.install_package, package, aur): package
                for package in packages_list
            }

            for future in as_completed(futures):
                package = futures[future]
                try:
                    future.result()
                except Exception as e:
                    logger.error(f'Failed to install package "{package}": {e}')

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

            try:
                subprocess.run(
                    ["sudo", "mv", temp_pacman_config_path, pacman_config_path],
                    check=True,
                )
                logger.success("Pacman has been successfully configured!")
            except Exception:
                logger.error(
                    f"Error while configuring pacman: {traceback.format_exc()}"
                )
        else:
            logger.warning("Pacman configuration skipped... (file not found)")
