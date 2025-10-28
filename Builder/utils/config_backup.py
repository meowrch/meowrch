import datetime
from pathlib import Path
from typing import Iterable
import subprocess


class ConfigBackup:
    DEFAULT_PATHS = [
        "/etc/mkinitcpio.conf",
        "/etc/default/grub",
        "/etc/pacman.conf",
        "/etc/sddm.conf",
    ]

    @staticmethod
    def _next_backup_path(path: Path) -> Path:
        ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        base = path.name + f".meowrch.bak.{ts}"
        return path.parent / base

    @staticmethod
    def backup_files(paths: Iterable[str]) -> None:
        for p in paths:
            src = Path(p)
            if not src.exists():
                continue
            dst = ConfigBackup._next_backup_path(src)
            try:
                subprocess.run(["sudo", "cp", "--preserve=all", str(src), str(dst)], check=True)
            except Exception:
                # Best-effort; continue
                pass

    @staticmethod
    def backup_all() -> None:
        ConfigBackup.backup_files(ConfigBackup.DEFAULT_PATHS)


