import os
import subprocess
import tempfile
import traceback
from pathlib import Path
from typing import Callable, Dict, List, Optional

import inquirer
from loguru import logger

from managers.package_manager import PackageManager
from utils.bootloader import BootloaderManager
from utils.gpu_detector import (
    AMD,
    DetectedGpu,
    GpuDetector,
    INTEL,
    NVIDIA,
)
from utils.grub_config import GrubConfigEditor
from utils.initramfs import InitramfsManager
from utils.mkinitcpio_config import MkinitcpioConfigEditor
from utils.schemes import AurHelper


# ---------------------------------------------------------------------------
# NVIDIA installer
# The idea comes from the repository https://github.com/Justus0405/Nvidiainstall
# ---------------------------------------------------------------------------

class NvidiaDriverInstaller:
    """Install and configure NVIDIA drivers for a given driver package."""

    MODPROBE_CONF = Path("/etc/modprobe.d/nvidia.conf")

    # Base userspace/companion packages for each driver branch. Mirrors the
    # package lists from nvidiainstall.sh.
    _COMPANION_PACKAGES = {
        "nvidia-open-dkms": (
            "nvidia-utils", "opencl-nvidia", "nvidia-settings", "libglvnd",
            "lib32-nvidia-utils", "lib32-opencl-nvidia", "egl-wayland",
        ),
        "nvidia-580xx-dkms": (
            "nvidia-580xx-utils", "opencl-nvidia-580xx", "nvidia-580xx-settings",
            "libglvnd", "lib32-nvidia-580xx-utils", "lib32-opencl-nvidia-580xx",
            "egl-wayland",
        ),
        "nvidia-470xx-dkms": (
            "nvidia-470xx-utils", "opencl-nvidia-470xx", "nvidia-470xx-settings",
            "libglvnd", "lib32-nvidia-470xx-utils", "lib32-opencl-nvidia-470xx",
            "egl-wayland",
        ),
        "nvidia-390xx-dkms": (
            "nvidia-390xx-utils", "opencl-nvidia-390xx", "nvidia-390xx-settings",
            "libglvnd", "lib32-nvidia-390xx-utils", "lib32-opencl-nvidia-390xx",
            "egl-wayland",
        ),
        # nvidia-340xx-settings is known to fail to install (man page perms)
        # and the chaotic mirror does not carry the lib32-* variants, so the
        # list is intentionally trimmed.
        "nvidia-340xx-dkms": (
            "nvidia-340xx-utils", "opencl-nvidia-340xx", "libglvnd", "egl-wayland",
        ),
    }

    def __init__(self):
        self.mkinitcpio_editor = MkinitcpioConfigEditor()
        self.grub_editor = GrubConfigEditor()
        self.bootloader_manager = BootloaderManager()
        self.initramfs_manager = InitramfsManager()

    # -- public -------------------------------------------------------------

    def install(
        self,
        gpu_driver: str,
        gpu_gen: str,
        use_chaotic_aur: bool,
        aur_helper: AurHelper,
    ) -> bool:
        """Run the full NVIDIA install/configuration pipeline.

        Returns ``False`` if any step fails; the caller decides whether that
        is fatal. We try to be resilient: package install failures are logged
        but do not abort the configuration steps that follow.
        """
        logger.info(f"Installing NVIDIA driver {gpu_driver} ({gpu_gen})")

        if gpu_driver in ("unsupported", "unidentified", ""):
            logger.error(f"Cannot install NVIDIA driver: {gpu_driver} ({gpu_gen})")
            return False

        try:
            self._install_kernel_headers()
            self._install_driver_packages(gpu_driver, use_chaotic_aur, aur_helper)
            self._configure_mkinitcpio(gpu_driver)
            self._configure_modprobe()
            self._configure_grub()
            self._rebuild_initramfs()
            logger.success(f"NVIDIA driver {gpu_driver} installed and configured")
            return True
        except Exception:
            logger.error(f"NVIDIA driver installation failed:\n{traceback.format_exc()}")
            return False

    # -- steps --------------------------------------------------------------

    def _install_kernel_headers(self) -> None:
        """Install the kernel headers matching the running kernel (dkms needs them)."""
        kernel = os.uname().release
        if "zen" in kernel:
            headers = "linux-zen-headers"
        elif "lts" in kernel:
            headers = "linux-lts-headers"
        elif "hardened" in kernel:
            headers = "linux-hardened-headers"
        else:
            headers = "linux-headers"

        logger.info(f"Detected kernel {kernel}; installing {headers}")
        PackageManager.install_packages([headers])

    def _install_driver_packages(
        self,
        gpu_driver: str,
        use_chaotic_aur: bool,
        aur_helper: AurHelper,
    ) -> None:
        companion = self._COMPANION_PACKAGES.get(gpu_driver, ())
        packages = [gpu_driver] + list(companion)

        # nvidia-open-dkms lives in the official repos; legacy branches live
        # in the AUR. When Chaotic AUR is enabled its binary packages are
        # available through pacman directly, so we only need the AUR helper
        # for the legacy branches without chaotic.
        if gpu_driver == "nvidia-open-dkms" or use_chaotic_aur:
            logger.info(f"Installing {gpu_driver} via pacman")
            PackageManager.install_packages(packages)
        else:
            logger.info(f"Installing {gpu_driver} via AUR helper {aur_helper.value}")
            PackageManager.install_packages(packages, aur=aur_helper)

    def _configure_mkinitcpio(self, gpu_driver: str) -> None:
        """Add NVIDIA modules to MODULES=() for early loading."""
        logger.info("Configuring mkinitcpio NVIDIA modules")
        if gpu_driver == "nvidia-340xx-dkms":
            modules = ["nvidia", "nvidia_uvm"]
        else:
            modules = ["nvidia", "nvidia_modeset", "nvidia_uvm", "nvidia_drm"]
        self.mkinitcpio_editor.add_modules(modules)

    def _configure_modprobe(self) -> None:
        """Write ``options nvidia_drm modeset=1 fbdev=1`` (per Hyprland wiki)."""
        logger.info(f"Configuring {self.MODPROBE_CONF}")
        desired_content = "options nvidia_drm modeset=1 fbdev=1\n"

        try:
            existing = subprocess.run(
                ["sudo", "cat", str(self.MODPROBE_CONF)],
                capture_output=True,
                text=True,
            ).stdout
        except subprocess.CalledProcessError:
            existing = ""

        if existing.strip() == desired_content.strip():
            logger.info("nvidia modprobe already configured")
            return

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp:
            tmp.write(desired_content)
            tmp.flush()
            tmp_path = tmp.name

        try:
            subprocess.run(
                ["sudo", "mkdir", "-p", str(self.MODPROBE_CONF.parent)],
                check=True,
            )
            subprocess.run(["sudo", "cp", tmp_path, str(self.MODPROBE_CONF)], check=True)
            logger.success("nvidia modprobe configured")
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def _configure_grub(self) -> None:
        """Add ``nvidia_drm.modeset=1`` to the kernel command line."""
        self.bootloader_manager.configure_grub_cmdline(
            required_grub_params={"nvidia_drm.modeset=1"},
            grub_editor=self.grub_editor,
            allow_grub_config=True,
        )

    def _rebuild_initramfs(self) -> None:
        """Rebuild the initramfs and regenerate the GRUB config."""
        run_sudo: Callable[[List[str], Optional[str]], str] = NvidiaDriverInstaller._run_sudo
        self.bootloader_manager.regenerate_grub_config(run_sudo=run_sudo)
        self.initramfs_manager.rebuild_initramfs(
            tool=self.initramfs_manager.detect_tool(),
            run_sudo=run_sudo,
        )

    @staticmethod
    def _run_sudo(command: List[str], input: Optional[str] = None) -> str:
        result = subprocess.run(
            ["sudo"] + command,
            input=input,
            text=True,
            capture_output=True,
            check=True,
        )
        return result.stdout

    # -- driver selection prompt -------------------------------------------

    @staticmethod
    def choose_driver_interactively() -> Optional[str]:
        """Ask the user which NVIDIA branch to install when auto-detect fails."""
        choices = [
            ("nvidia-open-dkms", "Turing and newer"),
            ("nvidia-580xx-dkms", "Maxwell, Pascal, Volta"),
            ("nvidia-470xx-dkms", "Kepler"),
            ("nvidia-390xx-dkms", "Fermi"),
            ("nvidia-340xx-dkms", "Tesla"),
        ]

        question = inquirer.List(
            "driver",
            message="Could not identify the NVIDIA GPU. Which driver do you want?",
            choices=[
                f"{pkg}  [{gen}]" for pkg, gen in choices
            ],
            carousel=True,
        )
        answer = inquirer.prompt([question])
        if not answer or not answer.get("driver"):
            return None
        return answer["driver"].split("  ")[0].strip()


# ---------------------------------------------------------------------------
# Intel / AMD installer
# ---------------------------------------------------------------------------

class GenericGpuInstaller:
    """Install userspace drivers for Intel and AMD GPUs.

    These vendors use the unified open-source (mesa/amdgpu/i915) stack that is
    built into the kernel, so there is no kernel-module or mkinitcpio/grub
    configuration to perform; we only install the userspace packages.
    """

    _AMD_PACKAGES = (
        "mesa", "lib32-mesa", "vulkan-radeon", "lib32-vulkan-radeon",
        "mesa-vdpau", "libva-mesa-driver", "lib32-libva-mesa-driver",
        "xf86-video-amdgpu",
    )

    _INTEL_PACKAGES = (
        "mesa", "lib32-mesa", "vulkan-intel", "intel-media-driver",
        "libva-utils",
    )

    @staticmethod
    def install(vendor: str) -> bool:
        if vendor == AMD:
            packages = GenericGpuInstaller._AMD_PACKAGES
        elif vendor == INTEL:
            packages = GenericGpuInstaller._INTEL_PACKAGES
        else:
            logger.error(f"Unsupported vendor for generic GPU install: {vendor}")
            return False

        logger.info(f"Installing {vendor.upper()} userspace GPU packages")
        not_installed = PackageManager.install_packages(list(packages))
        if not_installed:
            logger.warning(
                f"Some {vendor.upper()} packages could not be installed: "
                + ", ".join(not_installed)
            )
        else:
            logger.success(f"{vendor.upper()} GPU packages installed")
        return not not_installed


# ---------------------------------------------------------------------------
# Facade used by install.py
# ---------------------------------------------------------------------------

class GpuDriversManager:
    """Top-level entry point that orchestrates driver installation."""

    def install(self, build_options) -> None:
        """Install drivers for the vendors selected in the survey."""
        logger.info("Starting GPU driver installation")
        detected = GpuDetector.detect_all()
        logger.info(f"Detected GPUs: {detected or 'none'}")

        if build_options.install_nvidia:
            self._install_nvidia(detected, build_options)
        else:
            logger.info("NVIDIA driver installation skipped by user")

        if build_options.install_amd:
            self._install_generic(AMD, detected)
        else:
            logger.info("AMD driver installation skipped by user")

        if build_options.install_intel:
            self._install_generic(INTEL, detected)
        else:
            logger.info("Intel driver installation skipped by user")

    # -- helpers ------------------------------------------------------------

    @staticmethod
    def _install_nvidia(detected: Dict[str, DetectedGpu], build_options) -> None:
        nvidia_gpu = detected.get(NVIDIA)
        if not nvidia_gpu:
            logger.warning(
                "NVIDIA installation requested but no NVIDIA GPU was detected; "
                "skipping"
            )
            return

        gpu_driver, gpu_gen = GpuDetector.detect_nvidia_driver(nvidia_gpu.name)
        logger.info(f"NVIDIA GPU: {nvidia_gpu.name} | {gpu_gen} | {gpu_driver}")

        if gpu_driver == "unsupported":
            logger.error(f"NVIDIA generation {gpu_gen} is no longer supported")
            return

        if gpu_driver == "unidentified":
            logger.warning(
                f"Could not identify NVIDIA driver for '{nvidia_gpu.name}'"
            )
            chosen = NvidiaDriverInstaller.choose_driver_interactively()
            if not chosen:
                logger.warning("No NVIDIA driver selected; skipping")
                return
            gpu_driver = chosen
            gpu_gen = "Manual"

        NvidiaDriverInstaller().install(
            gpu_driver=gpu_driver,
            gpu_gen=gpu_gen,
            use_chaotic_aur=build_options.use_chaotic_aur,
            aur_helper=build_options.aur_helper,
        )

    @staticmethod
    def _install_generic(vendor: str, detected: Dict[str, DetectedGpu]) -> None:
        if not detected.get(vendor):
            logger.warning(
                f"{vendor.upper()} installation requested but no {vendor.upper()} "
                f"GPU was detected; installing userspace packages anyway"
            )
        GenericGpuInstaller.install(vendor)
