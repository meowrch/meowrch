import os
from logger import Logger, LoggerStatus


class GraphicDrivers:
    @staticmethod
    def build():
        GraphicDrivers.__prepare_multilib()
        GraphicDrivers.__update_multilib_repo()
        GraphicDrivers.__install_hybrid_drivers()

    @staticmethod
    def __install_hybrid_drivers():
        Logger.add_record("[+] Install Nvidia & Intel Drivers", status=LoggerStatus.SUCCESS)
        os.system("sudo pacman -S mesa")
        os.system("sudo pacman -S lib32-mesa")
        os.system("sudo pacman -S xf86-video-nouveau xf86-video-intel vulkan-intel")

    @staticmethod
    def __prepare_multilib():
        Logger.add_record("[+] Prepare Multilib", status=LoggerStatus.SUCCESS)
        os.system(r"sudo sed -i 's/^#\[multilib\]/[multilib]/' /etc/pacman.conf")
        os.system(r"sudo sed -i '/^\[multilib\]$/,/^\[/ s/^#\(Include = \/etc\/pacman\.d\/mirrorlist\)/\1/' /etc/pacman.conf")

    @staticmethod
    def __update_multilib_repo():
        Logger.add_record("[+] Update Multilib Repository", status=LoggerStatus.SUCCESS)
        os.system("sudo pacman -Sl multilib")
        os.system("sudo pacman -Sy")
