# ARM Architecture Support for Meowrch

## Overview

This guide explains how to install Meowrch on ARM devices, specifically Raspberry Pi 4. The installer now automatically detects your architecture and adapts the installation accordingly.

## Supported ARM Devices

###  Tested ON
- **Raspberry Pi 4** (8GB recommended, 4GB minimum)
  - aarch64 (64-bit ARM)
  - Best performance with BSPWM
  - Hyprland supported but may have performance limitations
    
### Known Graphics Limitation (Under Investigation)

During limited real-hardware testing, it was observed that graphical
workloads were executed primarily on the CPU instead of the GPU.

This indicates a potential issue with GPU acceleration configuration
(e.g. Mesa, KMS, or driver setup) on certain ARM devices.

- Desktop environments may feel less smooth than expected
- Wayland compositors may show reduced performance
- Video playback may rely on software rendering

This is a known limitation and is currently under investigation.
Future updates may improve GPU utilization on supported hardware.

### Not Recommended
- ARMv7 devices (32-bit ARM)
- Devices with less than 4GB RAM

## Installation

### Prerequisites

1. **Fresh Arch Linux ARM installation**
   - Follow the [official Arch Linux ARM installation guide](https://archlinuxarm.org/platforms/armv8/broadcom/raspberry-pi-4)
   - Ensure your system is up to date: `sudo pacman -Syu`

2. **Network connection**
   - Wired connection recommended for initial install
   - WiFi should work but may be slower

3. **Python dependencies**
   - The installer requires Python 3 and pip
   - Required Python packages: `loguru`, `inquirer`
   - These will be automatically installed by `install.sh`
   - For manual testing, install with: `pip install -r requirements.txt --break-system-packages`

4. **Sufficient storage**
   - Minimum 16GB SD card/storage
   - 32GB+ recommended for comfortable usage

### Installation Steps

```bash
# 1. Clone the repository
git clone https://github.com/meowrch/meowrch --depth 1 --single-branch
cd meowrch

# 2. (Optional) Check prerequisites
python check_prerequisites.py
# This will verify that your system has all required dependencies
# including Python, pip, git, and network connectivity

# 3. Run the installer
sh install.sh

# The installer will automatically detect ARM architecture and:
# - Display architecture information
# - Install Python dependencies (loguru, inquirer, etc.)
# - Skip x86-only packages (Steam, proprietary apps, etc.)
# - Configure ARM-specific drivers
# - Optimize for ARM performance

# 3. Reboot after installation
reboot
```

## What's Different on ARM?

### Limitations and Considerations on ARM

The following features are unavailable or have limited support on ARM,
depending on hardware, drivers, and distribution support:


#### Gaming
| Feature    | ARM Support Status | Consideration                                                                              |
| ---------- | ------------------ | ------------------------------------------------------------------------------------------ |
| Steam      | ⚠️ Partial         | Available only on specific distributions or devices; not officially supported on Arch ARM. |
| Gamemode   | ✅ Supported        | Runs in userspace and works on ARM without architecture-specific limitations.              |
| MangoHud   | ⚠️ Partial         | Requires a compatible Mesa/Vulkan/OpenGL stack; support varies by device.                  |
| PortProton | ❌ Not supported    | Depends on x86 Wine/Proton and is not viable on ARM.                                       |


#### Proprietary Applications
| Application                 | ARM Support Status | Consideration                                                                      |
| --------------------------- | ------------------ | ---------------------------------------------------------------------------------- |
| Visual Studio Code (binary) | ⚠️ Partial         | Official ARM64 builds exist but may not be available through default repositories. |
| Discord (binary)            | ❌ Not supported    | No official ARM Linux binary is provided.                                          |
| Spotify (binary)            | ❌ Not supported    | No official ARM Linux binary; web-based alternatives are required.                 |
| Yandex Music                | ❌ Not supported    | No native ARM Linux client available.                                              |
| OnlyOffice (binary)         | ⚠️ Partial         | ARM builds exist, but support and stability may vary by distribution.              |

#### Hardware-Specific
| Feature                           | ARM Support Status | Consideration                                                                          |
| --------------------------------- | ------------------ | -------------------------------------------------------------------------------------- |
| NVIDIA proprietary drivers        | ❌ Not supported    | Proprietary NVIDIA drivers are not available for ARM Linux.                            |
| AMD proprietary drivers           | ❌ Not supported    | AMD relies on open-source Mesa drivers on ARM platforms.                               |
| x86-specific audio firmware (SOF) | ❌ Not supported    | Sound Open Firmware is designed exclusively for x86 systems.                           |
| GRUB bootloader                   | ⚠️ Partial         | GRUB is available on ARM, but many devices rely on U-Boot or vendor-specific firmware. |
| Plymouth boot splash              | ✅ Supported        | Works on ARM systems with proper KMS/DRM support.                                      |


### ARM-Specific Additions

The installer adds these ARM-specific packages:

- **Raspberry Pi Firmware** (if on RPi)
- **Raspberry Pi Bootloader** (if on RPi)
- **Mesa VA-API drivers** (video acceleration)
- **CPU power management tools**

### Performance Optimizations

On ARM devices, Meowrch automatically:

1. **Configures GPU memory** (256MB for 8GB models)
2. **Enables KMS drivers** for better Wayland support
3. **Attempts to enable video acceleration**, depending on driver and hardware support
4. **Optimizes compositor settings** for ARM GPUs

## Window Manager Recommendations

### BSPWM (Recommended for ARM)
- ✅ Excellent performance on Raspberry Pi 4
- ✅ Low resource usage
- ✅ Stable and reliable
- ✅ Works great with Picom compositor

### Hyprland (Experimental on ARM)
- ⚠️ May have performance issues on RPi 4
- ⚠️ Requires good GPU driver support
- ⚠️ Higher resource usage
- ℹ️ Works better on more powerful ARM devices

**Recommendation**: Start with BSPWM, try Hyprland later if you want.

## Post-Installation

### Verify GPU Acceleration

```bash
# Check if GPU is detected
glxinfo | grep renderer

# Should show something like:
# OpenGL renderer string: V3D 4.2
```

### Check Boot Configuration (Raspberry Pi)

```bash
# View boot config
cat /boot/config.txt
# or
cat /boot/firmware/config.txt

# Look for [meowrch] section with optimizations
```

### Performance Tips

1. **Disable unnecessary animations**
   - Reduce Picom effects if using BSPWM
   - Lower Hyprland animation speeds

2. **Monitor resource usage**
   ```bash
   btop  # Check RAM and CPU usage
   ```

3. **Optimize swap** (if using 4GB model)
   ```bash
   sudo systemctl enable systemd-swap
   ```

## Troubleshooting

### Display Issues

**Problem**: Black screen or no display after boot

**Solution**:
```bash
# Edit boot config
sudo nano /boot/config.txt

# Ensure these lines are present:
dtoverlay=vc4-kms-v3d
max_framebuffers=2
```

### Performance Issues

**Problem**: Laggy desktop environment

**Solutions**:
1. Switch to BSPWM if using Hyprland
2. Disable compositor effects:
   ```bash
   # Edit ~/.config/picom/picom.conf
   # Set: fading = false; shadow = false;
   ```
3. Close unnecessary applications

### Package Installation Failures

**Problem**: Some AUR packages fail to build

**Solution**:
- ARM packages may take longer to compile
- Some packages may not support ARM - check AUR comments
- Use `paru` instead of `yay` for better ARM support

### Video Playback Issues

**Problem**: Choppy video playback

**Solution**:
```bash
# Verify hardware acceleration
vainfo

# Install additional codecs if needed
sudo pacman -S libva-mesa-driver mesa-vdpau
```

### Python Dependency Errors

**Problem**: `ModuleNotFoundError: No module named 'loguru'` or similar errors

**Solution**:
```bash
# First, ensure pip is installed
sudo pacman -S python-pip

# Then install dependencies manually
pip install loguru inquirer --break-system-packages

# Or use requirements.txt
pip install -r requirements.txt --break-system-packages

# The test script will also offer to install dependencies automatically
python test_arm_support.py
```

**Note**: The `test_arm_support.py` script will automatically detect if pip is missing and provide installation instructions.

## Known Limitations

1. **Compilation Time**: AUR packages compile on your device, which can be slow on ARM
2. **GPU Acceleration**: Some systems may fall back to CPU rendering due to driver or Mesa limitations
3. **Battery Monitor**: Not applicable for desktop Raspberry Pi setups
4. **Some Themes**: May need adjustment for ARM GPU capabilities
5. **Gaming**: x86 games are not supported on ARM


## Preserving Existing Configuration

If you're running Meowrch on a Raspberry Pi that's already configured (e.g., as a Samba server):

1. **Create a test user first**:
   ```bash
   sudo useradd -m -G wheel testuser
   sudo passwd testuser
   ```

2. **Install Meowrch on test user**:
   - Login as testuser
   - Run installation
   - Test everything works

3. **Your existing services** (like Samba) will continue running
4. **System-wide changes** are minimal - mostly package installation

## Getting Help

- **Telegram**: [t.me/meowrch](https://t.me/meowrch)
- **GitHub Issues**: [github.com/meowrch/meowrch/issues](https://github.com/meowrch/meowrch/issues)
- **Wiki**: [meowrch.github.io](https://meowrch.github.io)

When reporting ARM-specific issues, include:
- Device model (e.g., "Raspberry Pi 4 8GB")
- Architecture (`uname -m` output)
- Error messages from installation log

## Contributing

Found an issue on ARM? Want to add support for your ARM device?

1. Fork the repository
2. Test on your device
3. Submit a pull request with:
   - Device information
   - Changes made
   - Test results

---

**Note**: ARM support is actively being developed. Some features may change or improve over time.
