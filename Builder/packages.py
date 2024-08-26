from utils.schemes import Packages, DistributionPackages


BASE = Packages(
	pacman=DistributionPackages(
		common=[
			"pacman-contrib", "downgrade", "libnotify", "ffmpeg","ffmpegthumbnailer", "jq", "parallel", "kitty", "fastfetch", "lsd", "bat", "brightnessctl", 
			"automake", "blueman", "bluez", "bluez-utils", "dunst", "fakeroot", "firefox", "fish", "fisher", "dpkg", "gcc", "git", "gnu-netcat", "btop", 
			"micro", "mat2", "nemo", "papirus-icon-theme", "pavucontrol", "pamixer", "pipewire", "pipewire-pulse", "pipewire-audio",
			"pipewire-jack", "pipewire-alsa", "wireplumber", "python-pyalsa", "ranger", "redshift", "reflector", "sudo", "tree", "unrar",
			"zip", "unzip", "uthash", "ark", "cmake", "clang", "gzip", "imagemagick",
			"make", "openssh", "shellcheck", "vlc", "loupe", "usbutils", "openvpn", "networkmanager-openvpn", "p7zip", "gparted",
			"sshfs", "wget", "netctl", "libreoffice", "ttf-jetbrains-mono", "ttf-jetbrains-mono-nerd", "ttf-fira-code",
        	"ttf-iosevka-nerd", "playerctl", "starship", "upower", "udiskie", "zenity", "gvfs", "qt5ct", "qt6ct",
        	"timeshift", "sddm", "qt5-graphicaleffects", "qt5-svg",  "qt5-quickcontrols2", "clipnotify",
			"xdg-desktop-portal-gtk", "gnome-disk-utility", "evince", "neovim", "tmux", "cowsay", "polkit-gnome",
			"rofimoji", "wmname", "pyenv", "xdg-desktop-portal", "ttf-hack-nerd"
		],
		bspwm_packages=["xorg", "bspwm", "sxhkd", "xorg-xinit", "xclip", "feh", "lxappearance", "polybar", "xorg-xrandr", "xsettingsd"],
		hyprland_packages=[
			"hyprland", "waybar", "swww", "cliphist", "wl-clipboard", "xdg-desktop-portal-hyprland", "qt5-wayland", "qt6-wayland",
			"xdg-desktop-portal-wlr"]
	),
	aur=DistributionPackages(
		common=[
			"gnome-calculator-gtk3", "flameshot-git", "rofi-lbonn-wayland-git", "bibata-cursor-theme-bin", "tela-circle-icon-theme-dracula",
			"themix-theme-oomox-git", "themix-plugin-base16-git", "themix-icons-papirus-git", "themix-gui-git", "themix-export-spotify-git",
			"themix-theme-materia-git", "oomox-qt5-styleplugin-git", "oomox-qt6-styleplugin-git", "cava", "pokemon-colorscripts",
			"youtube-dl", "update-grub", "ttf-meslo-nerd-font-powerlevel10k", "visual-studio-code-bin"
		],
		bspwm_packages=["i3lock-color", "picom-ftlabs-git"],
		hyprland_packages=["hyprpicker", "swaylock-effects-git", "wlr-randr-git", "hyprprop", "grimblast-git"]
	)
)

CUSTOM = {
	"games": Packages(
		pacman=DistributionPackages(
			common=["steam", "gamemode", "mangohud"]
		),
		aur=DistributionPackages(
			common=["portproton"]
		)
	),
	"social_media": Packages(
		pacman=DistributionPackages(
			common=["telegram-desktop"]
		),
		aur=DistributionPackages(
			common=["vesktop"]
		)
	)
}

DRIVERS = {
	"intel": Packages(
		pacman=DistributionPackages(
			common=[
				"lib32-mesa", "vulkan-intel", "lib32-vulkan-intel", 
				"vulkan-icd-loader", "lib32-vulkan-icd-loader", "intel-media-driver",
				"libva-intel-driver", "xf86-video-intel"
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
				"nvidia-settings", "vulkan-icd-loader", "lib32-vulkan-icd-loader",
				"lib32-opencl-nvidia", "opencl-nvidia", "libxnvctrl"
			]
		)
	)
}
