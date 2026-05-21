

-- ██████╗░░█████╗░  ███╗░░██╗░█████╗░████████╗  ███████╗██████╗░██╗████████╗
-- ██╔══██╗██╔══██╗  ████╗░██║██╔══██╗╚══██╔══╝  ██╔════╝██╔══██╗██║╚══██╔══╝
-- ██║░░██║██║░░██║  ██╔██╗██║██║░░██║░░░██║░░░  █████╗░░██║░░██║██║░░░██║░░░
-- ██║░░██║██║░░██║  ██║╚████║██║░░██║░░░██║░░░  ██╔══╝░░██║░░██║██║░░░██║░░░
-- ██████╔╝╚█████╔╝  ██║░╚███║╚█████╔╝░░░██║░░░  ███████╗██████╔╝██║░░░██║░░░
-- ╚═════╝░░╚════╝░  ╚═╝░░╚══╝░╚════╝░░░░╚═╝░░░  ╚══════╝╚═════╝░╚═╝░░░╚═╝░░░


-- █▀▀ █▀▀▄ ▀█░█▀ ░▀░ █▀▀█ █▀▀█ █▀▀▄ █▀▄▀█ █▀▀ █▀▀▄ ▀▀█▀▀ 
-- █▀▀ █░░█ ░█▄█░ ▀█▀ █▄▄▀ █░░█ █░░█ █░▀░█ █▀▀ █░░█ ░░█░░ 
-- ▀▀▀ ▀░░▀ ░░▀░░ ▀▀▀ ▀░▀▀ ▀▀▀▀ ▀░░▀ ▀░░░▀ ▀▀▀ ▀░░▀ ░░▀░░
-- See https://wiki.hyprland.org/Configuring/Environment-variables/

-- Hyprland
hl.env("XDG_CURRENT_DESKTOP", "Hyprland")
hl.env("XDG_SESSION_TYPE", "wayland")
hl.env("XDG_SESSION_DESKTOP", "Hyprland")

-- Environment
hl.on("hyprland.start", function()
    hl.exec_cmd([[sh -c 'set -a; eval "$(/usr/lib/systemd/user-environment-generators/30-systemd-environment-d-generator)"; set +a; dbus-update-activation-environment --systemd --all']])
end)

-- GPU env
require("default/gpu-env")	


-- █▀▀ █▀▀█ █░░█ █▀▀█ █▀▀ █▀▀ 
-- ▀▀█ █░░█ █░░█ █▄▄▀ █░░ █▀▀ 
-- ▀▀▀ ▀▀▀▀ ░▀▀▀ ▀░▀▀ ▀▀▀ ▀▀▀

require("default/autostart")
require("default/monitors")
require("default/input")
require("default/keybindings")
require("default/windowrules")
require("default/appearance")
require("default/general")
require("userprefs")
