<div align="center">

<img src=".meta/logo.png" width="280px" alt="Meowrch Logo">

# ≽ܫ≼ Meowrch

### *Arch Linux. Evolved.*
**Where performance meets aesthetics**

<br>

[![Issues](https://img.shields.io/github/issues/meowrch/meowrch?color=ffb29b&labelColor=1C2325&style=for-the-badge)](https://github.com/meowrch/meowrch/issues)
[![Stars](https://img.shields.io/github/stars/meowrch/meowrch?color=fab387&labelColor=1C2325&style=for-the-badge)](https://github.com/meowrch/meowrch/stargazers)
[![License](https://img.shields.io/github/license/meowrch/meowrch?color=FCA2AA&labelColor=1C2325&style=for-the-badge)](./LICENSE)


[![README RU](https://img.shields.io/badge/README-RU-blue?color=cba6f7&labelColor=1C2325&style=for-the-badge)](./README.ru.md)
[![README ENG](https://img.shields.io/badge/README-ENG-blue?color=C9CBFF&labelColor=C9CBFF&style=for-the-badge)](./README.md)

<br>

[🚀 Quick Start](#-installation) • [📸 Gallery](#-visual-presentation) • [⚡ Features](#-why-meowrch) • [📖 Wiki](https://meowrch.github.io/en/) • [💬 Community](https://t.me/meowrch)

</div>

---

## 🎯 Why another distro?

<table>
<tr>
<td width="60%">

Arch Linux is **freedom**. But freedom **requires time**.

If you want Arch, but don't want to spend a week on **dotfiles** — Meowrch does it for you.

CachyOS — performance through deep optimization.
EndeavourOS - pure Arch with DE choice, minimal pre-configuration.
Manjaro - simplicity and stability through delayed updates.

**Meowrch** combines **everything:**
- ⚡ **Maximum performance**: best optimizations from [ARU](https://github.com/ventureoo/ARU) and [CachyOS](https://cachyos.org/). [Learn more](https://meowrch.github.io/en/optimization/performance-advantages/)
- 🎨 **Ready-to-use environment**: BSPWM/Hyprland with themes, smooth animations, functional **Dynamic Island**.
- 🛠️ **10-minute installation**: from clean Arch to fully configured desktop.

</td>
<td width="40%">

> [!NOTE]
> **"Arch for those who value their time"**

**By the numbers:**
- 🎯 **10 minutes** to complete installation.
- 🚀 **2 fully configured environments** BSPWM + Hyprland.
- 🎨 **2 default themes** + **community** theme store.
- ⚙️ **1Gb RAM** on system startup, thanks to [lightweight components](https://meowrch.github.io/en/introduction/component-selection-philosophy/).

</td>
</tr>
</table>

---

## 🌟 Why Meowrch?

<div align="center">

| 💎 Feature | 🔥 What it gives you |
|:---:|:---|
| **🚀 Optimization** | System configured with [aggressive optimization flags](https://meowrch.github.io/en/optimization/performance-advantages/), community-tested. Performance on par with [CachyOS](https://cachyos.org/) |
| **🎨 [Community](https://github.com/meowrch/pawlette-themes) theme store** | Change the entire system's appearance **with one command** |
| **📦 Open-source development** | We support Linux development by creating our own components **useful to the global Linux community**. [**Learn more here**](https://github.com/meowrch/) |
| **🛠️ Automation** | Installation **in 10 minutes**, full setup and optimization — **without manual config editing** |
| **🎯 Ergonomics** | Hotkeys designed **down to the smallest detail** — work faster |
| **🌊 Two environments** | BSPWM (X11) or Hyprland (Wayland) — **stability or modernity** |

</div>

---

## 📸 Visual presentation

<table align="center">
  <tr>
    <td colspan="3">
        <a href="https://youtu.be/KdGPDF4p5CA">
            <img src=".meta/assets/video-preview-youtube.png" width="100%" alt="Meowrch video preview">
        </a>
    </td>
  </tr>
  <tr>
    <td><img src=".meta/assets/1.png" alt="Basic applications and widgets"></td>
    <td><img src=".meta/assets/2.png" alt="Demonstration of desktop use case for music visualization."></td>
    <td><img src=".meta/assets/3.png" alt="Demonstration of Adobe software (Photoshop, AfterEffects) functionality"></td>
  </tr>
  <tr>
    <td><img src=".meta/assets/4.png" alt="Demonstration of latest Steam games with complex protection technologies like Denuvo (Mafia: The old country example)"></td>
    <td><img src=".meta/assets/5.png" alt="Demonstration of VSCode workflow"></td>
    <td><img src=".meta/assets/6.png" alt="Demonstration of desktop wallpaper change animation via mewline dynamic island"></td>
  </tr>
</table>

---

## 🛠️ Installation

> [!WARNING] 
> The installer is designed for **clean Arch Linux**. \
> If you already have a configured system, the installation **will overwrite** configurations. \
> For testing, create a new user. \
> If you like it — switch to Meowrch completely

### 📦 Quick start

```
# 1. Clone the repository
git clone https://github.com/meowrch/meowrch --depth 1 --single-branch
cd meowrch

# 2. Run the installer
sh install.sh

# 3. Reboot
reboot
```

---

## 📋 What do you get after installation?

<table align="center">
<tr>
<th width="30%">Component</th>
<th width="70%">Details</th>
</tr>
<tr>
<td><b>🐧 Base OS</b></td>
<td><a href="https://archlinux.org/">Arch Linux</a> + <a href="https://meowrch.github.io/en/optimization/performance-advantages/">aggressive optimization</a>
</tr>
<tr>
<td><b>🪟 Window managers</b></td>
<td><a href="https://github.com/baskerville/bspwm">BSPWM</a> (X11) | <a href="https://hyprland.org/">Hyprland</a> (Wayland)</td>
</tr>
<tr>
<td><b>📊 Panels</b></td>
<td><a href="https://github.com/polybar/polybar">Polybar</a> | <a href="https://github.com/Alexays/Waybar">Waybar</a> | <a href="https://github.com/meowrch/mewline">Mewline</a></td>
</tr>
<tr>
<td><b>🎨 Customization</b></td>
<td><a href="https://github.com/meowrch/pawlette">Pawlette</a> with pre-installed Catppuccin Mocha theme</td>
</tr>
<tr>
<td><b>🖥️ Terminal</b></td>
<td><a href="https://github.com/kovidgoyal/kitty">Kitty</a></td>
</tr>
<tr>
<td><b>🐚 Shells</b></td>
<td><a href="https://github.com/fish-shell/fish-shell">Fish</a> | <a href="https://www.zsh.org">Zsh</a></td>
</tr>
<tr>
<td><b>🎯 Menus and widgets</b></td>
<td><a href="https://github.com/davatorium/rofi">Rofi</a> | <a href="https://github.com/meowrch/mewline">Mewline</a></td>
</tr>
<tr>
<td><b>🔔 Notifications</b></td>
<td><a href="https://github.com/dunst-project/dunst">Dunst</a> | <a href="https://github.com/ErikReider/SwayNotificationCenter">Swaync</a> | <a href="https://github.com/meowrch/mewline">Mewline</a></td>
</tr>
<tr>
<td><b>📦 Repositories</b></td>
<td><a href="https://wiki.archlinux.org/title/Official_repositories">Arch Official</a> + <a href="https://aur.chaotic.cx/">Chaotic AUR</a></td>
</tr>
</table>

> [!NOTE]
> **Why these components?**
> We chose between performance, functionality, and stability.
> [Learn more about component selection](https://meowrch.github.io/en/introduction/сomponent-selection-philosophy/)

---

## ⌨️ Hotkeys

| Action                     | Combination    | Why is it convenient?                                                                                           |
| -------------------------- | -------------- | --------------------------------------------------------------------------------------------------------------- |
| Open terminal              | Super + Enter  | Quick access to universal tool.                                                                                 |
| Application selection      | Super + A      | Convenient way to choose the needed application.                                                                |
| Color picker               | Super + C      | Pick color from screen for design/development.                                                                  |
| Change wallpaper           | Super + W      | Rofi with preview. One button — new desktop look.                                                               |
| Change theme               | Super + T      | New theme in 2 seconds. Without config editing.                                                                 |
| Emoji                      | Super + .      | Like Windows 11, but faster.                                                                                    |
| Disable keyboard shortcuts | Super + Escape | Can help when using virtual machines on Meowrch with configurations that also work through keyboard shortcuts. |


> [!TIP] 
> **All available keyboard shortcuts** can be found [**here**](https://meowrch.github.io/en/usage/hotkeys/#meowrch-hotkeys).

---

## 💬 Support and community

<div align="center">

<a href="https://meowrch.github.io/en/">
<img src=".meta/assets/wiki-banner-en.png" width="80%" alt="Meowrch Wiki">
</a>

**[🌐 Official Wiki](https://meowrch.github.io/en/)** — guides, FAQ, troubleshooting

<br>

### 💬 Join the community

<table align="center">
<tr>
<td align="center" width="33%">
<h3>📢 Telegram</h3>
<a href="https://t.me/meowrch">
<img src="https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram">
</a>
<br><br>
News, updates and <a href="https://t.me/meowrch/7">quick support</a>
</td>
<td align="center" width="33%">
<h3>🐛 Issues</h3>
<a href="https://github.com/meowrch/meowrch/issues">
<img src="https://img.shields.io/badge/GitHub-Issues-181717?style=for-the-badge&logo=github&logoColor=white" alt="Issues">
</a>
<br><br>
Report a bug or suggest a feature
</td>
<td align="center" width="33%">
<h3>⭐ Reviews</h3>
<a href="https://meowrch.github.io/en/#reviews">
<img src="https://img.shields.io/badge/GitHub-Reviews-181717?style=for-the-badge&logo=github&logoColor=white" alt="Reviews">
</a>
<br><br>
Share your impressions about the distro
</td>
</tr>
</table>

</div>

---

## ⭐ What users say?

<div align="center">

<a href="https://meowrch.github.io/en/#reviews">
<img src=".meta/assets/reviews-banner-en.png" width="80%" alt="User Reviews">
</a>
<br>
<br>
</div>


> [!IMPORTANT]
> **📢 Your feedback matters!**  \
> Share your experience on the [**website**](https://meowrch.github.io/en/#reviews)


---

## ☕ Support the project

<div align="center">

**Like Meowrch?** Help develop the project! 🚀

| 💎 Cryptocurrency | 📬 Address |
|:---:|:---|
| **TON** | `UQB9qNTcAazAbFoeobeDPMML9MG73DUCAFTpVanQnLk3BHg3` |
| **Ethereum** | `0x56e8bf8Ec07b6F2d6aEdA7Bd8814DB5A72164b13` |
| **Bitcoin** | `bc1qt5urnw7esunf0v7e9az0jhatxrdd0smem98gdn` |
| **Tron** | `TBTZ5RRMfGQQ8Vpf8i5N8DZhNxSum2rzAs` |

<br>

*Every donation motivates to continue developing the project! ❤️*

</div>

---

## 📊 Project statistics


### ⭐ Star history

<a href="https://star-history.com/#meowrch/meowrch&Date">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=meowrch/meowrch&type=Date&theme=dark" />
<source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=meowrch/meowrch&type=Date" />
<img alt="Star History Chart" src="https://api.star-history.com/svg?repos=meowrch/meowrch&type=Date" />
</picture>
</a>

### 📈 Repository activity

![Repobeats Analytics](https://repobeats.axiom.co/api/embed/96a58cbd631f6100db2e77966316aa5cf0c21f47.svg "Repobeats analytics image")


---

<div align="center">

**Made with ❤️ for Linux community**

</div>