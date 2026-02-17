import shutil
import subprocess
from pathlib import Path
from typing import Callable, List, Optional, Set

from loguru import logger

from .grub_config import GrubConfigEditor


class BootloaderManager:
    """Helper for bootloader detection and GRUB-related Plymouth setup steps."""

    def detect_bootloader_type(self) -> str:
        """Detect bootloader: 'grub', 'systemd-boot', or 'unknown'."""
        try:
            if shutil.which("bootctl"):
                try:
                    subprocess.run(
                        ["bootctl", "is-installed"],
                        check=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                    return "systemd-boot"
                except subprocess.CalledProcessError:
                    pass
            if Path("/boot/loader/entries").exists() or Path("/boot/loader/loader.conf").exists():
                return "systemd-boot"
        except Exception:
            pass

        if Path("/etc/default/grub").exists() or Path("/boot/grub").exists() or shutil.which("grub-mkconfig"):
            return "grub"
        return "unknown"

    def configure_grub_cmdline(
        self,
        required_grub_params: Set[str],
        grub_editor: GrubConfigEditor,
        allow_grub_config: bool = True,
        bootloader_type: Optional[str] = None,
    ) -> None:
        """Ensure required kernel parameters are present in GRUB_CMDLINE_LINUX_DEFAULT."""
        logger.info("The process of configuring the settings of GRUB has begun")

        if not allow_grub_config:
            logger.info("Skipping GRUB configuration: user opted out of GRUB installation.")
            return

        effective_bootloader = bootloader_type or self.detect_bootloader_type()
        if effective_bootloader != "grub":
            logger.info("Skipping GRUB configuration: bootloader is not GRUB (likely systemd-boot).")
            return

        if not Path("/etc/default/grub").exists():
            logger.warning("Skipping GRUB configuration: /etc/default/grub not found.")
            return

        changes_made = grub_editor.add_cmdline_params(
            required_grub_params,
            update_grub=False,  # Не запускаем update-grub пока, сделаем в конце
        )

        if changes_made:
            logger.success("GRUB settings configured successfully!")
        else:
            logger.info("All required GRUB parameters are already configured")

    def regenerate_grub_config(
        self,
        run_sudo: Callable[[List[str], Optional[str]], str],
        allow_grub_config: bool = True,
        bootloader_type: Optional[str] = None,
    ) -> None:
        """Regenerate GRUB configuration when system actually uses GRUB."""
        effective_bootloader = bootloader_type or self.detect_bootloader_type()

        if effective_bootloader == "grub" and allow_grub_config:
            if not Path("/boot/grub").exists():
                logger.warning("Skipping GRUB config generation: /boot/grub directory does not exist.")
            elif not shutil.which("grub-mkconfig"):
                logger.warning("Skipping GRUB config generation: grub-mkconfig not found.")
            else:
                logger.info("Running grub-mkconfig -o /boot/grub/grub.cfg...")
                run_sudo(["grub-mkconfig", "-o", "/boot/grub/grub.cfg"])
        elif effective_bootloader == "grub":
            logger.info("Skipping GRUB config generation: user opted out of GRUB installation.")
        else:
            logger.info("Skipping GRUB config generation: system is not using GRUB.")
