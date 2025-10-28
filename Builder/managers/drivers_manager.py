import subprocess
import traceback
from typing import List, Optional

from loguru import logger

from utils.mkinitcpio_config import MkinitcpioConfigEditor, Position


class DriversManager:
    @staticmethod
    def get_gpu_vendor() -> str:
        error_msg = "Error processing GPU vendor: {err}"

        try:
            output = subprocess.check_output(
                "lspci | grep -E 'VGA|3D'", shell=True
            ).decode()
            if "NVIDIA" in output:
                return "Nvidia"
            elif "AMD" in output:
                return "AMD"
            elif "Intel" in output:
                return "Intel"
        except subprocess.CalledProcessError as e:
            logger.error(error_msg.format(err=e.stderr))
        except Exception:
            logger.error(error_msg.format(err=traceback.format_exc()))

        return "unknown"

    @staticmethod
    def get_cpu_vendor() -> str:
        error_msg = "Error processing CPU vendor: {err}"

        try:
            output = subprocess.check_output("lscpu", shell=True).decode()
            if "GenuineIntel" in output:
                return "Intel"
            elif "AuthenticAMD" in output:
                return "AMD"
        except subprocess.CalledProcessError as e:
            logger.error(error_msg.format(err=e.stderr))
        except Exception:
            logger.error(error_msg.format(err=traceback.format_exc()))

        return "unknown"

    @staticmethod
    def auto_detection() -> List[str]:
        cpu = DriversManager.get_cpu_vendor()
        gpu = DriversManager.get_gpu_vendor()
        drivers_for = [cpu, gpu]

        if "unknown" in drivers_for:
            drivers_for.remove("unknown")

        return drivers_for

    @staticmethod
    def add_gpu_modules(gpu_type: Optional[str] = None, force: bool = False) -> bool:
        """Добавить модули GPU для ранней загрузки в mkinitcpio
        
        Args:
            gpu_type: Тип GPU ("nvidia", "amd", "intel", None для автодетекта)
            force: Принудительно добавить модули даже если GPU не обнаружен
            
        Returns:
            bool: True если модули были добавлены
        """
        mkinitcpio_editor = MkinitcpioConfigEditor()
        
        # Маппинг между GPU типами и модулями для загрузки
        gpu_modules = {
            "nvidia": ["nvidia", "nvidia_modeset", "nvidia_uvm", "nvidia_drm"],
            "amd": ["amdgpu", "radeon"],
            "intel": ["i915"]
        }
        
        if gpu_type is None:
            gpu_type = DriversManager.get_gpu_vendor().lower()
            
        if gpu_type not in gpu_modules and not force:
            logger.warning(f"GPU type '{gpu_type}' not supported or not detected, skipping GPU modules setup")
            return False
            
        modules_to_add = gpu_modules.get(gpu_type, [])
        if not modules_to_add:
            logger.error(f"Unsupported GPU type: {gpu_type}")
            return False
            
        logger.info(f"Adding {gpu_type.upper()} modules for early boot: {', '.join(modules_to_add)}")
        
        # Добавляем модули в начало для ранней загрузки
        changes_made = mkinitcpio_editor.add_modules(
            modules_to_add, 
            Position.START
        )
        
        if changes_made:
            logger.success(f"{gpu_type.upper()} modules configured for early boot")
        else:
            logger.info(f"{gpu_type.upper()} modules already configured")
            
        return changes_made
    
    @staticmethod
    def setup_gpu_modules_for_early_boot() -> bool:
        """Настроить GPU модули для ранней загрузки
        
        Returns:
            bool: True если были внесены изменения
        """
        logger.info("Setting up GPU modules for early boot...")
        return DriversManager.add_gpu_modules()
