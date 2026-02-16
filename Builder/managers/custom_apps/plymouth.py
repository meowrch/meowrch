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

    def _detect_initramfs_tool(self) -> str:
        """
        Detect the initramfs generator in use.
        Preference: dracut when it is configured; otherwise mkinitcpio if present.
        """
        try:
            mkinitcpio_available = Path("/etc/mkinitcpio.conf").exists() and shutil.which("mkinitcpio")
            dracut_available = shutil.which("dracut")
            dracut_configured = self._dracut_config_present()

            if dracut_available and (dracut_configured or not mkinitcpio_available):
                return "dracut"
            if mkinitcpio_available:
                return "mkinitcpio"
            if dracut_available:
                return "dracut"
        except Exception:
            pass
        return "unknown"
    
    def _dracut_config_present(self) -> bool:
        """Check whether dracut has configuration files present."""
        try:
            if Path("/etc/dracut.conf").exists():
                return True
            if self.dracut_conf_dir.exists():
                # Any file in dracut.conf.d implies dracut is configured/used
                for _ in self.dracut_conf_dir.iterdir():
                    return True
        except Exception:
            pass
        return False

    def update_grub_cmdline(self):
        """Update GRUB_CMDLINE_LINUX_DEFAULT"""
        logger.info("The process of configuring the settings of GRUB has begun")
        if not self.allow_grub_config:
            logger.info("Skipping GRUB configuration: user opted out of GRUB installation.")
            return
        
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

        # Refresh hooks after possible changes
        current_hooks = self.mkinitcpio_editor.list_hooks()

        # If systemd is used, prefer sd-encrypt over encrypt
        if "systemd" in current_hooks and "encrypt" in current_hooks:
            self.mkinitcpio_editor.remove_hook("encrypt")
            if "sd-encrypt" not in current_hooks:
                self.mkinitcpio_editor.add_hook("sd-encrypt")
            logger.info("Replaced encrypt with sd-encrypt for systemd")
        
        # We guarantee that the “base” hook is always the first one.
        if "base" in current_hooks:
            self.mkinitcpio_editor.remove_hook("base")
            self.mkinitcpio_editor.add_hook("base", "start")
        else:
            self.mkinitcpio_editor.add_hook("base", "start")
            
        plymouth_present = "plymouth" in current_hooks
        if plymouth_present:
            logger.info("Plymouth hook already exists in configuration")
        
        # Define hooks that should be before plymouth
        before_plymouth_hooks = {
            "base", "systemd", "autodetect", "microcode", "modconf", 
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
        
        if not plymouth_present:
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

        # Ensure required modules for encryption hooks are present
        self.mkinitcpio_editor.ensure_required_modules_for_hooks()

        logger.success("mkinitcpio settings configured successfully!")


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

    def detect_initramfs_path(self) -> Path:
        # 1. defaults
        candidates = [
            Path("/boot/initramfs-linux.img"),
            Path("/boot/initramfs-linux-lts.img"),
        ]
        for c in candidates:
            if c.exists():
                logger.info(f"Detected initramfs at {c}")
                return c

        # 2. Попытка для systemd-boot: читаем loader entries
        loader_dir = Path("/boot/loader/entries")
        if loader_dir.is_dir():
            for entry in loader_dir.glob("*.conf"):
                lines = entry.read_text(encoding="utf-8", errors="ignore").splitlines()
                for line in lines:
                    line = line.strip()
                    if line.lower().startswith("initrd"):
                        # формат: initrd /initramfs-linux.img
                        parts = line.split()
                        if len(parts) >= 2:
                            rel = parts[1]
                            # предполагаем, что ESP смонтирован в /boot
                            p = Path("/boot") / rel.lstrip("/")
                            if p.exists():
                                logger.info(f"Detected initramfs from {entry}: {p}")
                                return p

        raise FileNotFoundError(
            "Could not detect initramfs path automatically. "
            "Please specify it manually or ensure /boot/initramfs-linux.img exists."
        )
        
    def run_post_commands(self):
        """Run post-installation commands"""
        bootloader = self._bootloader_type()
        logger.info(f"Detected bootloader: {bootloader}")

        # Regenerate bootloader configuration when appropriate
        if bootloader == "grub" and self.allow_grub_config:
            if not Path("/boot/grub").exists():
                logger.warning("Skipping GRUB config generation: /boot/grub directory does not exist.")
            elif not shutil.which("grub-mkconfig"):
                logger.warning("Skipping GRUB config generation: grub-mkconfig not found.")
            else:
                logger.info("Running grub-mkconfig -o /boot/grub/grub.cfg...")
                self._run_sudo(["grub-mkconfig", "-o", "/boot/grub/grub.cfg"])
        elif bootloader == "grub":
            logger.info("Skipping GRUB config generation: user opted out of GRUB installation.")
        else:
            logger.info("Skipping GRUB config generation: system is not using GRUB.")

        # Always rebuild initramfs after changes
        tool = self.initramfs_tool or self._detect_initramfs_tool()
        if tool == "mkinitcpio":
            logger.info("Running mkinitcpio -P...")
            self._run_sudo(["mkinitcpio", "-P"])
        elif tool == "dracut":
            try:
                kver = subprocess.run(
                    ["uname", "-r"],
                    text=True,
                    capture_output=True,
                    check=True,
                ).stdout.strip()

                initramfs_path = self.detect_initramfs_path()

                logger.info(f"Running dracut for kernel {kver}...")
                self._run_sudo([
                    "dracut",
                    "--kver", kver,
                    str(initramfs_path),
                    "--force",
                ])
            except subprocess.CalledProcessError as e:
                logger.error(f"dracut failed: {e.stderr or e}")
        else:
            logger.warning("Initramfs tool is unknown; skipping initramfs rebuild.")

    def update_dracut_config(self):
        """Configure dracut to include plymouth module."""
        logger.info("The process of configuring dracut for plymouth has begun")

        desired_content = (
            "# Generated by meowrch installer for plymouth support\n"
            'add_dracutmodules+=" plymouth "\n'
        )

        existing_content: Optional[str] = None
        try:
            existing_content = self._run_sudo(["cat", str(self.dracut_conf_file)])
        except subprocess.CalledProcessError:
            existing_content = None

        if existing_content == desired_content:
            logger.info("Dracut configuration already contains plymouth module")
            return

        self._run_sudo(["mkdir", "-p", str(self.dracut_conf_dir)])

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp:
            tmp.write(desired_content)
            tmp.flush()
            self._run_sudo(["cp", tmp.name, str(self.dracut_conf_file)])

        logger.success("Dracut settings configured successfully!")
