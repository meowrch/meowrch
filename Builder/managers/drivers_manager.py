import re
import subprocess
from pathlib import Path
import traceback
from typing import Optional, Dict
from loguru import logger


class ChdwManager:
    CACHYOS_REPO_URL = "https://mirror.cachyos.org/repo/x86_64/cachyos"
    LOCAL_REPO_PATH = Path("/var/lib/meowrch/cachyos-local")
    LOCAL_REPO_NAME = "meowrch-cachyos-local"
    PACMAN_CONF = Path("/etc/pacman.conf")
    REQUIRED_PACKAGES = ["chwd"]
    
    # Paths to external files
    SCRIPT_DIR = Path(__file__).parent.parent.parent
    UPDATE_SCRIPT_SOURCE = SCRIPT_DIR / "misc" / "scripts" / "update-chwd-repo.sh"
    SERVICE_SOURCE = SCRIPT_DIR / "misc" / "services" / "update-chwd-repo.service"
    TIMER_SOURCE = SCRIPT_DIR / "misc" / "services" / "update-chwd-repo.timer"
    
    UPDATE_SCRIPT_DEST = Path("/usr/local/bin/update-chwd-repo")
    SERVICE_DEST = Path("/etc/systemd/system/update-chwd-repo.service")
    TIMER_DEST = Path("/etc/systemd/system/update-chwd-repo.timer")

    def __init__(self):
        self.repo_path = self.LOCAL_REPO_PATH
        self.repo_db_path = self.repo_path / f"{self.LOCAL_REPO_NAME}.db.tar.zst"
        print(self.SCRIPT_DIR)

    def _run_sudo(self, cmd: list, **kwargs) -> subprocess.CompletedProcess:
        """Run command with sudo, prompting for password if needed"""
        return subprocess.run(["sudo"] + cmd, **kwargs)

    def setup_repo_directory(self) -> bool:
        try:
            logger.info(f"Creating repository directory: {self.repo_path}")
            self._run_sudo(["mkdir", "-p", str(self.repo_path)], check=True)
            self._run_sudo(["chmod", "755", str(self.repo_path)], check=True)
            return True
        except Exception as e:
            logger.error(f"Directory creation error: {e}")
            logger.debug(traceback.format_exc())
            return False

    def get_package_info(self, package_name: str) -> Optional[Dict]:
        try:
            logger.info(f"Getting information about {package_name} package")
            pkg_url = f"{self.CACHYOS_REPO_URL}/{package_name}"
            return {"url": pkg_url, "name": package_name}
        except Exception as e:
            logger.error(f"Error receiving package information: {e}")
            return None

    def find_latest_package(self, package_name: str) -> Optional[str]:
        try:
            logger.info(f"Searching for package: {package_name}")
            cmd = ["curl", "-s", f"{self.CACHYOS_REPO_URL}/"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            lines = result.stdout.split('\n')
            pattern = rf'({package_name}-[\d\.\-a-zA-Z_]+\.pkg\.tar\.zst)(?!\.sig)'
            found_packages = []
            
            for line in lines:
                match = re.search(pattern, line)
                if match:
                    pkg_file = match.group(1)
                    if not pkg_file.endswith('.sig'):
                        found_packages.append(pkg_file)
            
            if found_packages:
                logger.info(f"Found package: {found_packages[0]}")
                return found_packages[0]
            
            logger.warning(f"Package {package_name} not found in repository")
            return None
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Curl execution error: {e}")
            logger.debug(f"stderr: {e.stderr}")
            return None
        except Exception as e:
            logger.error(f"Package search error: {e}")
            logger.debug(traceback.format_exc())
            return None

    def download_package(self, package_file: str) -> bool:
        """Download package from CachyOS repository"""
        url = f"{self.CACHYOS_REPO_URL}/{package_file}"
        dest = self.repo_path / package_file
        
        logger.info(f"Downloading {package_file}")
        try:
            # Download with progress bar
            self._run_sudo(
                ["curl", "-L", "-#", "-o", str(dest), url],
                check=True,
                capture_output=False
            )
            
            # Check if file was downloaded
            if not dest.exists():
                logger.error(f"File was not downloaded: {dest}")
                return False
            
            logger.info(f"Package downloaded: {dest} ({dest.stat().st_size} bytes)")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Package download error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected download error: {e}")
            logger.debug(traceback.format_exc())
            return False

    def create_local_repo(self) -> bool:
        """Create local repository using repo-add"""
        logger.info("Creating local repository")
        try:
            # Get list of all .pkg.tar.zst files
            packages = list(self.repo_path.glob("*.pkg.tar.zst"))
            
            if not packages:
                logger.error("No packages to add to repository")
                return False
            
            logger.info(f"Found {len(packages)} package(s)")
            for pkg in packages:
                logger.info(f"  - {pkg.name}")
            
            # Create/update repository database
            cmd = ["repo-add", str(self.repo_db_path)] + [str(p) for p in packages]
            self._run_sudo(
                cmd,
                check=True,
                cwd=str(self.repo_path),
                capture_output=True,
                text=True
            )
            
            logger.info("Local repository created successfully")
            
            # Check that database was created
            if not self.repo_db_path.exists():
                logger.error("Repository database was not created")
                return False
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Repository creation error: {e}")
            logger.error(f"stdout: {e.stdout}")
            logger.error(f"stderr: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"Unexpected repository creation error: {e}")
            logger.debug(traceback.format_exc())
            return False

    def update_pacman_conf(self) -> bool:
        """Add local repository to pacman.conf"""
        logger.info("Updating pacman.conf")
        
        repo_entry = f"""
[{self.LOCAL_REPO_NAME}]
SigLevel = Optional TrustAll
Server = file://{self.repo_path}
"""
        
        try:
            with open(self.PACMAN_CONF, 'r') as f:
                content = f.read()
            
            # Check if repository is already added
            if self.LOCAL_REPO_NAME in content:
                logger.info("Repository already added to pacman.conf")
                return True
            
            # Add repository before [core]
            if '[core]' in content:
                content = content.replace('[core]', repo_entry + '\n[core]')
            else:
                # If [core] not found, add to the end
                content += '\n' + repo_entry
            
            # Create backup
            backup = self.PACMAN_CONF.with_suffix('.conf.backup')
            self._run_sudo(["cp", str(self.PACMAN_CONF), str(backup)], check=True)
            logger.info(f"Backup created: {backup}")
            
            # Write updated config
            # Use tee to write with sudo
            proc = subprocess.Popen(
                ["sudo", "tee", str(self.PACMAN_CONF)],
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                text=True
            )
            proc.communicate(input=content)
            
            if proc.returncode != 0:
                raise subprocess.CalledProcessError(proc.returncode, "tee")
            
            logger.info("pacman.conf updated successfully")
            return True
            
        except (IOError, subprocess.CalledProcessError) as e:
            logger.error(f"pacman.conf update error: {e}")
            logger.debug(traceback.format_exc())
            return False

    def install_chwd(self) -> bool:
        """Install chwd package via pacman"""
        logger.info("Installing chwd")
        try:
            # Update pacman databases
            logger.info("Updating pacman databases...")
            self._run_sudo(["pacman", "-Sy"], check=True)
            
            # Install packages
            logger.info(f"Installing packages: {', '.join(self.REQUIRED_PACKAGES)}")
            cmd = ["pacman", "-S", "--noconfirm"] + self.REQUIRED_PACKAGES
            self._run_sudo(cmd, check=True)
            
            logger.info("chwd installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"chwd installation error: {e}")
            return False

    def auto_configure_drivers(self) -> bool:
        """Automatic driver configuration using chwd"""
        logger.info("Automatic driver configuration")
        try:
            # First show available profiles
            logger.info("Checking available driver profiles...")
            result = self._run_sudo(
                ["chwd", "-l"],
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info("Available profiles:")
            print(result.stdout)
            
            # Automatic driver installation for PCI devices
            logger.info("Automatic driver installation...")
            result = self._run_sudo(
                ["chwd", "-a", "pci", "nonfree", "0300"],
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info("Driver configuration result:")
            print(result.stdout)
            
            logger.info("Drivers configured automatically")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.warning(f"Warning during driver configuration: {e}")
            logger.info("This is not a critical error - drivers may already be installed or not required")
            return True
        except Exception as e:
            logger.warning(f"Unexpected driver configuration error: {e}")
            return True  # Not critical

    def setup_update_checker(self) -> bool:
        """Install update script and systemd service/timer from misc/ directory"""
        try:
            # Check if source files exist
            if not self.UPDATE_SCRIPT_SOURCE.exists():
                logger.error(f"Update script not found: {self.UPDATE_SCRIPT_SOURCE}")
                return False
            
            if not self.SERVICE_SOURCE.exists():
                logger.error(f"Service file not found: {self.SERVICE_SOURCE}")
                return False
            
            if not self.TIMER_SOURCE.exists():
                logger.error(f"Timer file not found: {self.TIMER_SOURCE}")
                return False
            
            # Copy update script
            logger.info(f"Installing update script: {self.UPDATE_SCRIPT_DEST}")
            self._run_sudo(["cp", str(self.UPDATE_SCRIPT_SOURCE), str(self.UPDATE_SCRIPT_DEST)], check=True)
            self._run_sudo(["chmod", "755", str(self.UPDATE_SCRIPT_DEST)], check=True)
            logger.info("Update script installed")
            
            # Copy service and timer
            logger.info("Installing systemd service and timer...")
            self._run_sudo(["cp", str(self.SERVICE_SOURCE), str(self.SERVICE_DEST)], check=True)
            self._run_sudo(["cp", str(self.TIMER_SOURCE), str(self.TIMER_DEST)], check=True)
            
            # Reload systemd and enable timer
            self._run_sudo(["systemctl", "daemon-reload"], check=True)
            self._run_sudo(["systemctl", "enable", "update-chwd-repo.timer"], check=True)
            self._run_sudo(["systemctl", "start", "update-chwd-repo.timer"], check=True)
            
            return True
            
        except (IOError, subprocess.CalledProcessError) as e:
            logger.error(f"Failed to setup update checker: {e}")
            logger.debug(traceback.format_exc())
            return False

    def install(self) -> bool:
        logger.info("Starting chwd installation")
        
        steps = [
            ("Creating repository directory", self.setup_repo_directory),
            ("Downloading packages", self._download_all_packages),
            ("Creating local repository", self.create_local_repo),
            ("Updating pacman.conf", self.update_pacman_conf),
            ("Installing chwd", self.install_chwd),
            ("Auto-configuring drivers", self.auto_configure_drivers),
            ("Setting up update checker", self.setup_update_checker),
        ]
        
        for step_name, step_func in steps:
            if not step_func():
                logger.error(f"✗ Error at step: {step_name}")
                return False
        
        return True

    def _download_all_packages(self) -> bool:
        """Download all required packages"""
        all_success = True
        
        for package in self.REQUIRED_PACKAGES:
            logger.info(f"Processing package: {package}")
            
            pkg_file = self.find_latest_package(package)
            if not pkg_file:
                logger.error(f"Package not found: {package}")
                all_success = False
                continue
            
            if not self.download_package(pkg_file):
                all_success = False
                continue
        
        return all_success
