import os
from logger import Logger, LoggerStatus


class AurBuilder:
    @staticmethod
    def build():
        os.system("git -C /tmp clone https://aur.archlinux.org/yay.git")
        os.system("cd /tmp/yay && makepkg -si")


class FirefoxCustomize:
    @staticmethod
    def build():
        os.system("timeout 10 firefox --headless")
        os.system("sh ./misc/apps/firefox/install.sh")
        Logger.add_record("[+] Firefox styles installed", status=LoggerStatus.SUCCESS)
