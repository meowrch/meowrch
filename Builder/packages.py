from utils.schemes import DistributionPackages, PackageInfo, Packages

BASE = Packages(
	pacman=DistributionPackages(
		common=[  
			##==> Базовые инструменты и демоны
			###########################################
			"base-devel", "git", "networkmanager", "libnotify", "bluez", 
            "bluez-utils", "playerctl", "upower", "brightnessctl", 
			"udiskie", "xdg-desktop-portal-gtk", "xdg-desktop-portal",
            "mkinitcpio",

			##==> Звук
            ###########################################
            "pipewire-jack", "pipewire-alsa", "wireplumber", 
			"python-pyalsa", "pavucontrol", "pamixer", "pipewire", 
			"pipewire-pulse", "pipewire-audio",
            
			##==> CLI-Tools
			###########################################
            "jq", "fastfetch", "lsd", "bat", "micro", "sudo",
            "btop", "yazi", "starship", "openssh", "sshfs", 
            "wget", "neovim", "tmux", "ffmpeg", "cliphist", "udiskie", 
            "tree", "bash-completion",

			##==> GUI 
			###########################################
			"sddm", "plymouth", "firefox", "kitty", "blueman", "file-roller", "nemo", 
            "nemo-fileroller", "gvfs", "ffmpegthumbnailer", "imagemagick", 
            "vlc", "loupe", "qt5ct", "qt6ct", "qt5-graphicaleffects", 
            "qt5-svg", "qt5-multimedia", "qt5-quickcontrols2", "gst-plugins-good", 
            "redshift", "zenity", "polkit-gnome", "gnome-disk-utility","rofimoji",
            "flameshot", "rofi",
            
			##==> Шрифты
            ###########################################
            "ttf-hack-nerd", "noto-fonts", "noto-fonts-cjk", 
			"noto-fonts-emoji", "noto-fonts-extra", "ttf-iosevka-nerd", 
			"ttf-jetbrains-mono", "ttf-jetbrains-mono-nerd", 
			"ttf-fira-code",
		],
		bspwm_packages=[
			"xorg-server", "bspwm", "sxhkd", "xorg-xinit", "xclip", "feh", 
			"wmname", "polybar", "xorg-xrandr", "xsettingsd", "clipnotify",
            "dunst",
		],
		hyprland_packages=[
			"hyprland", "waybar", "hyprlock", "swww", "wl-clipboard", 
            "xdg-desktop-portal-hyprland", "qt5-wayland", "qt6-wayland",
			"xdg-desktop-portal-wlr", "hypridle", "hyprpicker", "wlr-randr",
            "uwsm", "libnewt", "swaync", "wl-clip-persist"
        ]
	),
	aur=DistributionPackages(
		common=[
            ##==> System
            ###########################################
            "meowrch-settings", "meowrch-tools", "update-grub",

			##==> GUI
            ###########################################
            "gnome-calculator-gtk3", "visual-studio-code-bin", 
            "nemo-tags",
            
            ##==> Кастомизация: Темы, иконки и курсор
            ###########################################
            "bibata-cursor-theme-bin", "tela-circle-icon-theme-dracula",
            "pawlette",
            
            ##==> CLI-Tools
            ###########################################
            "cava", "pokemon-colorscripts",
            
            ##==> Шрифты
            ###########################################
            "ttf-meslo-nerd-font-powerlevel10k",
		],
		bspwm_packages=["xkb-switch", "i3lock-color", "picom-ftlabs-git"],
		hyprland_packages=[
			"hyprprop", "grimblast-git", "mewline"
		]
	)
)

DRIVERS = {
	"intel": Packages(
		pacman=DistributionPackages(
			common=[
				"lib32-mesa", "vulkan-intel", "lib32-vulkan-intel", 
				"vulkan-icd-loader", "lib32-vulkan-icd-loader", 
				"intel-media-driver", "libva-intel-driver", 
				"xf86-video-intel"
			]
		)
	),
	"amd": Packages(
		pacman=DistributionPackages(
			common=[
				"lib32-mesa", "vulkan-radeon", "lib32-vulkan-radeon", 
				"vulkan-icd-loader", "lib32-vulkan-icd-loader"
			]
		)
	),
	"nvidia": Packages(
		pacman=DistributionPackages(
			common=[
				"nvidia-dkms", "nvidia-utils", "lib32-nvidia-utils",
				"nvidia-settings", "vulkan-icd-loader", "opencl-nvidia",
				"lib32-vulkan-icd-loader", "lib32-opencl-nvidia",
				"libxnvctrl", "libva-nvidia-driver"
			]
		)
	)
}

CUSTOM = {
    "useful": {
        "timeshift": PackageInfo("A system restore utility for Linux", recommended=True)
	},
    "development": {
        "obsidian": PackageInfo("A powerful knowledge base that works on top of a local folder of plain text Markdown files", recommended=True),
        "postgresql": PackageInfo("Sophisticated object-relational DBMS", recommended=True),
        "pgadmin4-desktop": PackageInfo("The desktop user interface for pgAdmin", aur=True, recommended=True),
        "redis": PackageInfo("An in-memory database that persists on disk")
	},
    "social_media": {
		"telegram-desktop": PackageInfo("Popular messenger", recommended=True, selected=True),
        "discord": PackageInfo("Popular social platform", recommended=True),
		"vesktop": PackageInfo("Custom Discord client", recommended=True, aur=True)
	},
	"games": {
		"steam": PackageInfo("The best launcher for games", recommended=True, selected=True), 
		"gamemode": PackageInfo("Game optimization tool", recommended=True, selected=True), 
		"mangohud": PackageInfo("Displays metrics in running games"),
        "portproton": PackageInfo("Launcher for Windows games with good optimization", recommended=True, aur=True)
	},
    "entertainment": {
        "yandex-music": PackageInfo("Personal recommendations, selections for any occasion and new music", aur=True, recommended=True),
        "spotify": PackageInfo("A proprietary music streaming service", aur=True, recommended=True)
	},
    "office": {
        "libreoffice-fresh": PackageInfo("Comprehensive office suite for word processing, spreadsheets, and presentations"),
        "onlyoffice-bin": PackageInfo("Office suite that allows collaborative editing of documents", aur=True, recommended=True),
		"evince": PackageInfo("Document viewer", selected=True, recommended=True)
    }
}
