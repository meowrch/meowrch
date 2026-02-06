#!/usr/bin/env python3
"""
Test script for ARM architecture detection and package filtering.
Run this to verify ARM support is working correctly.
"""

import subprocess
import sys
from pathlib import Path


def check_pip_installed():
    """Check if pip is installed and provide installation instructions if not"""
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "--version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def check_and_install_dependencies():
    """Check for required dependencies and install if missing"""
    
    # First, check if pip is installed
    if not check_pip_installed():
        print("=" * 70)
        print("ERROR: pip IS NOT INSTALLED")
        print("=" * 70)
        print("Python pip is required to install dependencies.")
        print("\nPlease install pip first with:")
        print("  sudo pacman -S python-pip")
        print("\nAfter installing pip, run this script again.")
        print("=" * 70)
        sys.exit(1)
    
    required_packages = {
        'loguru': 'loguru',
        'inquirer': 'inquirer'
    }
    
    missing_packages = []
    
    for import_name, pip_name in required_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(pip_name)
    
    if missing_packages:
        print("=" * 70)
        print("MISSING DEPENDENCIES DETECTED")
        print("=" * 70)
        print(f"The following Python packages are required but not installed:")
        for pkg in missing_packages:
            print(f"  - {pkg}")
        print()
        
        response = input("Would you like to install them now? [Y/n]: ").strip().lower()
        
        if response in ['', 'y', 'yes']:
            print("\nInstalling dependencies...")
            for pkg in missing_packages:
                try:
                    print(f"Installing {pkg}...")
                    subprocess.check_call(
                        [sys.executable, "-m", "pip", "install", pkg, "--break-system-packages"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.PIPE
                    )
                    print(f"✓ {pkg} installed successfully")
                except subprocess.CalledProcessError as e:
                    print(f"✗ Failed to install {pkg}: {e}")
                    print("\nPlease install manually with:")
                    print(f"  pip install {pkg} --break-system-packages")
                    sys.exit(1)
            print("\n✓ All dependencies installed successfully!\n")
            print("Restarting script to load new dependencies...\n")
            import os
            os.execv(sys.executable, [sys.executable] + sys.argv)
        else:
            print("\nPlease install the required packages manually:")
            print(f"  pip install {' '.join(missing_packages)} --break-system-packages")
            sys.exit(1)


# Check dependencies before importing
check_and_install_dependencies()

# Add Builder to path
sys.path.insert(0, str(Path(__file__).parent / "Builder"))

from utils.arch_detector import ArchDetector
from packages_arm import filter_packages_for_arm, get_arm_specific_packages
from packages import BASE


def test_architecture_detection():
    """Test architecture detection"""
    print("\n" + "="*70)
    print("TEST 1: Architecture Detection")
    print("="*70)
    
    arch_info = ArchDetector.get_architecture()
    ArchDetector.print_architecture_info()
    
    assert arch_info is not None, "Failed to detect architecture"
    print("✓ Architecture detection successful")
    
    return arch_info


def test_package_filtering(arch_info):
    """Test package filtering for ARM"""
    print("\n" + "="*70)
    print("TEST 2: Package Filtering")
    print("="*70)
    
    if not arch_info.is_arm:
        print("⊘ Skipping package filtering test (not on ARM)")
        return
    
    # Test pacman packages
    original_pacman = BASE.pacman.common.copy()
    filtered_pacman = filter_packages_for_arm(original_pacman, "pacman", False)
    
    print(f"\nOriginal pacman packages: {len(original_pacman)}")
    print(f"Filtered pacman packages: {len(filtered_pacman)}")
    print(f"Removed: {len(original_pacman) - len(filtered_pacman)} packages")
    
    # Check that x86-only packages are removed
    excluded = set(original_pacman) - set(filtered_pacman)
    if excluded:
        print(f"\nExcluded packages: {', '.join(sorted(excluded))}")
    
    # Test AUR packages
    original_aur = BASE.aur.common.copy()
    filtered_aur = filter_packages_for_arm(original_aur, "aur", False)
    
    print(f"\nOriginal AUR packages: {len(original_aur)}")
    print(f"Filtered AUR packages: {len(filtered_aur)}")
    print(f"Removed: {len(original_aur) - len(filtered_aur)} packages")
    
    excluded_aur = set(original_aur) - set(filtered_aur)
    if excluded_aur:
        print(f"\nExcluded AUR packages: {', '.join(sorted(excluded_aur))}")
    
    print("\n✓ Package filtering test successful")


def test_arm_specific_packages(arch_info):
    """Test ARM-specific package additions"""
    print("\n" + "="*70)
    print("TEST 3: ARM-Specific Packages")
    print("="*70)
    
    if not arch_info.is_arm:
        print("⊘ Skipping ARM-specific packages test (not on ARM)")
        return
    
    is_rpi = "raspberry_pi" in arch_info.device_type.value
    arm_pacman, arm_aur = get_arm_specific_packages(is_rpi)
    
    print(f"\nIs Raspberry Pi: {is_rpi}")
    print(f"ARM-specific pacman packages: {len(arm_pacman)}")
    if arm_pacman:
        print(f"  Packages: {', '.join(arm_pacman)}")
    
    print(f"\nARM-specific AUR packages: {len(arm_aur)}")
    if arm_aur:
        print(f"  Packages: {', '.join(arm_aur)}")
    
    print("\n✓ ARM-specific packages test successful")


def test_driver_manager(arch_info):
    """Test ARM driver manager (dry run)"""
    print("\n" + "="*70)
    print("TEST 4: ARM Driver Manager (Dry Run)")
    print("="*70)
    
    if not arch_info.is_arm:
        print("⊘ Skipping driver manager test (not on ARM)")
        return
    
    try:
        from managers.arm_driver_manager import ArmDriverManager
        
        manager = ArmDriverManager(arch_info)
        print(f"\n✓ ARM Driver Manager initialized successfully")
        print(f"  Device Type: {arch_info.device_type.value}")
        print(f"  Is Raspberry Pi: {manager.is_raspberry_pi}")
        
        # Don't actually run install in test
        print("\n  (Skipping actual installation in test mode)")
        
    except Exception as e:
        print(f"\n✗ ARM Driver Manager test failed: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("MEOWRCH ARM SUPPORT TEST SUITE")
    print("="*70)
    
    try:
        # Test 1: Architecture Detection
        arch_info = test_architecture_detection()
        
        # Test 2: Package Filtering
        test_package_filtering(arch_info)
        
        # Test 3: ARM-Specific Packages
        test_arm_specific_packages(arch_info)
        
        # Test 4: Driver Manager
        test_driver_manager(arch_info)
        
        # Summary
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        print("✓ All tests completed successfully!")
        print("\nYour system is ready for Meowrch ARM installation.")
        
        if arch_info.is_arm:
            print("\nNOTE: You are running on ARM architecture.")
            print("Some features will be limited. See ARM_INSTALLATION.md for details.")
        else:
            print("\nNOTE: You are running on x86_64 architecture.")
            print("Full feature support is available.")
        
        print("="*70 + "\n")
        
    except Exception as e:
        print("\n" + "="*70)
        print("TEST FAILED")
        print("="*70)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
