import os
import urllib.request
import shutil
import zipfile
import subprocess
import packages

from logger import Logger, LoggerStatus
from creators.software import AurBuilder, FirefoxCustomize
from creators.drivers import GraphicDrivers
from creators.patches import PatchSystemBugs
from creators.daemons import Daemons


class SystemConfiguration:
    def start(*args):
        start_text = f"[+] Starting assembly. Options {args}"
        Logger.add_record(start_text, status=LoggerStatus.SUCCESS)
        if args[0]: SystemConfiguration.__start_option_1()
        if args[1]: SystemConfiguration.__start_option_2()
        if args[2]: SystemConfiguration.__start_option_3()
        if args[3]: SystemConfiguration.__start_option_4()
        if args[4]: GraphicDrivers.build()
        if args[5]: SystemConfiguration.__start_option_6()

        Daemons.enable_all_daemons()
        PatchSystemBugs.enable_all_patches()

        ##==> Installing a theme for fish
        os.system("fish_config theme save \"Catppuccin Mocha\"")

    @staticmethod
    def __start_option_1():
        SystemConfiguration.__create_default_folders()
        SystemConfiguration.__copy_bspwm_dotfiles()

    @staticmethod
    def __start_option_2():
        Logger.add_record("[+] Updates Enabled", status=LoggerStatus.SUCCESS)
        os.system("sudo pacman -Sy")

    @staticmethod
    def __start_option_3():
        Logger.add_record("[+] Installed BSPWM Dependencies", status=LoggerStatus.SUCCESS)
        AurBuilder.build()
        SystemConfiguration.__install_pacman_package(packages.BASE_PACKAGES)
        SystemConfiguration.__install_aur_package(packages.AUR_PACKAGES)
        FirefoxCustomize.build()

    @staticmethod
    def __start_option_4():
        Logger.add_record("[+] Installed Dev Dependencies", status=LoggerStatus.SUCCESS)
        SystemConfiguration.__install_pacman_package(packages.DEV_PACKAGES)
        SystemConfiguration.__install_aur_package(packages.AUR_DEV_PACKAGES)

    @staticmethod
    def __start_option_6():
        repo_url = "https://github.com/catppuccin/grub/archive/refs/heads/main.zip"
        theme_zip_path = "/tmp/catppuccin-grub-theme.zip"
        extract_to = "/tmp"
        theme_path = "/boot/grub/themes/catppuccin-mocha-grub-theme"
        grub_config_path = "/etc/default/grub"

        try:
            ##==> Скачивание темы
            Logger.add_record("[+] Downloading theme...", status=LoggerStatus.SUCCESS)
            with urllib.request.urlopen(repo_url) as response, open(theme_zip_path, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)

            ##==> Распаковка архива
            Logger.add_record("[+] Unpacking the archive...", status=LoggerStatus.SUCCESS)
            with zipfile.ZipFile(theme_zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)

            ##==> Перемещение темы в нужную папку
            Logger.add_record("[+] Installing theme...", status=LoggerStatus.SUCCESS)
            extracted_theme_path = os.path.join(extract_to, "grub-main/src/catppuccin-mocha-grub-theme")
            subprocess.run(["sudo", "mv", extracted_theme_path, theme_path], check=True)

            if not os.path.exists(theme_path):
                raise Exception("Failed to move theme to the GRUB directory.")

            ##==> Обновление файла конфигурации GRUB
            Logger.add_record("[+] Updating GRUB configuration...", status=LoggerStatus.SUCCESS)

            temp_grub_config_path = "/tmp/grub"

            with open(grub_config_path, 'r') as file:
                grub_config = file.readlines()

            grub_theme_setting = f"GRUB_THEME={theme_path}/theme.txt\n"
            grub_config = [line for line in grub_config if not line.startswith("GRUB_THEME")]
            grub_config.append(grub_theme_setting)

            with open(temp_grub_config_path, 'w') as file:
                file.writelines(grub_config)

            subprocess.run(["sudo", "mv", temp_grub_config_path, grub_config_path], check=True)

            subprocess.run(["sudo", "update-grub"], check=True)
            Logger.add_record("[+] The GRUB theme has been successfully installed!", status=LoggerStatus.SUCCESS)
        except Exception as e:
            Logger.add_record(f"[!] An error occurred: {e}", status=LoggerStatus.ERROR)
            SystemConfiguration.__option_6_rollback_changes(theme_zip_path, theme_path)

    @staticmethod
    def __option_6_rollback_changes(theme_zip_path, theme_path):
        Logger.add_record("[+] Rolling back changes...", status=LoggerStatus.SUCCESS)
        if os.path.exists(theme_zip_path):
            try:
                os.remove(theme_zip_path)
                Logger.add_record("[+] Removed temporary theme zip file.", status=LoggerStatus.SUCCESS)
            except OSError as e:
                Logger.add_record(f"[!] Error removing temporary theme zip file: {e}", status=LoggerStatus.SUCCESS)
        if os.path.exists(theme_path):
            try:
                subprocess.run(["sudo", "rm", "-r", theme_path], check=True)
                Logger.add_record("[+] Removed theme directory.", status=LoggerStatus.SUCCESS)
            except subprocess.CalledProcessError as e:
                Logger.add_record(f"[!] Error removing theme directory: {e}", status=LoggerStatus.SUCCESS)

    @staticmethod
    def __install_pacman_package(package_names: list):
        for package in package_names:
            os.system(f"sudo pacman -S --noconfirm {package}")
            Logger.add_record(f"Installed: {package}", status=LoggerStatus.SUCCESS)

    @staticmethod
    def __install_aur_package(package_names: list):
        for package in package_names:
            os.system(f"yay -S --noconfirm {package}")
            Logger.add_record(f"Installed: {package}", status=LoggerStatus.SUCCESS)

    @staticmethod
    def __create_default_folders():
        Logger.add_record("[+] Create default directories", status=LoggerStatus.SUCCESS)
        default_folders = "~/Videos ~/Pictures ~/Documents ~/Downloads ~/Music ~/Desktop"
        os.system("mkdir -p ~/.config")
        os.system(f"mkdir -p {default_folders}")

    @staticmethod
    def __copy_bspwm_dotfiles():
        Logger.add_record("[+] Copy Dotfiles & GTK", status=LoggerStatus.SUCCESS)
        os.system("cp -r ./home/config/* ~/.config/")
        os.system("cp ./home/Xresources ~/.Xresources")
        os.system("cp ./home/gtkrc-2.0 ~/.gtkrc-2.0")
        os.system("cp -r ./home/themes ~/.themes")
        os.system("cp ./home/xinitrc ~/.xinitrc")
        os.system("cp -r ./home/bin/ ~/")
        os.system("cp -r ./home/Wallpapers/ ~/")
        os.system("mkdir -p ~/.icons/default")
        os.system("cp ./home/icons/default/index.theme ~/.icons/default/index.theme")
