#!/usr/bin/env python3
import sys
import os
import shutil
import tempfile
import subprocess
from pathlib import Path

# Ensure project root is importable
sys.path.insert(0, str(Path(__file__).parent.parent))

import Builder.managers.custom_apps.plymouth as plymouth_mod
from Builder.managers.custom_apps.plymouth import PlymouthConfigurer
from Builder.utils.mkinitcpio_config import MkinitcpioConfigEditor


def _fake_run_sudo_factory(calls):
    def _fake_run_sudo(cmd, input=None):
        calls.append(list(cmd))
        return ""
    return _fake_run_sudo


def _create_test_mkinitcpio_file(hooks: str) -> Path:
    """Создать тестовый mkinitcpio.conf с заданными хуками"""
    content = f'''# vim:set ft=sh
MODULES=()
BINARIES=()
FILES=()
HOOKS=({hooks})
'''

    tmp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='_plymouth_hooks_test')
    tmp_file.write(content)
    tmp_file.close()
    return Path(tmp_file.name)


def _mock_run_sudo_for_file(test_file: Path):
    def _mock_run_sudo(command, input=None):
        if command[0] == "cat":
            return test_file.read_text()
        elif command[0] == "cp":
            shutil.copy(command[1], command[2])
            return ""
        return ""
    return _mock_run_sudo


def test_plymouth_systemd_boot_skips_grub():
    """When bootloader is systemd-boot, GRUB steps are skipped and mkinitcpio -P runs."""
    pc = PlymouthConfigurer()

    # Track sudo calls and intercept all sudo executions
    calls = []
    pc._run_sudo = _fake_run_sudo_factory(calls)
    pc.initramfs_tool = "mkinitcpio"

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
    pc.initramfs_tool = "mkinitcpio"

    # Force GRUB environment
    pc._bootloader_type = lambda: "grub"

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

def test_plymouth_realistic_hooks_luks():
    """Проверить реальный набор HOOKS с LUKS и правильной вставкой plymouth."""
    hooks = "base udev autodetect microcode modconf keyboard keymap consolefont kms block encrypt filesystems fsck"
    test_file = _create_test_mkinitcpio_file(hooks)

    try:
        editor = MkinitcpioConfigEditor(test_file)
        editor._run_sudo = _mock_run_sudo_for_file(test_file)

        pc = PlymouthConfigurer()
        pc.mkinitcpio_editor = editor

        pc.update_mkinitcpio_hooks()

        final_hooks = editor.list_hooks()
        assert "plymouth" in final_hooks
        assert "sd-encrypt" in final_hooks
        assert "encrypt" not in final_hooks
        assert final_hooks.index("kms") < final_hooks.index("plymouth") < final_hooks.index("sd-encrypt")

        modules = editor.list_modules()
        assert "dm_mod" in modules
        assert "dm_crypt" in modules
        assert "aes" in modules
        assert "xts" in modules
    finally:
        test_file.unlink()


def test_systemd_replaces_encrypt_with_sd_encrypt():
    """Если используется systemd, encrypt должен быть заменен на sd-encrypt."""
    hooks = "base systemd autodetect modconf block encrypt filesystems fsck"
    test_file = _create_test_mkinitcpio_file(hooks)

    try:
        editor = MkinitcpioConfigEditor(test_file)
        editor._run_sudo = _mock_run_sudo_for_file(test_file)

        pc = PlymouthConfigurer()
        pc.mkinitcpio_editor = editor

        pc.update_mkinitcpio_hooks()

        final_hooks = editor.list_hooks()
        assert "sd-encrypt" in final_hooks
        assert "encrypt" not in final_hooks
    finally:
        test_file.unlink()


def test_udev_replaced_with_systemd_and_encrypt_migrated():
    """Если был udev, он заменяется на systemd, а encrypt на sd-encrypt."""
    hooks = "base udev autodetect modconf block encrypt filesystems fsck"
    test_file = _create_test_mkinitcpio_file(hooks)

    try:
        editor = MkinitcpioConfigEditor(test_file)
        editor._run_sudo = _mock_run_sudo_for_file(test_file)

        pc = PlymouthConfigurer()
        pc.mkinitcpio_editor = editor

        pc.update_mkinitcpio_hooks()

        final_hooks = editor.list_hooks()
        assert "systemd" in final_hooks
        assert "udev" not in final_hooks
        assert "sd-encrypt" in final_hooks
        assert "encrypt" not in final_hooks
    finally:
        test_file.unlink()


def test_plymouth_realistic_hooks_sd_encrypt():
    """Проверить реальный набор HOOKS с sd-encrypt и правильной вставкой plymouth."""
    hooks = "base systemd autodetect microcode modconf keyboard keymap consolefont kms block sd-encrypt lvm2 resume filesystems fsck"
    test_file = _create_test_mkinitcpio_file(hooks)

    try:
        editor = MkinitcpioConfigEditor(test_file)
        editor._run_sudo = _mock_run_sudo_for_file(test_file)

        pc = PlymouthConfigurer()
        pc.mkinitcpio_editor = editor

        pc.update_mkinitcpio_hooks()

        final_hooks = editor.list_hooks()
        assert "plymouth" in final_hooks
        assert final_hooks.index("kms") < final_hooks.index("plymouth") < final_hooks.index("sd-encrypt")

        modules = editor.list_modules()
        assert "dm_mod" in modules
        assert "dm_crypt" in modules
    finally:
        test_file.unlink()


def test_plymouth_grub_runs_when_boot_is_directory():
    """On GRUB systems where /boot is part of /, grub-mkconfig should still run."""
    pc = PlymouthConfigurer()

    calls = []
    pc._run_sudo = _fake_run_sudo_factory(calls)
    pc.initramfs_tool = "mkinitcpio"

    pc._bootloader_type = lambda: "grub"

    # Ensure which returns a valid grub-mkconfig path
    orig_which = plymouth_mod.shutil.which
    plymouth_mod.shutil.which = lambda name: "/usr/bin/grub-mkconfig" if name == "grub-mkconfig" else orig_which(name)

    # Pretend /boot/grub exists
    orig_exists = Path.exists
    def fake_exists(p: Path):
        if str(p) == "/boot/grub":
            return True
        return orig_exists(p)
    Path.exists = fake_exists

    try:
        pc.run_post_commands()
        # grub-mkconfig should still run when /boot is a directory on /
        assert any(cmd[:2] == ["grub-mkconfig", "-o"] for cmd in calls), "grub-mkconfig must be called"
        # mkinitcpio -P still expected
        assert any(cmd[:2] == ["mkinitcpio", "-P"] for cmd in calls), "mkinitcpio -P must be called"
    finally:
        plymouth_mod.shutil.which = orig_which
        Path.exists = orig_exists

def test_dracut_config_written_and_dracut_runs():
    """Ensure dracut is configured for plymouth and dracut regeneration is triggered."""
    pc = PlymouthConfigurer()
    calls = []

    with tempfile.TemporaryDirectory() as tmpdir:
        conf_dir = Path(tmpdir) / "dracut.conf.d"
        conf_dir.mkdir()
        conf_file = conf_dir / "90-plymouth-meowrch.conf"

        def _mock_run_sudo(cmd, input=None):
            if cmd[:2] == ["mkdir", "-p"]:
                Path(cmd[2]).mkdir(parents=True, exist_ok=True)
                calls.append(list(cmd))
                return ""
            if cmd[0] == "cp":
                shutil.copy(cmd[1], cmd[2])
                calls.append(list(cmd))
                return ""
            if cmd[0] == "cat" and cmd[1] == str(conf_file):
                calls.append(list(cmd))
                if conf_file.exists():
                    return conf_file.read_text()
                raise subprocess.CalledProcessError(1, cmd, "", "")
            calls.append(list(cmd))
            return ""

        pc._run_sudo = _mock_run_sudo
        pc.dracut_conf_dir = conf_dir
        pc.dracut_conf_file = conf_file
        pc.initramfs_tool = "dracut"

        pc.update_dracut_config()

        assert conf_file.exists(), "Dracut plymouth config file should be created"
        assert 'add_dracutmodules+=" plymouth "' in conf_file.read_text()

        pc.run_post_commands()
        assert any(cmd[0] == "dracut" for cmd in calls), "dracut must be called to regenerate initramfs"


if __name__ == "__main__":
    # Run tests manually for ad-hoc execution
    tests = [
        test_plymouth_systemd_boot_skips_grub,
        test_plymouth_grub_calls_grub_mkconfig_when_ready,
        test_plymouth_grub_runs_when_boot_is_directory,
        test_plymouth_realistic_hooks_luks,
        test_plymouth_realistic_hooks_sd_encrypt,
        test_systemd_replaces_encrypt_with_sd_encrypt,
        test_udev_replaced_with_systemd_and_encrypt_migrated,
        test_dracut_config_written_and_dracut_runs,
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

