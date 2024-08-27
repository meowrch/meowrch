from dataclasses import dataclass, field
from typing import List	


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
class BuildOptions:
	install_bspwm: bool
	install_hyprland: bool
	enable_multilib: bool
	update_arch_database: bool
	install_game_depends: bool
	install_social_media_depends: bool
	install_drivers: bool
	intel_driver: bool
	nvidia_driver: bool
	amd_driver: bool
	