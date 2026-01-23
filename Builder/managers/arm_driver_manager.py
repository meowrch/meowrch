"""
ARM-specific driver manager for Meowrch installer.
Handles driver installation and configuration for ARM devices, especially Raspberry Pi.
"""

import subprocess
from pathlib import Path
from loguru import logger
from utils.schemes import DeviceType, ArchInfo


class ArmDriverManager:
    """Manages ARM-specific driver installation and configuration"""
    
    def __init__(self, arch_info: ArchInfo):
        self.arch_info = arch_info
        self.is_raspberry_pi = arch_info.device_type in [
            DeviceType.RASPBERRY_PI_3, 
            DeviceType.RASPBERRY_PI_4
        ]
    
    def install(self) -> bool:
        """
        Install and configure ARM-specific drivers.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("Starting ARM driver installation and configuration")
        
        try:
            if self.is_raspberry_pi:
                self._configure_raspberry_pi()
            else:
                self._configure_generic_arm()
            
            logger.success("ARM driver configuration completed")
            return True
            
        except Exception as e:
            logger.error(f"ARM driver configuration failed: {e}")
            return False
    
    def _configure_raspberry_pi(self):
        """Configure Raspberry Pi specific drivers and settings"""
        logger.info("Configuring Raspberry Pi drivers...")
        
        # Check if we're actually on Raspberry Pi OS or Arch ARM
        boot_config = Path("/boot/config.txt")
        firmware_config = Path("/boot/firmware/config.txt")
        
        config_file = None
        if boot_config.exists():
            config_file = boot_config
        elif firmware_config.exists():
            config_file = firmware_config
        
        if config_file:
            logger.info(f"Found boot config at: {config_file}")
            self._update_boot_config(config_file)
        else:
            logger.warning("Boot config not found - skipping boot configuration")
        
        # Configure GPU memory
        self._configure_gpu_memory()
        
        # Enable hardware video acceleration
        self._enable_video_acceleration()
    
    def _configure_generic_arm(self):
        """Configure generic ARM device drivers"""
        logger.info("Configuring generic ARM drivers...")
        
        # Generic ARM configuration
        # Most ARM devices will work with default Mesa drivers
        logger.info("Using default Mesa drivers for ARM GPU")
    
    def _update_boot_config(self, config_file: Path):
        """
        Update Raspberry Pi boot configuration for optimal performance.
        
        Args:
            config_file: Path to config.txt
        """
        logger.info("Updating boot configuration for optimal performance...")
        
        try:
            # Read existing config
            with open(config_file, 'r') as f:
                config = f.read()
            
            # Backup original config
            backup_file = config_file.with_suffix('.txt.meowrch-backup')
            if not backup_file.exists():
                subprocess.run(
                    ["sudo", "cp", str(config_file), str(backup_file)],
                    check=True
                )
                logger.info(f"Backup created: {backup_file}")
            
            # Settings to add/modify
            settings = {
                "gpu_mem": "256",  # Allocate 256MB to GPU (good for 8GB model)
                "dtoverlay": "vc4-kms-v3d",  # Enable KMS driver for better Wayland support
                "max_framebuffers": "2",  # Support for multiple displays
            }
            
            # Check if Meowrch section already exists
            if "[meowrch]" not in config:
                config += "\n\n# Meowrch optimizations\n[meowrch]\n"
                for key, value in settings.items():
                    config += f"{key}={value}\n"
                
                # Write updated config
                proc = subprocess.Popen(
                    ["sudo", "tee", str(config_file)],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.DEVNULL,
                    text=True
                )
                proc.communicate(input=config)
                
                if proc.returncode == 0:
                    logger.success("Boot configuration updated")
                else:
                    logger.error("Failed to update boot configuration")
            else:
                logger.info("Meowrch boot configuration already present")
                
        except Exception as e:
            logger.error(f"Failed to update boot config: {e}")
    
    def _configure_gpu_memory(self):
        """Configure GPU memory allocation"""
        logger.info("GPU memory configuration handled in boot config")
    
    def _enable_video_acceleration(self):
        """Enable hardware video acceleration"""
        logger.info("Enabling hardware video acceleration...")
        
        # For Raspberry Pi, video acceleration is handled by:
        # 1. Mesa drivers (already in package list)
        # 2. libva-mesa-driver (already in ARM packages)
        # 3. Proper VC4/V3D drivers (enabled in boot config)
        
        # Verify video group exists and user will be added
        try:
            result = subprocess.run(
                ["getent", "group", "video"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                logger.info("Video group exists - user will have access to GPU")
            else:
                logger.warning("Video group not found - may need manual configuration")
        except Exception as e:
            logger.debug(f"Could not check video group: {e}")
        
        logger.success("Video acceleration configuration complete")
    
    @staticmethod
    def print_post_install_info():
        """Print post-installation information for ARM users"""
        print("\n" + "="*60)
        print("ARM DRIVER CONFIGURATION COMPLETE")
        print("="*60)
        print("Post-installation notes:")
        print("  1. Reboot required for driver changes to take effect")
        print("  2. GPU acceleration should work out of the box")
        print("  3. For Raspberry Pi: Check /boot/config.txt for settings")
        print("  4. If you experience issues, check:")
        print("     - dmesg | grep drm")
        print("     - glxinfo | grep renderer")
        print("="*60 + "\n")


if __name__ == "__main__":
    # Test the driver manager
    from utils.arch_detector import ArchDetector
    
    arch_info = ArchDetector.get_architecture()
    if arch_info.is_arm:
        manager = ArmDriverManager(arch_info)
        manager.install()
        ArmDriverManager.print_post_install_info()
    else:
        print("Not running on ARM architecture")
