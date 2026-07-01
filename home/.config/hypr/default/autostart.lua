-- ▒█░░░ █▀▀█ █░░█ █▀▀▄ █▀▀ █░░█ 
-- ▒█░░░ █▄▄█ █░░█ █░░█ █░░ █▀▀█ 
-- ▒█▄▄█ ▀░░▀ ░▀▀▀ ▀░░▀ ▀▀▀ ▀░░▀

-- See https://wiki.hyprland.org/Configuring/Keywords/

-- Environment setup for D-Bus and systemd
-- System services

hl.on("hyprland.start", function()
    -- We use [[ ]] so that Bash can handle the ${XDG_BIN_HOME} environment variable on its own
    hl.exec_cmd([[${XDG_BIN_HOME:-$HOME/bin}/resetxdgportal.sh]])
    
    -- The UWSM and D-Bus environment
    hl.exec_cmd([[${XDG_BIN_HOME:-$HOME/bin}/uwsm-launcher.sh -t service -s s dbus-update-activation-environment --systemd --all]])
    hl.exec_cmd([[${XDG_BIN_HOME:-$HOME/bin}/uwsm-launcher.sh -t service -s s systemctl --user import-environment WAYLAND_DISPLAY XDG_CURRENT_DESKTOP]])
    
    -- Polkit and daemons (notifications, clipboard, disk manager)
    hl.exec_cmd([[${XDG_BIN_HOME:-$HOME/bin}/uwsm-launcher.sh -t service -s s ${XDG_BIN_HOME:-$HOME/bin}/polkitkdeauth.sh]])
    hl.exec_cmd([[${XDG_BIN_HOME:-$HOME/bin}/uwsm-launcher.sh -t service -s s swaync]])
    hl.exec_cmd([[${XDG_BIN_HOME:-$HOME/bin}/uwsm-launcher.sh -t service -s s hypridle]])
    hl.exec_cmd([[${XDG_BIN_HOME:-$HOME/bin}/uwsm-launcher.sh -t service -s s awww-daemon]])
    hl.exec_cmd([[${XDG_BIN_HOME:-$HOME/bin}/uwsm-launcher.sh -t service -s s udiskie --no-automount --smart-tray]])
    
    -- Clipboard managers (Cliphist)
    hl.exec_cmd([[${XDG_BIN_HOME:-$HOME/bin}/uwsm-launcher.sh -t service -s s wl-clip-persist --clipboard regular]])
    hl.exec_cmd([[${XDG_BIN_HOME:-$HOME/bin}/uwsm-launcher.sh -t service -s s wl-paste --type text --watch cliphist store]])
    hl.exec_cmd([[${XDG_BIN_HOME:-$HOME/bin}/uwsm-launcher.sh -t service -s s wl-paste --type image --watch cliphist store]])
    
    -- Your custom Mewline/Toggle-bar status bar, the Meowrch system service, and wallpapers
    hl.exec_cmd([[${XDG_BIN_HOME:-$HOME/bin}/uwsm-launcher.sh --system-mode sh ${XDG_BIN_HOME:-$HOME/bin}/toggle-bar.sh --start]])
    hl.exec_cmd([[systemctl --user start meowrch-hyprland-uwsm.service]])
    hl.exec_cmd([[sh ${XDG_BIN_HOME:-$HOME/bin}/set-wallpaper.sh --current]])
end)