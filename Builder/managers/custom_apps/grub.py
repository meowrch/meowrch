import os
import shutil
import subprocess
import traceback
from pathlib import Path

from loguru import logger
try:
    from Builder.utils.grub_config import GrubConfigEditor
except ImportError:
    from utils.grub_config import GrubConfigEditor

from .base import AppConfigurer


class GrubConfigurer(AppConfigurer):
    def __init__(self):
        self.theme_path = "/boot/grub/themes/meowrch"
        self.theme_src = Path("./misc/grub_theme")
        self.grub_editor = GrubConfigEditor()

    def _bootloader_type(self) -> str:
        """Detect the bootloader type: 'grub', 'systemd-boot', or 'unknown'"""
        try:
            if shutil.which("bootctl"):
                try:
                    subprocess.run(["bootctl", "is-installed"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return "systemd-boot"
                except subprocess.CalledProcessError:
                    pass
            if Path("/boot/loader/entries").exists() or Path("/boot/loader/loader.conf").exists():
                return "systemd-boot"
        except Exception:
            pass
        if Path("/etc/default/grub").exists() or Path("/boot/grub").exists() or shutil.which("grub-mkconfig"):
            return "grub"
        return "unknown"

    def _is_boot_mounted(self) -> bool:
        """Check if /boot is a mounted filesystem"""
        try:
            return os.path.ismount("/boot")
        except Exception:
            return Path("/boot").exists()

    def setup(self) -> None:
        logger.info("Starting the GRUB theme installation process")
        # Skip if this system is not using GRUB
        bootloader = self._bootloader_type()
        if bootloader != "grub":
            logger.info("Skipping GRUB theme installation: bootloader is not GRUB.")
            return
        if not Path("/etc/default/grub").exists():
            logger.error("GRUB is not installed. Skipping theme installation.")
            return

        error_msg = "The installation of the grub theme failed: {err}"

        try:
            self._update_grub_config()
            self._install_theme()
            self._update_grub()
            logger.success("The GRUB theme has been successfully installed!")
        except subprocess.CalledProcessError as e:
            logger.error(error_msg.format(err=e.stderr))
        except Exception:
            logger.error(error_msg.format(err=traceback.format_exc()))

    def _update_grub_config(self) -> None:
        """Update GRUB configuration to use the theme"""
        # Добавляем GRUB_THEME параметр через безопасный редактор
        theme_param = f"GRUB_THEME={self.theme_path}/theme.txt"
        
        # Добавляем параметр как кастомную настройку
        self._add_grub_theme_setting(theme_param)

    def _install_theme(self) -> None:
        """Install GRUB theme files"""
        if not self.theme_src.exists():
            logger.warning("GRUB theme source not found, skipping theme installation")
            return

        # Ensure /boot is mounted and destination exists
        if not self._is_boot_mounted():
            logger.warning("Skipping GRUB theme copy: /boot is not mounted.")
            return
        if not Path("/boot/grub").exists():
            logger.warning("Skipping GRUB theme copy: /boot/grub directory does not exist.")
            return
        dest_dir = Path(self.theme_path).parent
        if not dest_dir.exists():
            logger.warning(f"Skipping GRUB theme copy: destination directory {dest_dir} does not exist.")
            return

        subprocess.run(
            ["sudo", "cp", "-r", str(self.theme_src), self.theme_path], check=True
        )

    def _update_grub(self) -> None:
        """Update GRUB configuration"""
        # Only regenerate if /boot is mounted and grub directory exists
        if not self._is_boot_mounted():
            logger.warning("Skipping GRUB config generation: /boot is not mounted.")
            return
        if not Path("/boot/grub").exists():
            logger.warning("Skipping GRUB config generation: /boot/grub directory does not exist.")
            return

        # Prefer grub-mkconfig, fallback to update-grub if available
        if shutil.which("grub-mkconfig"):
            subprocess.run(["sudo", "grub-mkconfig", "-o", "/boot/grub/grub.cfg"], check=True)
        elif shutil.which("update-grub"):
            subprocess.run(["sudo", "update-grub"], check=True)
        else:
            logger.warning("Skipping GRUB config generation: no grub-mkconfig or update-grub found.")
        
    def _add_grub_theme_setting(self, theme_setting: str) -> None:
        """Add GRUB_THEME setting to configuration file
        
        TODO: Это временное решение, пока GrubConfigEditor не поддерживает 
        произвольные параметры. В идеале нужно расширить GrubConfigEditor.
        """
        grub_config_file = Path("/etc/default/grub")
        
        try:
            # Читаем текущий файл
            content = subprocess.run(
                ["sudo", "cat", str(grub_config_file)],
                capture_output=True,
                text=True,
                check=True
            ).stdout
            
            # Удаляем существующие строки GRUB_THEME
            lines = [line for line in content.splitlines() if not line.startswith("GRUB_THEME")]
            
            # Добавляем новую настройку
            lines.append(theme_setting)
            
            # Записываем обратно через временный файл
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='_grub') as tmp:
                tmp.write('\n'.join(lines) + '\n')
                tmp.flush()
                
                subprocess.run(
                    ["sudo", "cp", tmp.name, str(grub_config_file)], 
                    check=True
                )
                
            Path(tmp.name).unlink(missing_ok=True)
            logger.info(f"Added GRUB theme setting: {theme_setting}")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error updating GRUB theme setting: {e}")
            raise
