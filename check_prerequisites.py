#!/usr/bin/env python3
"""
Quick prerequisite checker for Meowrch ARM installation.
This script verifies that all basic requirements are met before installation.
"""

import subprocess
import sys
import platform
from pathlib import Path


def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def check_architecture():
    """Check if running on supported architecture"""
    print_header("ARCHITECTURE CHECK")
    
    arch = platform.machine().lower()
    print(f"Detected architecture: {arch}")
    
    if arch in ["x86_64", "amd64"]:
        print("✓ x86_64 architecture - Full support")
        return True
    elif arch in ["aarch64", "arm64"]:
        print("✓ ARM 64-bit architecture - Supported with limitations")
        print("  Note: Some features will be unavailable (gaming, proprietary apps)")
        return True
    elif arch.startswith("armv7"):
        print("⚠ ARM 32-bit architecture - Limited support")
        print("  Warning: Hyprland not recommended on ARMv7")
        return True
    else:
        print(f"✗ Unsupported architecture: {arch}")
        return False


def check_python():
    """Check Python version"""
    print_header("PYTHON CHECK")
    
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 8:
        print("✓ Python version is compatible")
        return True
    else:
        print("✗ Python 3.8 or higher is required")
        return False


def check_pip():
    """Check if pip is installed"""
    print_header("PIP CHECK")
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"✓ pip is installed: {result.stdout.strip()}")
            return True
        else:
            print("✗ pip is not working correctly")
            return False
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        print("✗ pip is not installed")
        print("\nTo install pip, run:")
        print("  sudo pacman -S python-pip")
        return False


def check_git():
    """Check if git is installed"""
    print_header("GIT CHECK")
    
    try:
        result = subprocess.run(
            ["git", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"✓ git is installed: {result.stdout.strip()}")
            return True
        else:
            print("✗ git is not working correctly")
            return False
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print("✗ git is not installed")
        print("\nTo install git, run:")
        print("  sudo pacman -S git")
        return False


def check_pacman():
    """Check if pacman is available"""
    print_header("PACKAGE MANAGER CHECK")
    
    try:
        result = subprocess.run(
            ["pacman", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print("✓ pacman is available")
            return True
        else:
            print("✗ pacman is not working correctly")
            return False
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print("✗ pacman is not found")
        print("  This script is designed for Arch Linux ARM")
        return False


def check_network():
    """Check network connectivity"""
    print_header("NETWORK CHECK")
    
    try:
        # Try to ping a reliable server
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "3", "8.8.8.8"],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0:
            print("✓ Network connectivity is working")
            return True
        else:
            print("⚠ Network connectivity issue detected")
            print("  Installation requires internet connection")
            return False
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print("⚠ Could not verify network connectivity")
        return False


def check_storage():
    """Check available storage"""
    print_header("STORAGE CHECK")
    
    try:
        result = subprocess.run(
            ["df", "-h", "/"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                parts = lines[1].split()
                if len(parts) >= 4:
                    available = parts[3]
                    print(f"Available storage: {available}")
                    print("✓ Storage check completed")
                    print("  Recommended: 32GB+ for comfortable usage")
                    return True
        print("⚠ Could not check storage")
        return True  # Don't fail on this
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print("⚠ Could not check storage")
        return True  # Don't fail on this


def main():
    """Run all prerequisite checks"""
    print("\n" + "=" * 70)
    print("  MEOWRCH PREREQUISITE CHECKER")
    print("=" * 70)
    print("\nThis script will verify that your system meets the basic")
    print("requirements for installing Meowrch.")
    
    checks = [
        ("Architecture", check_architecture),
        ("Python", check_python),
        ("pip", check_pip),
        ("git", check_git),
        ("pacman", check_pacman),
        ("Network", check_network),
        ("Storage", check_storage),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"\n✗ Error checking {name}: {e}")
            results[name] = False
    
    # Summary
    print_header("SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\nChecks passed: {passed}/{total}\n")
    
    for name, result in results.items():
        status = "✓" if result else "✗"
        print(f"  {status} {name}")
    
    print("\n" + "=" * 70)
    
    if all(results.values()):
        print("\n✓ All prerequisites are met!")
        print("  You can proceed with the installation:")
        print("  sh install.sh")
    else:
        print("\n⚠ Some prerequisites are missing.")
        print("  Please install the missing components before proceeding.")
        print("\n  For detailed installation instructions, see:")
        print("  - README.md (for x86_64)")
        print("  - ARM_INSTALLATION.md (for ARM devices)")
    
    print("\n" + "=" * 70 + "\n")
    
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
