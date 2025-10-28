import shutil
import subprocess
import tempfile
import traceback
from pathlib import Path
from typing import List, Optional

from loguru import logger
try:
    from Builder.utils.grub_config import GrubConfigEditor
    from Builder.utils.mkinitcpio_config import MkinitcpioConfigEditor
except ImportError:
    from utils.grub_config import GrubConfigEditor
    from utils.mkinitcpio_config import MkinitcpioConfigEditor

class PlymouthConfigurer:
    def __init__(self):
        self.theme_name = "meowrch"
        self.services_src = Path("./misc/services")
        self.theme_src = Path("./misc/plymouth_theme")
        self.theme_dest = Path("/usr/share/plymouth/themes/")
        
        # Инициализируем редакторы конфигурации
        self.grub_editor = GrubConfigEditor()
        self.mkinitcpio_editor = MkinitcpioConfigEditor()
        
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
                self.update_grub_cmdline()
                self.update_mkinitcpio_hooks()
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
        """Detect the bootloader type: 'grub', 'systemd-boot', or 'unknown'"""
        try:
            if shutil.which("bootctl"):
                try:
                    subprocess.run(["bootctl", "is-installed"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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

    def update_grub_cmdline(self):
        """Update GRUB_CMDLINE_LINUX_DEFAULT"""
        logger.info("The process of configuring the settings of GRUB has begun")
        # Skip if not a GRUB system
        if self._bootloader_type() != "grub":
            logger.info("Skipping GRUB configuration: bootloader is not GRUB (likely systemd-boot).")
            return
        # Ensure the GRUB config file exists
        if not Path("/etc/default/grub").exists():
            logger.warning("Skipping GRUB configuration: /etc/default/grub not found.")
            return
        changes_made = self.grub_editor.add_cmdline_params(
            self.required_grub_params, 
            update_grub=False  # Не запускаем update-grub пока, сделаем в конце
        )
        if changes_made:
            logger.success("GRUB settings configured successfully!")
        else:
            logger.info("All required GRUB parameters are already configured")

    def update_mkinitcpio_hooks(self):
        """Update hooks with proper plymouth placement using our new utilities"""
        logger.info("The process of configuring the settings of mkinitcpio has begun")
        
        current_hooks = self.mkinitcpio_editor.list_hooks()
        logger.info(f"Current hooks: {' '.join(current_hooks)}")
        
        # Replace udev with systemd if needed
        if "udev" in current_hooks and "systemd" not in current_hooks:
            self.mkinitcpio_editor.remove_hook("udev")
            self.mkinitcpio_editor.add_hook("systemd", "start")
            logger.info("Replaced udev with systemd")
        
        # Check if plymouth already exists
        if "plymouth" in current_hooks:
            logger.info("Plymouth hook already exists in configuration")
            return
        
        # Define hooks that should be before plymouth
        before_plymouth_hooks = {
            "systemd", "autodetect", "microcode", "modconf", 
            "kms", "keyboard", "keymap", "consolefont"
        }
        
        # Find the last hook from before_plymouth_hooks
        last_before_hook = None
        updated_hooks = self.mkinitcpio_editor.list_hooks()
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
        
        # Add plymouth with smart positioning
        if last_before_hook and first_encrypt_hook:
            # Plymouth after last_before_hook but before first_encrypt_hook
            self.mkinitcpio_editor.add_hook("plymouth", 
                                          after_hook=last_before_hook, 
                                          before_hook=first_encrypt_hook)
            logger.info(f"Added plymouth after {last_before_hook} and before {first_encrypt_hook}")
        elif last_before_hook:
            # Just after last_before_hook
            self.mkinitcpio_editor.add_hook("plymouth", "after", last_before_hook)
            logger.info(f"Added plymouth after {last_before_hook}")
        elif first_encrypt_hook:
            # Before first_encrypt_hook
            self.mkinitcpio_editor.add_hook("plymouth", "before", first_encrypt_hook)
            logger.info(f"Added plymouth before {first_encrypt_hook}")
        else:
            # Fallback: add after systemd or at start
            if "systemd" in updated_hooks:
                self.mkinitcpio_editor.add_hook("plymouth", "after", "systemd")
                logger.info("Added plymouth after systemd")
            else:
                self.mkinitcpio_editor.add_hook("plymouth", "start")
                logger.info("Added plymouth at start of hooks list")
        
        logger.success("mkinitcpio settings configured successfully!")


    def setup_services(self):
        """Install and configure services"""
        # Copy service files
        logger.info("The process of setup the services for plymouth has begun...")
        service_files = [
            ("sddm-plymouth.service", "/etc/systemd/system/"),
            ("plymouth-wait-for-animation.service", "/etc/systemd/system/"),
        ]

        for src_name, dest_dir in service_files:
            src = self.services_src / src_name
            dest = Path(dest_dir) / src_name

            if not src.exists():
                raise FileNotFoundError(f"Service file {src} not found")

            self._run_sudo(["cp", str(src), str(dest)])

        # Manage services
        self._run_sudo(["systemctl", "disable", "sddm.service"])
        self._run_sudo(["systemctl", "enable", "sddm-plymouth.service"])
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
        if bootloader == "grub":
            if not Path("/boot/grub").exists():
                logger.warning("Skipping GRUB config generation: /boot/grub directory does not exist.")
            elif not shutil.which("grub-mkconfig"):
                logger.warning("Skipping GRUB config generation: grub-mkconfig not found.")
            else:
                logger.info("Running grub-mkconfig -o /boot/grub/grub.cfg...")
                self._run_sudo(["grub-mkconfig", "-o", "/boot/grub/grub.cfg"])
        else:
            logger.info("Skipping GRUB config generation: system is not using GRUB.")

        # Always rebuild initramfs after changes
        logger.info("Running mkinitcpio -P...")
        self._run_sudo(["mkinitcpio", "-P"])
