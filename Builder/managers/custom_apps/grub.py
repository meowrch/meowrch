import subprocess
import traceback
from pathlib import Path

from loguru import logger
from utils.grub_config import GrubConfigEditor

from .base import AppConfigurer


class GrubConfigurer(AppConfigurer):
    def __init__(self):
        self.theme_path = "/boot/grub/themes/meowrch"
        self.theme_src = Path("./misc/grub_theme")
        self.grub_editor = GrubConfigEditor()

    def setup(self) -> None:
        logger.info("Starting the GRUB theme installation process")
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
            
        subprocess.run(
            ["sudo", "cp", "-r", str(self.theme_src), self.theme_path], check=True
        )

    def _update_grub(self) -> None:
        """Update GRUB configuration"""
        subprocess.run(["sudo", "update-grub"], check=True)
        
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
