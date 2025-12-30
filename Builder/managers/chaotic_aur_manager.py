import subprocess
import time
from loguru import logger


class ChaoticAurManager:
    """Менеджер для работы с Chaotic AUR - неофициальным репозиторием с бинарными AUR пакетами"""
    
    @staticmethod
    def is_installed() -> bool:
        """Проверяет, установлен ли Chaotic AUR"""
        try:
            with open('/etc/pacman.conf', 'r') as f:
                content = f.read()
                return '[chaotic-aur]' in content
        except Exception:
            return False
    
    @staticmethod
    def install(max_retries: int = 3) -> bool:
        """Устанавливает Chaotic AUR репозиторий"""
        logger.info("Installing Chaotic AUR repository...")
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Attempt {attempt + 1}/{max_retries} to install Chaotic AUR...")
                
                # Импортируем ключи
                logger.info("Importing PGP keys...")
                subprocess.run([
                    "sudo", "pacman-key", "--recv-key", "3056513887B78AEB", "--keyserver", "keyserver.ubuntu.com"
                ], check=True, timeout=60)
                
                subprocess.run([
                    "sudo", "pacman-key", "--lsign-key", "3056513887B78AEB"
                ], check=True, timeout=60)
                
                # Пробуем разные зеркала
                mirrors = [
                    "https://cdn-mirror.chaotic.cx/chaotic-aur",
                    "https://mirror.chaotic.cx/chaotic-aur",
                    "https://lonewolf-builder.chaotic.cx"
                ]
                
                for mirror in mirrors:
                    try:
                        logger.info(f"Trying mirror: {mirror}")
                        subprocess.run([
                            "sudo", "pacman", "-U", "--noconfirm", 
                            f"{mirror}/chaotic-keyring.pkg.tar.zst",
                            f"{mirror}/chaotic-mirrorlist.pkg.tar.zst"
                        ], check=True, timeout=120)
                        logger.success(f"Successfully used mirror: {mirror}")
                        break
                    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                        logger.warning(f"Mirror {mirror} failed, trying next...")
                        continue
                else:
                    logger.error("All mirrors failed!")
                    return False
                
                # Добавляем репозиторий в pacman.conf
                ChaoticAurManager._add_to_pacman_conf()
                
                # Обновляем базу данных
                subprocess.run(["sudo", "pacman", "-Sy"], check=True, timeout=60)
                
                logger.success("Chaotic AUR repository installed successfully!")
                return True
                
            except subprocess.TimeoutExpired:
                logger.warning(f"Timeout occurred on attempt {attempt + 1}")
                if attempt < max_retries - 1:
                    logger.info("Waiting 5 seconds before retry...")
                    time.sleep(5)
                continue
                
            except subprocess.CalledProcessError as e:
                error_msg = e.stderr if e.stderr else f"Command failed with exit code {e.returncode}"
                logger.error(f"Error installing Chaotic AUR (attempt {attempt + 1}): {error_msg}")
                if attempt < max_retries - 1:
                    logger.info("Waiting 5 seconds before retry...")
                    time.sleep(5)
                continue
                
            except Exception as e:
                logger.error(f"Unexpected error installing Chaotic AUR: {e}")
                return False
        
        logger.error(f"Failed to install Chaotic AUR after {max_retries} attempts")
        return False
    
    @staticmethod
    def _add_to_pacman_conf() -> None:
        """Добавляет Chaotic AUR в /etc/pacman.conf"""
        pacman_conf_path = "/etc/pacman.conf"
        temp_path = "/tmp/meowrch-pacman-chaotic.conf"
        
        chaotic_section = """
# Chaotic AUR - Binary AUR packages
[chaotic-aur]
Include = /etc/pacman.d/chaotic-mirrorlist
"""
        
        try:
            with open(pacman_conf_path, 'r') as f:
                content = f.read()
            
            # Проверяем, что Chaotic AUR еще не добавлен
            if '[chaotic-aur]' not in content:
                # Добавляем в конец файла
                content += chaotic_section
                
                with open(temp_path, 'w') as f:
                    f.write(content)
                
                subprocess.run([
                    "sudo", "mv", temp_path, pacman_conf_path
                ], check=True)
                
                logger.info("Chaotic AUR section added to pacman.conf")
            else:
                logger.info("Chaotic AUR already present in pacman.conf")
                
        except Exception as e:
            logger.error(f"Error updating pacman.conf: {e}")
            raise