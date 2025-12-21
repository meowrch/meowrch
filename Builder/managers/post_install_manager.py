import os
import subprocess
import tempfile
import traceback
from pathlib import Path

from loguru import logger
from packages import CUSTOM
from utils.schemes import TerminalShell


class PostInstallation:
    @staticmethod
    def apply(terminal_shell: TerminalShell = TerminalShell.FISH):
        logger.info("The post-installation configuration is starting...")
        PostInstallation._set_terminal_shell(terminal_shell)
        PostInstallation._add_to_gamemode_group()
        PostInstallation._ensure_en_us_locale()
        PostInstallation._fix_kitty_desktop_icon()
        PostInstallation._set_default_terminal()
        logger.info("The post-installation configuration is complete!")

    @staticmethod
    def _ensure_en_us_locale():
        locale_file = "/etc/locale.gen"
        target_line = "en_US.UTF-8 UTF-8"
        commented_line = f"#{target_line}"
        found = False
        modified = False

        if not os.path.exists(locale_file):
            logger.warning(
                f'Failed to add a locale. Error: file "{locale_file}" not found!'
            )
            return False

        with open(locale_file) as f:
            lines = f.readlines()

        new_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped == commented_line:
                new_lines.append(target_line + "\n")
                modified = True
                found = True
            elif stripped == target_line:
                new_lines.append(line)
                found = True
            else:
                new_lines.append(line)

        if not found:
            new_lines.append(target_line + "\n")
            modified = True

        if modified:
            try:
                with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp_file:
                    tmp_file.writelines(new_lines)
                    tmp_path = tmp_file.name

                subprocess.run(["sudo", "cp", tmp_path, locale_file], check=True)
                os.unlink(tmp_path)

                logger.info("Applying locale-gen....")
                subprocess.run(["sudo", "locale-gen"], check=True)
                logger.success(f'Locale "{target_line}" successfully added!')
                return True
            except subprocess.CalledProcessError as e:
                logger.warning(f"Failed to add a locale. Error: {e.stderr}")
                return False
            except Exception:
                logger.warning(
                    f"Failed to add a locale. Error: {traceback.format_exc()}"
                )
        else:
            logger.success(f'Locale "{target_line}" successfully added!')
            return True

    @staticmethod
    def _set_terminal_shell(terminal_shell: TerminalShell) -> None:
        error_msg = "Error changing shell: {err}"

        try:
            subprocess.run(
                ["chsh", "-s", f"/usr/bin/{terminal_shell.value}"], check=True
            )
            logger.success(f"The shell is changed to {terminal_shell.value}!")
        except subprocess.CalledProcessError as e:
            logger.error(error_msg.format(err=e.stderr))
        except Exception:
            logger.error(error_msg.format(err=traceback.format_exc()))

    @staticmethod
    def _add_to_gamemode_group() -> bool:
        if (
            "games" in CUSTOM
            and "gamemode" in CUSTOM["games"]
            and CUSTOM["games"]["gamemode"].selected
        ):
            error_msg = "Error adding user to group for gamemode: {err}"
            try:
                username = os.getenv("USER") or os.getenv("LOGNAME")
                subprocess.run(
                    ["sudo", "usermod", "-a", username, "-G", "gamemode"], check=True
                )
                logger.success("The user is added to the gamemode group!")
            except subprocess.CalledProcessError as e:
                logger.error(error_msg.format(err=e.stderr))
            except Exception:
                logger.error(error_msg.format(err=traceback.format_exc()))

    @staticmethod
    def _fix_kitty_desktop_icon() -> None:
        """Заменяет $HOME на полный путь пользователя в kitty.desktop файле"""
        kitty_desktop_path = Path.home() / ".local/share/applications/kitty.desktop"
        
        if not kitty_desktop_path.exists():
            logger.warning(f"Kitty desktop file not found at {kitty_desktop_path}")
            return
        
        try:
            # Получаем домашний каталог пользователя
            home_path = str(Path.home())
            
            # Читаем содержимое файла
            with open(kitty_desktop_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Заменяем $HOME на полный путь
            updated_content = content.replace('$HOME', home_path)
            
            # Записываем обновленное содержимое обратно
            if updated_content != content:
                with open(kitty_desktop_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                logger.success(f"Successfully updated kitty.desktop icon path: $HOME -> {home_path}")
            else:
                logger.info("No $HOME variables found in kitty.desktop file")
                
        except Exception as e:
            logger.error(f"Error updating kitty.desktop icon path: {e}")
            logger.error(traceback.format_exc())

    @staticmethod
    def _set_default_terminal() -> None:
        error_msg = "Error changing terminal: {err}"

        try:
            subprocess.run(
                ["gsettings", "set", "org.cinnamon.desktop.default-applications.terminal", "exec", "kitty"], check=True
            )
            logger.success("The terminal is changed to kitty!")
        except subprocess.CalledProcessError as e:
            logger.error(error_msg.format(err=e.stderr))
        except Exception:
            logger.error(error_msg.format(err=traceback.format_exc()))