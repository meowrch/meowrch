from dataclasses import dataclass, field
from enum import Enum
from typing import List


class AurHelper(Enum):
    YAY = "yay"
    PARU = "paru"
    YAY_BIN = "yay-bin"
    PARU_BIN = "paru-bin"


class TerminalShell(Enum):
    FISH = "fish"
    ZSH = "zsh"


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
    install_drivers: bool
    intel_driver: bool
    nvidia_driver: bool
    amd_driver: bool
    ff_darkreader: bool
    ff_ublock: bool
    ff_twp: bool
    ff_unpaywall: bool
    ff_tampermonkey: bool
    terminal_shell: TerminalShell
