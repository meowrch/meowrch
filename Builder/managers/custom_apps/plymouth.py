import re
import shutil
import subprocess
import tempfile
import traceback
from pathlib import Path
from typing import List, Optional

from loguru import logger


class PlymouthConfigurer:
    def __init__(self):
        self.theme_name = "meowrch"
        self.grub_path = Path("/etc/default/grub")
        self.mkinitcpio_path = Path("/etc/mkinitcpio.conf")
        self.services_src = Path("./misc/services")
        self.theme_src = Path("./misc/plymouth_theme")
        self.theme_dest = Path("/usr/share/plymouth/themes/")
        self.required_params = {
            "quiet",
            "loglevel=3",
            "splash",
            "vt.global_cursor_default=0",
            "systemd.show_status=auto",
            "rd.udev.log_level=3",
        }

    def setup(self):
        """Main setup method"""
        if self._check_plymouth_installed():
            try:
                self.update_grub_cmdline()
                self.update_mkinitcpio_hooks()
                self.setup_services()
                self.install_theme()
                self.run_post_commands()
            except Exception as e:
                logger.error(str(e))

    def _run_sudo(self, command: List[str], input: Optional[str] = None) -> str:
        """Run command with sudo"""
        try:
            result = subprocess.run(
                ["sudo"] + command,
                input=input,
                text=True,
                capture_output=True,
                check=True,
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            logger.error(
                f"Command failed: {' '.join(command)}\nError: {traceback.format_exc()}"
            )

    def _check_plymouth_installed(self) -> bool:
        """Check if Plymouth is installed"""
        if not shutil.which("plymouth"):
            logger.error("Plymouth is not installed. Please install it first.")
            return False
        
        return True

    def _safe_file_edit(self, path: Path, edit_callback: callable):
        """Edit file safely using temporary file and sudo"""
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp:
            original_content = self._run_sudo(["cat", str(path)])
            tmp.write(original_content)
            tmp.flush()

            edit_callback(Path(tmp.name))
            if Path(tmp.name).read_text() != original_content:
                self._run_sudo(["cp", tmp.name, str(path)])

    def update_grub_cmdline(self):
        """Update GRUB_CMDLINE_LINUX_DEFAULT"""

        def edit_grub(tmp_path: Path):
            content = tmp_path.read_text()
            match = re.search(r'^GRUB_CMDLINE_LINUX_DEFAULT="(.+?)"', content, re.M)

            if not match:
                logger.error("GRUB_CMDLINE_LINUX_DEFAULT not found")
                return

            current_params = set(match.group(1).split())
            missing_params = self.required_params - current_params

            if missing_params:
                new_params = " ".join(missing_params) + " " + match.group(1)
                new_line = f'GRUB_CMDLINE_LINUX_DEFAULT="{new_params}"'
                content = content.replace(match.group(0), new_line)
                tmp_path.write_text(content)

        logger.info("The process of configuring the settings of GRUB has begun")
        self._safe_file_edit(self.grub_path, edit_grub)
        logger.success("GRUB settings configured successfully!")

    def update_mkinitcpio_hooks(self):
        """Update hooks with proper plymouth placement, including dependency reordering"""

        def edit_mkinitcpio(tmp_path: Path):
            content = tmp_path.read_text()
            match = re.search(r"^HOOKS=\((.*?)\)", content, re.M)

            if not match:
                logger.error("HOOKS not found in mkinitcpio.conf")
                return

            hooks = match.group(1).split()

            # Replace udev with systemd
            hooks = [h if h != "udev" else "systemd" for h in hooks]

            if "plymouth" in hooks:
                return

            # Definition of dependencies
            before_plymouth = {
                "systemd",
                "autodetect",
                "microcode",
                "modconf",
                "kms",
                "keyboard",
                "keymap",
                "consolefont",
            }

            # Find encrypt/sd-encrypt positions
            encrypt_indices = [
                i for i, h in enumerate(hooks) if h in ("encrypt", "sd-encrypt")
            ]
            first_encrypt = encrypt_indices[0] if encrypt_indices else len(hooks)

            # Move all before_plymouth hooks before encrypt
            new_hooks = []
            moved_hooks = set()

            # First add everything up to the first encrypt
            for hook in hooks[:first_encrypt]:
                new_hooks.append(hook)
                if hook in before_plymouth:
                    moved_hooks.add(hook)

            # Adding the missing before_plymobile hooks
            for hook in before_plymouth:
                if hook not in new_hooks and hook in hooks:
                    new_hooks.append(hook)
                    moved_hooks.add(hook)

            # Add encrypt and the rest
            new_hooks.extend(hooks[first_encrypt:])

            # Remove duplicates of before_plymouth after a move
            final_hooks = []
            seen_before = set()
            for hook in new_hooks:
                if hook in before_plymouth:
                    if hook not in seen_before:
                        final_hooks.append(hook)
                        seen_before.add(hook)
                else:
                    final_hooks.append(hook)

            # Insert plymouth after the last before_plymouth
            last_before = max(
                [i for i, h in enumerate(final_hooks) if h in before_plymouth],
                default=-1,
            )

            if last_before != -1:
                insert_pos = last_before + 1
            else:
                # Fallback: after systemd or base
                systemd_index = next(
                    (i for i, h in enumerate(final_hooks) if h == "systemd"), -1
                )
                insert_pos = systemd_index + 1 if systemd_index != -1 else 1

            # Make sure plymouth before encrypt.
            if encrypt_indices:
                first_encrypt_new = next(
                    (
                        i
                        for i, h in enumerate(final_hooks)
                        if h in ("encrypt", "sd-encrypt")
                    ),
                    len(final_hooks),
                )
                insert_pos = min(insert_pos, first_encrypt_new)

            final_hooks.insert(insert_pos, "plymouth")

            new_hooks_str = f"HOOKS=({' '.join(final_hooks)})"
            tmp_path.write_text(content.replace(match.group(0), new_hooks_str))

        logger.info("The process of configuring the settings of mkinitcpio has begun")
        self._safe_file_edit(self.mkinitcpio_path, edit_mkinitcpio)
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
        self._run_sudo(["systemctl", "disable", "sddm.service", "--now"])
        self._run_sudo(["systemctl", "enable", "sddm-plymouth.service", "--now"])
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
        commands = [
            ["update-grub"],
            ["mkinitcpio", "-P"],
            ["systemctl", "daemon-reload"],
        ]

        for cmd in commands:
            logger.info(f"Running {' '.join(cmd)}...")
            try:
                self._run_sudo(cmd)
            except RuntimeError as e:
                logger.warning(str(e))
