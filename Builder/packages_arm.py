"""
ARM-specific package definitions and exclusions for Meowrch installer.
Defines which packages are incompatible with ARM and provides alternatives.
"""

from utils.schemes import DistributionPackages, PackageInfo, Packages


# Packages that are x86_64 only and should be excluded on ARM
X86_ONLY_PACKAGES = {
    "pacman": [
        "sof-firmware",  # x86 audio firmware
        "steam",  # x86 only
        "gamemode",  # Gaming optimization (x86 only)
        "mangohud",  # Gaming overlay (x86 only)
    ],
    "aur": [
        "visual-studio-code-bin",  # x86 binary
        "portproton",  # Wine-based, x86 only
        "yandex-music",  # x86 binary
        "spotify",  # x86 binary
        "onlyoffice-bin",  # x86 binary
        "vesktop",  # x86 binary (Discord client)
    ]
}

# ARM-specific package alternatives
ARM_ALTERNATIVES = {
    "visual-studio-code-bin": "code",  # OSS version, can be compiled
    # Note: Some alternatives may need to be compiled from AUR
}

# ARM-specific packages to add
ARM_SPECIFIC_PACKAGES = Packages(
    pacman=DistributionPackages(
        common=[
            # Raspberry Pi specific
            "raspberrypi-firmware",  # Only if on Raspberry Pi
            "raspberrypi-bootloader",  # Only if on Raspberry Pi
            
            # ARM video acceleration
            "libva-mesa-driver",
            "mesa-vdpau",
            
            # Additional tools for ARM
            "cpupower",  # CPU frequency management
        ],
        bspwm_packages=[
            # ARM-optimized compositor settings handled in configs
        ],
        hyprland_packages=[
            # Hyprland on ARM may need specific packages
        ]
    ),
    aur=DistributionPackages(
        common=[
            # ARM-specific AUR packages if needed
        ],
        bspwm_packages=[],
        hyprland_packages=[]
    )
)

# Packages that should be excluded on Raspberry Pi specifically
RASPBERRY_PI_EXCLUSIONS = {
    "pacman": [
        "plymouth",  # Boot splash - problematic on RPi
    ],
    "aur": []
}

# Packages that are problematic on all ARM devices
ARM_PROBLEMATIC_PACKAGES = {
    "pacman": [
        "xorg-server-xvfb",  # May have issues on some ARM devices
    ],
    "aur": [
        "hyprprop",  # May not compile on ARM
    ]
}


def filter_packages_for_arm(packages: list[str], package_type: str = "pacman", 
                           is_raspberry_pi: bool = False) -> list[str]:
    """
    Filter out x86-only packages from a package list.
    
    Args:
        packages: List of package names
        package_type: "pacman" or "aur"
        is_raspberry_pi: Whether running on Raspberry Pi
        
    Returns:
        Filtered list of packages compatible with ARM
    """
    excluded = set(X86_ONLY_PACKAGES.get(package_type, []))
    
    if is_raspberry_pi:
        excluded.update(RASPBERRY_PI_EXCLUSIONS.get(package_type, []))
    
    # Also exclude problematic packages
    excluded.update(ARM_PROBLEMATIC_PACKAGES.get(package_type, []))
    
    filtered = [pkg for pkg in packages if pkg not in excluded]
    
    # Apply alternatives
    if package_type == "aur":
        filtered = [ARM_ALTERNATIVES.get(pkg, pkg) for pkg in filtered]
    
    return filtered


def get_arm_specific_packages(is_raspberry_pi: bool = False) -> tuple[list[str], list[str]]:
    """
    Get ARM-specific packages to add.
    
    Args:
        is_raspberry_pi: Whether running on Raspberry Pi
        
    Returns:
        Tuple of (pacman_packages, aur_packages)
    """
    pacman_pkgs = ARM_SPECIFIC_PACKAGES.pacman.common.copy()
    aur_pkgs = ARM_SPECIFIC_PACKAGES.aur.common.copy()
    
    if not is_raspberry_pi:
        # Remove Raspberry Pi specific packages
        pacman_pkgs = [pkg for pkg in pacman_pkgs 
                      if not pkg.startswith("raspberrypi-")]
    
    return pacman_pkgs, aur_pkgs


def should_skip_package_category(category: str, arch_info) -> bool:
    """
    Determine if an entire package category should be skipped.
    
    Args:
        category: Package category name (e.g., "games", "entertainment")
        arch_info: ArchInfo object with architecture details
        
    Returns:
        True if category should be skipped
    """
    # Skip gaming category entirely on ARM
    if category == "games" and arch_info.is_arm:
        return True
    
    # Skip entertainment (streaming apps) on ARM as they're often x86 only
    if category == "entertainment" and arch_info.is_arm:
        return True
    
    return False


# Custom packages that work on ARM
ARM_COMPATIBLE_CUSTOM = {
    "useful": {
        "timeshift": PackageInfo("A system restore utility for Linux", recommended=True)
    },
    "development": {
        "obsidian": PackageInfo("A powerful knowledge base (AppImage works on ARM)", recommended=True),
        "postgresql": PackageInfo("Sophisticated object-relational DBMS", recommended=True),
        "redis": PackageInfo("An in-memory database that persists on disk")
    },
    "social_media": {
        "telegram-desktop": PackageInfo("Popular messenger", recommended=True, selected=True),
        # Discord and Vesktop excluded (x86 only)
    },
    "office": {
        "libreoffice-fresh": PackageInfo("Comprehensive office suite", recommended=True),
        "evince": PackageInfo("Document viewer", selected=True, recommended=True)
    }
}
