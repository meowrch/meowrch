import shutil
import subprocess
import tempfile
import traceback
from pathlib import Path
from typing import List, Optional

from loguru import logger
try:
    from Builder.utils.bootloader import BootloaderManager
    from Builder.utils.grub_config import GrubConfigEditor
    from Builder.utils.mkinitcpio_config import MkinitcpioConfigEditor
    from Builder.utils.initramfs import InitramfsManager
except ImportError:
    from utils.bootloader import BootloaderManager
    from utils.grub_config import GrubConfigEditor
    from utils.mkinitcpio_config import MkinitcpioConfigEditor
    from utils.initramfs import InitramfsManager

class PlymouthConfigurer:
    def __init__(self, allow_grub_config: bool = True):
        self.theme_name = "meowrch"
        self.services_src = Path("./misc/services")
        self.theme_src = Path("./misc/plymouth_theme")
        self.theme_dest = Path("/usr/share/plymouth/themes/")
        self.allow_grub_config = allow_grub_config
        self.initramfs_tool: Optional[str] = None
        self.dracut_conf_dir = Path("/etc/dracut.conf.d")
        self.dracut_conf_file = self.dracut_conf_dir / "90-plymouth-meowrch.conf"
        
        # Инициализируем редакторы конфигурации
        self.grub_editor = GrubConfigEditor()
        self.mkinitcpio_editor = MkinitcpioConfigEditor()
        self.bootloader_manager = BootloaderManager()
        self.initramfs_manager = InitramfsManager()
        
        # Требуемые параметры GRUB
        self.required_grub_params = {
            "quiet",
            "loglevel=3",
            "splash",
            "vt.global_cursor_default=0",
            "systemd.show_status=auto",
            "rd.udev.log_level=3",
        }

    def setup(self) -> None:
        """Main setup method"""
        error_msg = "An error occurred during the installation of plymouth: {err}"
        if self._check_plymouth_installed():
            try:
                self.initramfs_tool = self._detect_initramfs_tool()
                logger.info(f"Detected initramfs tool: {self.initramfs_tool}")
                self.update_grub_cmdline()
                if self.initramfs_tool == "mkinitcpio":
                    self.update_mkinitcpio_hooks()
                elif self.initramfs_tool == "dracut":
                    self.update_dracut_config()
                else:
                    logger.warning("Unknown initramfs generator; skipping initramfs configuration step.")
                self.setup_services()
                self.install_theme()
                self.run_post_commands()
            except subprocess.CalledProcessError as e:
                logger.error(error_msg.format(err=e.stderr))
            except Exception:
                logger.error(error_msg.format(err=traceback.format_exc()))

    def _run_sudo(self, command: List[str], input: Optional[str] = None) -> str:
        """Run command with sudo"""
        result = subprocess.run(
            ["sudo"] + command,
            input=input,
            text=True,
            capture_output=True,
            check=True,
        )
        return result.stdout

    def _check_plymouth_installed(self) -> bool:
        """Check if Plymouth is installed"""
        if not shutil.which("plymouth"):
            logger.error("Plymouth is not installed. Please install it first.")
            return False
        
        return True

    def _bootloader_type(self) -> str:
        """Detect the bootloader type via BootloaderManager."""
        return self.bootloader_manager.detect_bootloader_type()

    def _detect_initramfs_tool(self) -> str:
        """Detect the initramfs generator in use via InitramfsManager."""
        return self.initramfs_manager.detect_tool(self.dracut_conf_dir)

    def update_grub_cmdline(self):
        """Update GRUB_CMDLINE_LINUX_DEFAULT."""
        self.bootloader_manager.configure_grub_cmdline(
            required_grub_params=self.required_grub_params,
            grub_editor=self.grub_editor,
            allow_grub_config=self.allow_grub_config,
            bootloader_type=self._bootloader_type(),
        )

    def update_mkinitcpio_hooks(self):
        """Update hooks with proper plymouth placement using InitramfsManager."""
        self.initramfs_manager.configure_mkinitcpio_for_plymouth(self.mkinitcpio_editor)


    def setup_services(self):
        """Install and configure services"""
        # Copy service files
        logger.info("The process of setup the services for plymouth has begun...")
        service_files = [
            ("plymouth-wait-for-animation.service", "/etc/systemd/system/"),
        ]

        for src_name, dest_dir in service_files:
            src = self.services_src / src_name
            dest = Path(dest_dir) / src_name

            if not src.exists():
                raise FileNotFoundError(f"Service file {src} not found")

            self._run_sudo(["cp", str(src), str(dest)])

        # Manage services
        self._run_sudo(["systemctl", "enable", "plymouth-wait-for-animation.service"])
        logger.success("All services for plymouth successfully enabled! ")

    def install_theme(self):
        """Install Plymouth theme"""
        logger.info("The process of installing the theme for plymouth has begun...")
        if not self.theme_src.exists():
            logger.warning(
                "No theme found in ./misc/plymouth_theme - skipping theme installation"
            )
            return

        dest = self.theme_dest / self.theme_name

        # Create temporary directory
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_dest = Path(tmp_dir) / self.theme_name
            shutil.copytree(self.theme_src, tmp_dest)

            self._run_sudo(["rm", "-rf", str(dest)])
            self._run_sudo(["cp", "-r", str(tmp_dest), str(self.theme_dest)])

        self._run_sudo(["plymouth-set-default-theme", self.theme_name])
        logger.success(f'Installed "{self.theme_name}" Plymouth theme')

    def run_post_commands(self):
        """Run post-installation commands"""
        bootloader = self._bootloader_type()
        logger.info(f"Detected bootloader: {bootloader}")
        # Regenerate bootloader configuration when appropriate
        self.bootloader_manager.regenerate_grub_config(
            run_sudo=self._run_sudo,
            allow_grub_config=self.allow_grub_config,
            bootloader_type=bootloader,
        )

        # Always rebuild initramfs after changes
        self.initramfs_manager.rebuild_initramfs(
            tool=self.initramfs_tool,
            run_sudo=self._run_sudo,
            dracut_conf_dir=self.dracut_conf_dir,
        )

    def update_dracut_config(self):
        """Configure dracut to include plymouth module."""
        self.initramfs_manager.configure_dracut_for_plymouth(
            dracut_conf_dir=self.dracut_conf_dir,
            dracut_conf_file=self.dracut_conf_file,
            run_sudo=self._run_sudo,
        )
