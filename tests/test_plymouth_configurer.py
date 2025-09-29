#!/usr/bin/env python3
import sys
import os
import shutil
from pathlib import Path

# Ensure project root is importable
sys.path.insert(0, str(Path(__file__).parent.parent))

import Builder.managers.custom_apps.plymouth as plymouth_mod
from Builder.managers.custom_apps.plymouth import PlymouthConfigurer


def _fake_run_sudo_factory(calls):
    def _fake_run_sudo(cmd, input=None):
        calls.append(list(cmd))
        return ""
    return _fake_run_sudo


def test_plymouth_systemd_boot_skips_grub():
    """When bootloader is systemd-boot, GRUB steps are skipped and mkinitcpio -P runs."""
    pc = PlymouthConfigurer()

    # Track sudo calls and intercept all sudo executions
    calls = []
    pc._run_sudo = _fake_run_sudo_factory(calls)

    # Force detection paths
    pc._bootloader_type = lambda: "systemd-boot"

    # Ensure we don't try to touch real /etc/default/grub via the editor
    grub_called = {"called": False}
    pc.grub_editor.add_cmdline_params = lambda params, update_grub=False: grub_called.__setitem__("called", True)

    # Run the two phases that could hit GRUB
    pc.update_grub_cmdline()
    pc.run_post_commands()

    # Expectations
    assert not grub_called["called"], "GRUB editor should not be called on systemd-boot"

    # Only mkinitcpio -P should be executed
    assert any(cmd[:2] == ["mkinitcpio", "-P"] for cmd in calls), "mkinitcpio -P must be called"
    assert not any("grub-mkconfig" in cmd for c in calls for cmd in c), "grub-mkconfig must not be called"


def test_plymouth_grub_calls_grub_mkconfig_when_ready():
    """On GRUB systems with /boot mounted and /boot/grub present, grub-mkconfig should run."""
    pc = PlymouthConfigurer()

    # Track sudo calls
    calls = []
    pc._run_sudo = _fake_run_sudo_factory(calls)

    # Force GRUB environment
    pc._bootloader_type = lambda: "grub"
    pc._is_boot_mounted = lambda: True

    # Patch module-level which to return a path for grub-mkconfig
    orig_which = plymouth_mod.shutil.which
    plymouth_mod.shutil.which = lambda name: "/usr/bin/grub-mkconfig" if name == "grub-mkconfig" else orig_which(name)

    # Patch Path.exists to simulate /boot/grub and /etc/default/grub presence
    orig_exists = Path.exists
    def fake_exists(p: Path):
        p_str = str(p)
        if p_str in ("/boot/grub", "/etc/default/grub"):
            return True
        return orig_exists(p)
    Path.exists = fake_exists

    try:
        # We do not want to touch real GRUB config file via editor; stub it
        pc.grub_editor.add_cmdline_params = lambda *args, **kwargs: True

        # Run post commands
        pc.run_post_commands()

        # Both grub-mkconfig and mkinitcpio -P should be present
        assert any(cmd[:2] == ["grub-mkconfig", "-o"] for cmd in calls), "grub-mkconfig must be called"
        assert any(cmd[:2] == ["mkinitcpio", "-P"] for cmd in calls), "mkinitcpio -P must be called"
    finally:
        # Restore patched functions
        plymouth_mod.shutil.which = orig_which
        Path.exists = orig_exists


def test_plymouth_grub_skips_when_boot_not_mounted():
    """On GRUB systems with /boot not mounted, grub-mkconfig should be skipped."""
    pc = PlymouthConfigurer()

    calls = []
    pc._run_sudo = _fake_run_sudo_factory(calls)

    pc._bootloader_type = lambda: "grub"
    pc._is_boot_mounted = lambda: False  # simulate unmounted /boot

    # Ensure which returns a valid grub-mkconfig path
    orig_which = plymouth_mod.shutil.which
    plymouth_mod.shutil.which = lambda name: "/usr/bin/grub-mkconfig" if name == "grub-mkconfig" else orig_which(name)

    # Pretend /boot/grub exists (though mount check should short-circuit)
    orig_exists = Path.exists
    def fake_exists(p: Path):
        if str(p) == "/boot/grub":
            return True
        return orig_exists(p)
    Path.exists = fake_exists

    try:
        pc.run_post_commands()
        # No grub-mkconfig expected due to unmounted /boot
        assert not any(cmd and cmd[0] == "grub-mkconfig" for cmd in calls), "grub-mkconfig must be skipped when /boot is not mounted"
        # mkinitcpio -P still expected
        assert any(cmd[:2] == ["mkinitcpio", "-P"] for cmd in calls), "mkinitcpio -P must be called"
    finally:
        plymouth_mod.shutil.which = orig_which
        Path.exists = orig_exists


if __name__ == "__main__":
    # Run tests manually for ad-hoc execution
    tests = [
        test_plymouth_systemd_boot_skips_grub,
        test_plymouth_grub_calls_grub_mkconfig_when_ready,
        test_plymouth_grub_skips_when_boot_not_mounted,
    ]
    ok = 0
    for t in tests:
        try:
            t()
            print(f"[OK] {t.__name__}")
            ok += 1
        except AssertionError as e:
            print(f"[FAIL] {t.__name__}: {e}")
    print(f"\n{ok}/{len(tests)} tests passed")

