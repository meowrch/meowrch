import subprocess
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
    def install() -> bool:
        """Устанавливает Chaotic AUR репозиторий"""
        logger.info("Installing Chaotic AUR repository...")
        
        try:
            logger.info("Setting up Chaotic AUR using official method...")
            
            # Импортируем ключи
            logger.info("Importing PGP keys...")
            subprocess.run([
                "sudo", "pacman-key", "--recv-key", "3056513887B78AEB", "--keyserver", "keyserver.ubuntu.com"
            ], check=True)
            
            subprocess.run([
                "sudo", "pacman-key", "--lsign-key", "3056513887B78AEB"
            ], check=True)
            
            # Устанавливаем keyring и mirrorlist через прямые URL (официальный способ)
            logger.info("Installing keyring and mirrorlist...")
            subprocess.run([
                "sudo", "pacman", "-U", "--noconfirm", 
                "https://cdn-mirror.chaotic.cx/chaotic-aur/chaotic-keyring.pkg.tar.zst",
                "https://cdn-mirror.chaotic.cx/chaotic-aur/chaotic-mirrorlist.pkg.tar.zst"
            ], check=True)
            
            # Добавляем репозиторий в pacman.conf
            ChaoticAurManager._add_to_pacman_conf()
            
            # Обновляем базу данных
            subprocess.run(["sudo", "pacman", "-Sy"], check=True)
            
            logger.success("Chaotic AUR repository installed successfully!")
            return True
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else f"Command failed with exit code {e.returncode}"
            logger.error(f"Error installing Chaotic AUR: {error_msg}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error installing Chaotic AUR: {e}")
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
