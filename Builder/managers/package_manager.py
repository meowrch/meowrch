import os
import traceback
import subprocess
from loguru import logger
from typing import List


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
			subprocess.run(['yay', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			return True
		except subprocess.CalledProcessError:
			return False
		except FileNotFoundError:
			return False

	@staticmethod
	def install_aur_manager() -> None:
		logger.info("Starting the yay package manager installation process.")

		try:
			subprocess.run(["sudo", "pacman", "-S", "--noconfirm", "--needed", "git"], check=True)

			if not PackageManager.check_yay_installed():
				if not os.path.exists("/tmp/yay"):
					subprocess.run(["git", "-C", "/tmp", "clone", "https://aur.archlinux.org/yay.git"], check=True)

				subprocess.run(["makepkg", "-si"], cwd="/tmp/yay", check=True)
		except Exception:
			logger.error(f"Error while installing yay: {traceback.format_exc()}")
			exit(1)

		logger.success("Package \"yay\" has been successfully installed!")

	@staticmethod
	def install_packages(packages_list: List[str], aur: bool = False) -> None:
		for package in packages_list:
			try:
				if aur:
					subprocess.run(["yay", "-S", "--noconfirm", "--needed", package], check=True)
				else:
					subprocess.run(["sudo", "pacman", "-S", "--noconfirm", "--needed", package], check=True)
			except Exception:
				logger.error(f"Error while installing package \"{package}\": {traceback.format_exc()}")
				continue

			logger.success(f"Package \"{package}\" has been successfully installed!")

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
			"Color": ""
		}

		if os.path.isfile(pacman_config_path):
			with open(pacman_config_path, 'r') as file:
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

			with open(temp_pacman_config_path, 'w') as file:
				file.writelines(updated_lines)

			try:
				subprocess.run(["sudo", "mv", temp_pacman_config_path, pacman_config_path], check=True)
				logger.success("Pacman has been successfully configured!")
			except Exception:
				logger.error(f"Error while configuring pacman: {traceback.format_exc()}")
		else:
			logger.warning("Pacman configuration skipped... (file not found)")
