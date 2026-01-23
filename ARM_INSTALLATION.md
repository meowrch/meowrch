# ARM Architecture Support for Meowrch

## Overview

This guide explains how to install Meowrch on ARM devices, specifically Raspberry Pi 4. The installer now automatically detects your architecture and adapts the installation accordingly.

## Supported ARM Devices

### Fully Tested
- **Raspberry Pi 4** (8GB recommended, 4GB minimum)
  - aarch64 (64-bit ARM)
  - Best performance with BSPWM
  - Hyprland supported but may have performance limitations

### Should Work (Untested)
- **Raspberry Pi 3** (limited performance)
- **Generic ARM64 devices** with proper GPU drivers

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

3. **Sufficient storage**
   - Minimum 16GB SD card/storage
   - 32GB+ recommended for comfortable usage

### Installation Steps

```bash
# 1. Clone the repository
git clone https://github.com/meowrch/meowrch --depth 1 --single-branch
cd meowrch

# 2. Run the installer
sh install.sh

# The installer will automatically detect ARM architecture and:
# - Display architecture information
# - Skip x86-only packages (Steam, proprietary apps, etc.)
# - Configure ARM-specific drivers
# - Optimize for ARM performance

# 3. Reboot after installation
reboot
```

## What's Different on ARM?

### Excluded Features

The following features are **not available** on ARM:

#### Gaming
- ❌ Steam
- ❌ Gamemode
- ❌ MangoHud
- ❌ PortProton

#### Proprietary Applications
- ❌ Visual Studio Code (binary) - Use `code` (OSS version) instead
- ❌ Discord (binary)
- ❌ Spotify (binary)
- ❌ Yandex Music
- ❌ OnlyOffice (binary)

#### Hardware-Specific
- ❌ NVIDIA/AMD proprietary drivers
- ❌ x86 audio firmware (SOF)
- ❌ GRUB bootloader configuration
- ❌ Plymouth boot splash

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
3. **Sets up video acceleration** for smoother playback
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

## Known Limitations

1. **Compilation Time**: AUR packages compile on your device, which can be slow on ARM
2. **Battery Monitor**: Not applicable for desktop Raspberry Pi setups
3. **Some Themes**: May need adjustment for ARM GPU capabilities
4. **Gaming**: Not supported - ARM can't run x86 games

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
