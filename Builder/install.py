import os
import inquirer
import traceback
import subprocess
from loguru import logger
from typing import Dict, List, Union
from inquirer.themes import GreenPassion
from inquirer import Checkbox as QuestionCheckbox, List as QuestionList

from packages import BASE, CUSTOM
from managers.drivers_manager import DriversManager
from managers.filesystem_manager import FileSystemManager
from managers.package_manager import PackageManager
from managers.apps_manager import AppsManager
from utils.schemes import BuildOptions
from utils.banner import banner


answers_type = Dict[str, Union[str, List[str]]]


class Builder:
	def run(self) -> None:
		logger.success("The program has been launched successfully. We are starting the survey.")
		self.build_options: BuildOptions = self._questionaire()
		
		FileSystemManager.create_default_folders()
		FileSystemManager.copy_dotfiles(
			remove_bspwm=not self.build_options.install_bspwm,
			remove_hyprland=not self.build_options.install_hyprland
		)

		PackageManager.update_pacman_conf(enable_multilib=self.build_options.enable_multilib)
		PackageManager.install_aur_manager()

		if self.build_options.update_arch_database:
			PackageManager.update_database()

		self.packages_installation()
		self.drivers_installation()

		AppsManager.configure_grub()
		AppsManager.configure_sddm()
		AppsManager.configure_firefox()
		AppsManager.configure_code()

		self.daemons_setting()
		self.patching()

	def packages_installation(self) -> None:
		logger.info("Starting the package installation process")
		pacman, aur = [], []

		for source in [BASE, CUSTOM["games"], CUSTOM["social_media"]]:
			pacman.extend(source.pacman.common)
			aur.extend(source.aur.common)

		for wm in ['bspwm', 'hyprland']:
			if getattr(self.build_options, f'install_{wm}'):
				pacman.extend(getattr(BASE.pacman, f'{wm}_packages'))
				aur.extend(getattr(BASE.aur, f'{wm}_packages'))

				if self.build_options.install_game_depends:
					pacman.extend(getattr(CUSTOM["games"].pacman, wm))
					aur.extend(getattr(CUSTOM["games"].aur, wm))

				if self.build_options.install_social_media_depends:
					pacman.extend(getattr(CUSTOM["social_media"].pacman, wm))
					aur.extend(getattr(CUSTOM["social_media"].aur, wm))

		PackageManager.install_packages(pacman)
		PackageManager.install_packages(aur, aur=True)
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
	
		try:
			subprocess.run(["sudo", "systemctl", "enable", "NetworkManager"], check=True)
			subprocess.run(["sudo", "systemctl", "enable", "bluetooth.service"], check=True)
			subprocess.run(["sudo", "systemctl", "start", "bluetooth.service"], check=True)
			logger.success("The launch of the demons was successful!")
		except Exception:
			logger.error(f"Error starting the demons: {traceback.format_exc()}")

		logger.success("The setting of the daemons is complete!")

	def post_conf(self) -> None:
		logger.info("The post-installation configuration is starting...")
		
		try:
			subprocess.run(["sudo", "chsh", "-s", "/usr/bin/fish"], check=True)
		except Exception:
			logger.error(f"Error changing shell: {traceback.format_exc()}")

		if self.build_options.install_game_depends:
			try:
				username = os.getenv('USER') or os.getenv('LOGNAME')
				subprocess.run(["sudo", "usermod", "-a", "-G", username], check=True)
			except Exception:
				logger.error(f"Error adding user to group for gamemode: {traceback.format_exc()}")

		logger.info("The post-installation configuration is complete!")

	def _questionaire(self) -> BuildOptions:
		drivers = DriversManager.auto_detection()
		answers: answers_type = {}

		quests: List[Union[QuestionCheckbox, QuestionList]] = [
			QuestionCheckbox(
				name='install_wm', message="1) Which window manager do you want to install?",
				choices=["hyprland", "bspwm"], default=["bspwm", "hyprland"], carousel=True
			),
			QuestionList(
				name='enable_multilib', message="2) Should I enable the multilib repository?",
				choices=["Yes", "No"], default="Yes", carousel=True
			),
			QuestionList(
				name='update_arch_database', message="3) Update Arch DataBase?",
				choices=["Yes", "No"], default="Yes", carousel=True
			),
			QuestionList(
				name='install_game_depends', message="4) Install game dependencies?",
				choices=["Yes", "No"], default="Yes", carousel=True
			),
			QuestionList(
				name='install_social_media_depends', message="5) Install social-media dependencies?",
				choices=["Yes", "No"], default="Yes", carousel=True
			),
			QuestionCheckbox(
				name='install_drivers', message="6) What drivers do you want to install?",
				choices=["Nvidia", "Intel", "AMD"], default=drivers, carousel=True
			),
		]

		for question in quests:
			subprocess.run("clear", shell=True)
			print(banner)
			answer = inquirer.prompt([question], theme=GreenPassion())
			answers.update(answer)

		return BuildOptions(
			install_bspwm='bspwm' in answers['install_wm'],
			install_hyrpland='hyprland' in answers['install_wm'],
			enable_multilib=answers['enable_multilib'] == 'Yes',
			update_arch_database=answers['update_arch_database'] == 'Yes',
			install_game_depends=answers['install_game_depends'] == 'Yes',
			install_social_media_depends=answers['install_social_media_depends'] == 'Yes',
			install_drivers=len(answers['install_drivers']) > 0,
			intel_driver='Intel' in answers['install_drivers'],
			nvidia_driver='Nvidia' in answers['install_drivers'],
			amd_driver='AMD' in answers['install_drivers'],
		)


if __name__ == "__main__":
	logger.add(
		sink="build_debug.log",
		format="{time} | {level} | {message}",
		level="DEBUG",
		encoding="utf-8"
	)

	builder = Builder()
	builder.run()
