from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class AurHelper(Enum):
    YAY = "yay"
    PARU = "paru"
    YAY_BIN = "yay-bin"


class TerminalShell(Enum):
    FISH = "fish"
    ZSH = "zsh"


class Architecture(Enum):
    X86_64 = "x86_64"
    AARCH64 = "aarch64"
    ARMV7L = "armv7l"
    UNKNOWN = "unknown"


class DeviceType(Enum):
    GENERIC_X86 = "generic_x86"
    RASPBERRY_PI_4 = "raspberry_pi_4"
    RASPBERRY_PI_3 = "raspberry_pi_3"
    GENERIC_ARM = "generic_arm"
    UNKNOWN = "unknown"


@dataclass
class ArchInfo:
    """Information about system architecture and capabilities"""
    architecture: Architecture
    device_type: DeviceType
    is_arm: bool
    is_x86: bool
    gpu_type: Optional[str] = None
    supports_hyprland: bool = True
    supports_gaming: bool = True
    supports_proprietary_drivers: bool = True
    
    def __str__(self) -> str:
        return f"{self.architecture.value} ({self.device_type.value})"


@dataclass
class DistributionPackages:
    common: List[str] = field(default_factory=list)
    bspwm_packages: List[str] = field(default_factory=list)
    hyprland_packages: List[str] = field(default_factory=list)


@dataclass
class Packages:
    pacman: DistributionPackages = field(default_factory=DistributionPackages)
    aur: DistributionPackages = field(default_factory=DistributionPackages)


@dataclass
class NotInstalledPackages:
    pacman: List[str] = field(default_factory=list)
    aur: List[str] = field(default_factory=list)


@dataclass
class PackageInfo:
    description: str
    aur: bool = field(default=False, kw_only=True)
    recommended: bool = field(default=False, kw_only=True)
    selected: bool = field(default=False, kw_only=True)


@dataclass
class BuildOptions:
    make_backup: bool
    install_bspwm: bool
    install_hyprland: bool
    aur_helper: AurHelper
    use_chaotic_aur: bool
    ff_darkreader: bool
    ff_ublock: bool
    ff_twp: bool
    ff_unpaywall: bool
    ff_vot: bool
    terminal_shell: TerminalShell
