#!/usr/bin/env python3

from __future__ import annotations

import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


# ──────────────────────────────────────────────────────────────────────────────
# Logging
# ──────────────────────────────────────────────────────────────────────────────

def info(message: str) -> None:
    print(f"[INFO] {message}")


def warn(message: str) -> None:
    print(f"[WARN] {message}", file=sys.stderr)


def fail(message: str, exit_code: int = 1) -> None:
    """Print a clean error message and exit. Does NOT produce a Python traceback."""
    print(f"[ERROR] {message}", file=sys.stderr)
    raise SystemExit(exit_code)


# ──────────────────────────────────────────────────────────────────────────────
# Package management
# ──────────────────────────────────────────────────────────────────────────────

class PackageManager:
    """Install, update, and inspect pacman / AUR packages."""

    # ------------------------------------------------------------------
    # AUR helper detection
    # ------------------------------------------------------------------

    @staticmethod
    def detect_aur_helper() -> str | None:
        """Return the first available AUR helper ('yay' or 'paru'), or None."""
        for helper in ("yay", "paru"):
            if shutil.which(helper):
                return helper
        return None

    @staticmethod
    def require_aur_helper() -> str:
        """Like detect_aur_helper(), but calls fail() if none is found."""
        helper = PackageManager.detect_aur_helper()
        if not helper:
            fail("AUR helper not found. Install 'yay' or 'paru' first.")
        return helper  # type: ignore[return-value]

    # ------------------------------------------------------------------
    # Package queries
    # ------------------------------------------------------------------

    @staticmethod
    def is_installed(package: str) -> bool:
        """Return True if the package is currently installed (pacman -Q)."""
        return subprocess.run(
            ["pacman", "-Q", package],
            capture_output=True,
        ).returncode == 0

    # ------------------------------------------------------------------
    # Internal runner (logs command + output)
    # ------------------------------------------------------------------

    @staticmethod
    def _run(command: list[str], title: str) -> int:
        info(f"{title}: {' '.join(command)}")
        try:
            proc = subprocess.run(command, check=False, text=True,
                                  capture_output=True)
        except FileNotFoundError:
            warn(f"Command not found: {command[0]}")
            return 127

        if proc.stdout and proc.stdout.strip():
            print(proc.stdout.strip())
        if proc.stderr and proc.stderr.strip():
            print(proc.stderr.strip(), file=sys.stderr)
        return proc.returncode

    # ------------------------------------------------------------------
    # Install
    # ------------------------------------------------------------------

    @classmethod
    def install_pacman(
        cls,
        packages: list[str],
        *,
        title: str = "Installing pacman packages",
    ) -> None:
        """Install pacman packages (syncs db with -Sy first). Fails on error."""
        if not packages:
            return
        rc = cls._run(
            ["sudo", "pacman", "-Sy", "--noconfirm", "--needed", *packages],
            title=title,
        )
        if rc != 0:
            fail(f"Failed to install: {', '.join(packages)}")

    @classmethod
    def install_aur(
        cls,
        packages: list[str],
        *,
        title: str = "Installing AUR packages",
    ) -> None:
        """Install AUR packages via yay/paru. Fails if no helper is found."""
        if not packages:
            return
        helper = cls.require_aur_helper()
        rc = cls._run(
            [helper, "-Sy", "--noconfirm", "--needed", *packages],
            title=title,
        )
        if rc != 0:
            fail(f"Failed to install AUR packages: {', '.join(packages)}")

    # ------------------------------------------------------------------
    # Full upgrade
    # ------------------------------------------------------------------

    @classmethod
    def update_all_pacman(cls) -> None:
        """Full pacman system upgrade (-Syu)."""
        rc = cls._run(
            ["sudo", "pacman", "-Syu", "--noconfirm"],
            title="Upgrading all pacman packages",
        )
        if rc != 0:
            fail("pacman full upgrade failed")

    @classmethod
    def update_all_aur(cls) -> None:
        """Full AUR system upgrade via yay/paru (-Syu)."""
        helper = cls.require_aur_helper()
        rc = cls._run(
            [helper, "-Syu", "--noconfirm"],
            title="Upgrading all AUR packages",
        )
        if rc != 0:
            fail("AUR full upgrade failed")


# ──────────────────────────────────────────────────────────────────────────────
# Pre-migration guards
# ──────────────────────────────────────────────────────────────────────────────

def check_called_from_update_script() -> None:
    """
    Fail if the script was not launched by update-meowrch.

    update-meowrch sets MEOWRCH_UPDATE_RUNNER=1 before calling python3,
    so running the migration directly (python migrate_to_X.py) is blocked.
    """
    if not os.environ.get("MEOWRCH_UPDATE_RUNNER"):
        fail(
            "This migration script must be run through 'update-meowrch', not directly.\n"
            "Use: update-meowrch update"
        )


def check_meowrch_tools_updated() -> None:
    """
    Fail if the meowrch-tools package has a pending update.

    Checks pacman's local sync db first (covers official / custom repos),
    then falls back to the AUR helper for AUR-sourced packages.
    """
    result = subprocess.run(
        ["pacman", "-Q", "meowrch-tools"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        fail(
            "Package 'meowrch-tools' is not installed.\n"
            "Please install it and ensure it is up to date before running the migration."
        )

    installed_version = result.stdout.strip().split()[-1]
    info(f"meowrch-tools installed: {installed_version}")

    outdated_info = ""

    pacman_check = subprocess.run(
        ["pacman", "-Qu", "meowrch-tools"],
        capture_output=True, text=True,
    )
    if pacman_check.stdout.strip():
        outdated_info = pacman_check.stdout.strip()
    else:
        helper = PackageManager.detect_aur_helper()
        if helper:
            aur_check = subprocess.run(
                [helper, "-Qu", "meowrch-tools"],
                capture_output=True, text=True,
            )
            if aur_check.stdout.strip():
                outdated_info = aur_check.stdout.strip()

    if outdated_info:
        # Format: "meowrch-tools 1.0.0 -> 1.1.0"
        parts = outdated_info.split()
        available_version = parts[-1] if len(parts) >= 4 else "a newer version"
        fail(
            f"meowrch-tools is outdated "
            f"(installed: {installed_version}, available: {available_version}).\n"
            f"Update it first, then retry the migration:\n"
            f"  sudo pacman -S meowrch-tools\n"
            f"  update-meowrch update"
        )


# ──────────────────────────────────────────────────────────────────────────────
# GitHub file sync
# ──────────────────────────────────────────────────────────────────────────────

class GitHubSync:
    """
    Downloads files from a specific GitHub release tag and writes them
    into the user's home directory.

    All repo-relative paths must start with "home/" — that prefix is
    stripped and the remainder is resolved against the real home directory.

    Example:
        gh = GitHubSync(repo="meowrch/meowrch", tag="3.1.0")

        # Download a single file
        gh.sync_file("home/.config/hypr/new.conf")

        # Download many files (some executable)
        gh.sync_files(
            paths=(
                "home/.config/hypr/new.conf",
                "home/.local/bin/my-script.sh",
            ),
            executable_files={"home/.local/bin/my-script.sh"},
        )

        # Fetch raw bytes (do something custom with them)
        data = gh.fetch_file("home/.config/some/file.json")
    """

    _USER_AGENT_PREFIX = "meowrch-migrator"

    def __init__(self, repo: str, tag: str) -> None:
        self.repo = repo
        self.tag = tag

    # ------------------------------------------------------------------
    # Path helpers
    # ------------------------------------------------------------------

    def _to_user_path(self, repo_rel_path: str) -> Path:
        path = Path(repo_rel_path)
        if not str(path).startswith("home/"):
            fail(
                f"Invalid tracked path (must start with 'home/'): {repo_rel_path}"
            )
        return Path.home() / path.relative_to("home")

    # ------------------------------------------------------------------
    # Network
    # ------------------------------------------------------------------

    def _fetch_bytes(self, repo_rel_path: str) -> bytes:
        url = (
            f"https://raw.githubusercontent.com/{self.repo}"
            f"/refs/tags/{self.tag}/{repo_rel_path}"
        )
        req = Request(
            url,
            headers={"User-Agent": f"{self._USER_AGENT_PREFIX}/{self.tag}"},
        )
        try:
            with urlopen(req, timeout=25) as resp:
                return resp.read()
        except HTTPError as exc:
            raise RuntimeError(f"{url} → HTTP {exc.code}") from exc
        except URLError as exc:
            raise RuntimeError(f"{url} → {exc.reason}") from exc

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def fetch_file(self, repo_rel_path: str) -> bytes:
        """Download and return raw bytes for *repo_rel_path* at this tag."""
        try:
            return self._fetch_bytes(repo_rel_path)
        except Exception as exc:
            fail(
                f"Could not fetch '{repo_rel_path}' "
                f"from github:{self.repo}@{self.tag}: {exc}"
            )

    def sync_file(
        self,
        repo_rel_path: str,
        *,
        dest: Path | None = None,
        executable: bool = False,
    ) -> Path:
        """
        Download *repo_rel_path* and write it to the user's home
        (or *dest* if explicitly provided).

        Returns the destination Path.
        """
        content = self.fetch_file(repo_rel_path)
        target = dest if dest is not None else self._to_user_path(repo_rel_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        if executable:
            mode = target.stat().st_mode
            target.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        info(f"Updated {target}")
        return target

    def sync_files(
        self,
        paths: tuple[str, ...] | list[str],
        *,
        executable_files: set[str] | frozenset[str] = frozenset(),
    ) -> int:
        """
        Download and install every path in *paths*.

        *executable_files* is a subset of *paths* whose destinations
        should be made executable after writing.

        Returns the number of files written.
        """
        count = 0
        for rel in paths:
            self.sync_file(rel, executable=(rel in executable_files))
            count += 1
        info(f"Synced {count} file(s) from github:{self.repo}@{self.tag}")
        return count
