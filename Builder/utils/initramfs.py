import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Callable, List, Optional

from loguru import logger

from .mkinitcpio_config import MkinitcpioConfigEditor


class InitramfsManager:
    """Helper for detecting and configuring initramfs generators for Plymouth.

    This class encapsulates logic for working with mkinitcpio and dracut so that
    higher-level code (like PlymouthConfigurer) can stay focused on Plymouth
    installation and theming.
    """

    def detect_tool(self, dracut_conf_dir: Path = Path("/etc/dracut.conf.d")) -> str:
        """Detect the initramfs generator in use.

        Preference: dracut when it is configured; otherwise mkinitcpio if present.
        Returns one of: "mkinitcpio", "dracut" or "unknown".
        """
        try:
            mkinitcpio_available = Path("/etc/mkinitcpio.conf").exists() and shutil.which("mkinitcpio")
            dracut_available = shutil.which("dracut")
            dracut_configured = self._dracut_config_present(dracut_conf_dir)

            if dracut_available and (dracut_configured or not mkinitcpio_available):
                return "dracut"
            if mkinitcpio_available:
                return "mkinitcpio"
            if dracut_available:
                return "dracut"
        except Exception:
            # Fallback to unknown if detection fails for any reason
            pass
        return "unknown"

    def _dracut_config_present(self, dracut_conf_dir: Path) -> bool:
        """Check whether dracut has configuration files present."""
        try:
            if Path("/etc/dracut.conf").exists():
                return True
            if dracut_conf_dir.exists():
                # Any file in dracut.conf.d implies dracut is configured/used
                for _ in dracut_conf_dir.iterdir():
                    return True
        except Exception:
            pass
        return False

    def configure_mkinitcpio_for_plymouth(self, mkinitcpio_editor: MkinitcpioConfigEditor) -> None:
        """Configure mkinitcpio hooks and modules for Plymouth.

        This mirrors the previous inline logic from PlymouthConfigurer but is
        encapsulated here for reuse and testability.
        """
        logger.info("The process of configuring the settings of mkinitcpio has begun")

        current_hooks = mkinitcpio_editor.list_hooks()
        logger.info(f"Current hooks: {' '.join(current_hooks)}")

        # Replace udev with systemd if needed
        if "udev" in current_hooks and "systemd" not in current_hooks:
            mkinitcpio_editor.remove_hook("udev")
            mkinitcpio_editor.add_hook("systemd", "start")
            logger.info("Replaced udev with systemd")

        # Refresh hooks after possible changes
        current_hooks = mkinitcpio_editor.list_hooks()

        # If systemd is used, prefer sd-encrypt over encrypt
        if "systemd" in current_hooks and "encrypt" in current_hooks:
            mkinitcpio_editor.remove_hook("encrypt")
            if "sd-encrypt" not in current_hooks:
                mkinitcpio_editor.add_hook("sd-encrypt")
            logger.info("Replaced encrypt with sd-encrypt for systemd")

        # We guarantee that the “base” hook is always the first one.
        if "base" in current_hooks:
            mkinitcpio_editor.remove_hook("base")
            mkinitcpio_editor.add_hook("base", "start")
        else:
            mkinitcpio_editor.add_hook("base", "start")

        plymouth_present = "plymouth" in current_hooks
        if plymouth_present:
            logger.info("Plymouth hook already exists in configuration")

        # Define hooks that should be before plymouth
        before_plymouth_hooks = {
            "base",
            "systemd",
            "autodetect",
            "microcode",
            "modconf",
            "kms",
            "keyboard",
            "keymap",
            "consolefont",
        }

        # Find the last hook from before_plymouth_hooks
        last_before_hook = None
        updated_hooks = mkinitcpio_editor.list_hooks()
        for hook in reversed(updated_hooks):
            if hook in before_plymouth_hooks:
                last_before_hook = hook
                break

        # Find first encrypt hook to ensure plymouth goes before it
        first_encrypt_hook = None
        for hook in updated_hooks:
            if hook in ("encrypt", "sd-encrypt"):
                first_encrypt_hook = hook
                break

        if not plymouth_present:
            # Add plymouth with smart positioning
            if last_before_hook and first_encrypt_hook:
                # Plymouth after last_before_hook but before first_encrypt_hook
                mkinitcpio_editor.add_hook(
                    "plymouth",
                    after_hook=last_before_hook,
                    before_hook=first_encrypt_hook,
                )
                logger.info(
                    f"Added plymouth after {last_before_hook} and before {first_encrypt_hook}"
                )
            elif last_before_hook:
                # Just after last_before_hook
                mkinitcpio_editor.add_hook("plymouth", "after", last_before_hook)
                logger.info(f"Added plymouth after {last_before_hook}")
            elif first_encrypt_hook:
                # Before first_encrypt_hook
                mkinitcpio_editor.add_hook("plymouth", "before", first_encrypt_hook)
                logger.info(f"Added plymouth before {first_encrypt_hook}")
            else:
                # Fallback: add after systemd or at start
                if "systemd" in updated_hooks:
                    mkinitcpio_editor.add_hook("plymouth", "after", "systemd")
                    logger.info("Added plymouth after systemd")
                else:
                    mkinitcpio_editor.add_hook("plymouth", "start")
                    logger.info("Added plymouth at start of hooks list")

        # Ensure required modules for encryption hooks are present
        mkinitcpio_editor.ensure_required_modules_for_hooks()

        logger.success("mkinitcpio settings configured successfully!")

    def configure_dracut_for_plymouth(
        self,
        dracut_conf_dir: Path,
        dracut_conf_file: Path,
        run_sudo: Callable[[List[str], Optional[str]], str],
    ) -> None:
        """Configure dracut to include the plymouth module."""
        logger.info("The process of configuring dracut for plymouth has begun")

        desired_content = (
            "# Generated by meowrch installer for plymouth support\n"
            'add_dracutmodules+=" plymouth "\n'
        )

        existing_content: Optional[str] = None
        try:
            existing_content = run_sudo(["cat", str(dracut_conf_file)])
        except subprocess.CalledProcessError:
            existing_content = None

        if existing_content == desired_content:
            logger.info("Dracut configuration already contains plymouth module")
            return

        run_sudo(["mkdir", "-p", str(dracut_conf_dir)])

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp:
            tmp.write(desired_content)
            tmp.flush()
            run_sudo(["cp", tmp.name, str(dracut_conf_file)])

        logger.success("Dracut settings configured successfully!")

    def detect_initramfs_path(self) -> Path:
        """Best-effort automatic detection of the initramfs image path."""
        # 1. Common defaults
        candidates = [
            Path("/boot/initramfs-linux.img"),
            Path("/boot/initramfs-linux-lts.img"),
        ]
        for candidate in candidates:
            if candidate.exists():
                logger.info(f"Detected initramfs at {candidate}")
                return candidate

        # 2. Try systemd-boot loader entries
        loader_dir = Path("/boot/loader/entries")
        if loader_dir.is_dir():
            for entry in loader_dir.glob("*.conf"):
                lines = entry.read_text(encoding="utf-8", errors="ignore").splitlines()
                for line in lines:
                    line = line.strip()
                    if line.lower().startswith("initrd"):
                        # format: initrd /initramfs-linux.img
                        parts = line.split()
                        if len(parts) >= 2:
                            rel = parts[1]
                            # Assume ESP mounted at /boot
                            path = Path("/boot") / rel.lstrip("/")
                            if path.exists():
                                logger.info(f"Detected initramfs from {entry}: {path}")
                                return path

        raise FileNotFoundError(
            "Could not detect initramfs path automatically. "
            "Please specify it manually or ensure /boot/initramfs-linux.img exists."
        )

    def rebuild_initramfs(
        self,
        tool: Optional[str],
        run_sudo: Callable[[List[str], Optional[str]], str],
        dracut_conf_dir: Path = Path("/etc/dracut.conf.d"),
    ) -> None:
        """Rebuild initramfs for the detected or provided tool."""
        effective_tool = tool or self.detect_tool(dracut_conf_dir)

        if effective_tool == "mkinitcpio":
            logger.info("Running mkinitcpio -P...")
            run_sudo(["mkinitcpio", "-P"])
        elif effective_tool == "dracut":
            try:
                kver = subprocess.run(
                    ["uname", "-r"],
                    text=True,
                    capture_output=True,
                    check=True,
                ).stdout.strip()

                initramfs_path = self.detect_initramfs_path()

                logger.info(f"Running dracut for kernel {kver}...")
                run_sudo(
                    [
                        "dracut",
                        "--kver",
                        kver,
                        str(initramfs_path),
                        "--force",
                    ]
                )
            except subprocess.CalledProcessError as e:
                logger.error(f"dracut failed: {e.stderr or e}")
        else:
            logger.warning("Initramfs tool is unknown; skipping initramfs rebuild.")
