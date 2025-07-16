import subprocess
import traceback
from pathlib import Path

from loguru import logger

from .base import AppConfigurer


class SDDMConfigurer(AppConfigurer):
    def __init__(self):
        self.theme_name = "meowrch"
        self.sddm_config_file = "/etc/sddm.conf"
        self.temp_config_path = "/tmp/sddm.conf"
        self.theme_path = f"/usr/share/sddm/themes/{self.theme_name}"

    def setup(self) -> None:
        logger.info("Starting the SDDM installation process")
        error_msg = "The installation of the SDDM theme failed: {err}"
        try:
            self._create_config()
            self._install_theme()
            self.granting_permissions()
            logger.success("The SDDM theme has been successfully installed!")
        except subprocess.CalledProcessError as e:
            logger.error(error_msg.format(err=e.stderr))
        except Exception:
            logger.error(error_msg.format(err=traceback.format_exc()))

    def _create_config(self) -> None:
        config_content = (
            "[Theme]\n"
            f"Current={self.theme_name}\n"
            "FacesDir=/var/lib/AccountsService/icons/\n"
            "CursorTheme=Bibata-Modern-Classic\n"
            "DefaultSession=hyprland-uwsm.desktop\n"
        )
        with open(self.temp_config_path, "w") as f:
            f.write(config_content)

        subprocess.run(
            ["sudo", "mv", self.temp_config_path, self.sddm_config_file], check=True
        )

    def _install_theme(self) -> None:
        subprocess.run(
            ["sudo", "cp", "-r", "./misc/sddm_theme", self.theme_path], check=True
        )

    def granting_permissions(self) -> None:
        ##==> Выдаем права sddm
        ##############################################
        error_msg = "[!] An error occurred when granting permissions for sddm: {err}"

        face_icon = Path.home() / ".face.icon"
        face_icon.touch(exist_ok=True)

        try:
            commands = [
                ["setfacl", "-m", "u:sddm:x", str(Path.home())],
                ["setfacl", "-m", "u:sddm:r", str(face_icon)]
            ]
            
            for cmd in commands:
                subprocess.run(
                    ["sudo"] + cmd,
                    check=True,
                    capture_output=True,
                    text=True,
                    shell=False
                )
        except subprocess.CalledProcessError as e:
            logger.error(error_msg.format(err=e.stderr))
        except Exception:
            logger.error(error_msg.format(err=traceback.format_exc()))
