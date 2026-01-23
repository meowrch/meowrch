"""
Architecture detection utility for Meowrch installer.
Detects CPU architecture and device-specific information.
"""

import platform
import subprocess
from pathlib import Path
from typing import Optional

from loguru import logger
from utils.schemes import ArchInfo, Architecture, DeviceType


class ArchDetector:
    """Detects system architecture and device-specific capabilities"""
    
    @staticmethod
    def get_architecture() -> ArchInfo:
        """
        Detect system architecture and return detailed information.
        
        Returns:
            ArchInfo: Complete architecture information including capabilities
        """
        machine = platform.machine().lower()
        logger.info(f"Detected machine type: {machine}")
        
        # Determine architecture
        if machine == "x86_64" or machine == "amd64":
            arch = Architecture.X86_64
            is_arm = False
            is_x86 = True
        elif machine == "aarch64" or machine == "arm64":
            arch = Architecture.AARCH64
            is_arm = True
            is_x86 = False
        elif machine.startswith("armv7"):
            arch = Architecture.ARMV7L
            is_arm = True
            is_x86 = False
        else:
            logger.warning(f"Unknown architecture: {machine}")
            arch = Architecture.UNKNOWN
            is_arm = False
            is_x86 = False
        
        # Detect device type
        device_type = ArchDetector._detect_device_type(arch)
        
        # Detect GPU
        gpu_type = ArchDetector._detect_gpu(arch)
        
        # Determine capabilities based on architecture
        supports_hyprland = ArchDetector._check_hyprland_support(arch, device_type)
        supports_gaming = is_x86  # Gaming (Steam, etc.) only on x86_64
        supports_proprietary_drivers = is_x86  # NVIDIA/AMD drivers only on x86_64
        
        arch_info = ArchInfo(
            architecture=arch,
            device_type=device_type,
            is_arm=is_arm,
            is_x86=is_x86,
            gpu_type=gpu_type,
            supports_hyprland=supports_hyprland,
            supports_gaming=supports_gaming,
            supports_proprietary_drivers=supports_proprietary_drivers
        )
        
        logger.info(f"Architecture detected: {arch_info}")
        return arch_info
    
    @staticmethod
    def _detect_device_type(arch: Architecture) -> DeviceType:
        """Detect specific device type, especially for ARM devices"""
        
        if arch == Architecture.X86_64:
            return DeviceType.GENERIC_X86
        
        # Check for Raspberry Pi
        if arch in [Architecture.AARCH64, Architecture.ARMV7L]:
            # Check /proc/device-tree/model for Raspberry Pi
            model_file = Path("/proc/device-tree/model")
            if model_file.exists():
                try:
                    model = model_file.read_text().strip('\x00').lower()
                    logger.debug(f"Device model: {model}")
                    
                    if "raspberry pi 4" in model:
                        return DeviceType.RASPBERRY_PI_4
                    elif "raspberry pi 3" in model:
                        return DeviceType.RASPBERRY_PI_3
                except Exception as e:
                    logger.warning(f"Could not read device model: {e}")
            
            return DeviceType.GENERIC_ARM
        
        return DeviceType.UNKNOWN
    
    @staticmethod
    def _detect_gpu(arch: Architecture) -> Optional[str]:
        """Detect GPU type"""
        
        if arch == Architecture.X86_64:
            # Try to detect x86 GPU
            try:
                result = subprocess.run(
                    ["lspci"], 
                    capture_output=True, 
                    text=True, 
                    timeout=5
                )
                output = result.stdout.lower()
                
                if "nvidia" in output:
                    return "NVIDIA"
                elif "amd" in output or "radeon" in output:
                    return "AMD"
                elif "intel" in output:
                    return "Intel"
            except Exception as e:
                logger.debug(f"Could not detect GPU via lspci: {e}")
        
        elif arch in [Architecture.AARCH64, Architecture.ARMV7L]:
            # Check for Raspberry Pi VideoCore
            if Path("/dev/vchiq").exists() or Path("/dev/vcio").exists():
                return "VideoCore"
            
            # Check for Mali GPU
            if Path("/dev/mali0").exists():
                return "Mali"
        
        return None
    
    @staticmethod
    def _check_hyprland_support(arch: Architecture, device_type: DeviceType) -> bool:
        """
        Check if Hyprland is supported on this architecture/device.
        
        Hyprland can be challenging on ARM devices due to GPU driver requirements.
        """
        if arch == Architecture.X86_64:
            return True
        
        # Raspberry Pi 4 can run Hyprland but may have performance issues
        if device_type == DeviceType.RASPBERRY_PI_4:
            logger.warning(
                "Hyprland on Raspberry Pi 4 may have performance issues. "
                "BSPWM is recommended for better performance."
            )
            return True  # Allow but warn
        
        # Other ARM devices - depends on GPU support
        if arch == Architecture.AARCH64:
            return True  # Allow, but user should test
        
        # ARMv7 typically doesn't have good Wayland support
        if arch == Architecture.ARMV7L:
            logger.warning("Hyprland is not recommended on ARMv7 devices")
            return False
        
        return False
    
    @staticmethod
    def is_arm() -> bool:
        """Quick check if running on ARM architecture"""
        machine = platform.machine().lower()
        return machine in ["aarch64", "arm64"] or machine.startswith("armv")
    
    @staticmethod
    def is_x86() -> bool:
        """Quick check if running on x86_64 architecture"""
        machine = platform.machine().lower()
        return machine in ["x86_64", "amd64"]
    
    @staticmethod
    def is_raspberry_pi() -> bool:
        """Quick check if running on Raspberry Pi"""
        model_file = Path("/proc/device-tree/model")
        if model_file.exists():
            try:
                model = model_file.read_text().strip('\x00').lower()
                return "raspberry pi" in model
            except Exception:
                pass
        return False
    
    @staticmethod
    def print_architecture_info():
        """Print detailed architecture information for debugging"""
        arch_info = ArchDetector.get_architecture()
        
        print("\n" + "="*60)
        print("MEOWRCH ARCHITECTURE DETECTION")
        print("="*60)
        print(f"Architecture:        {arch_info.architecture.value}")
        print(f"Device Type:         {arch_info.device_type.value}")
        print(f"GPU Type:            {arch_info.gpu_type or 'Unknown'}")
        print(f"Is ARM:              {arch_info.is_arm}")
        print(f"Is x86_64:           {arch_info.is_x86}")
        print(f"Supports Hyprland:   {arch_info.supports_hyprland}")
        print(f"Supports Gaming:     {arch_info.supports_gaming}")
        print(f"Supports Prop. Drivers: {arch_info.supports_proprietary_drivers}")
        print("="*60 + "\n")


if __name__ == "__main__":
    # Test the detector
    ArchDetector.print_architecture_info()
