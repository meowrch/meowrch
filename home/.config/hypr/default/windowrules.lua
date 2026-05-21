
-- # █░█░█ █ █▄░█ █▀▄ █▀█ █░█░█   █▀█ █░█ █░░ █▀▀ █▀
-- # ▀▄▀▄▀ █ █░▀█ █▄▀ █▄█ ▀▄▀▄▀   █▀▄ █▄█ █▄▄ ██▄ ▄█
-- # See https://wiki.hyprland.org/Configuring/Window-Rules/

-- ##===> Opacity & Blur
-- ############################################
hl.window_rule({
    match = { class = "^()$", title = "^()$" },
    no_blur = true
})

hl.window_rule({
    match = { class = "^(.*)$", title = "^(.*)$" },
    opacity = "0.90 0.90"
})

hl.window_rule({
    match = { class = "^(firefox)$" },
    opacity = "1 1"
})

-- ##===> Picture In Picture
-- ############################################
hl.window_rule({
    name = "picture_in_picture"
    match = { title = "^([Pp]icture[-\\s]?[Ii]n[-\\s]?[Pp]icture)(.*)$" },
    float = true
    keep_aspect_ratio = true
    move = { "(monitor_w*0.745)", "(monitor_h*0.74)" },
    size = { "(monitor_w*0.25)", "(monitor_h*0.25)" },
    pin = true
})

-- ##===> idleinhibit rules
-- ############################################
hl.window_rule({
    match = { class = "^(.*celluloid.*)$|^(.*mpv.*)$|^(.*vlc.*)$" },
    idle_inhibit = "fullscreen"
})

hl.window_rule({
    match = { class = "^(.*[Ss]potify.*)$" },
    idle_inhibit = "fullscreen"
})

hl.window_rule({
    match = { class = "^(yandex-music)$" },
    idle_inhibit = "fullscreen"
})

hl.window_rule({
    match = { class = "^(.*LibreWolf.*)$|^(.*floorp.*)$|^(.*brave-browser.*)$|^(.*firefox.*)$|^(.*chromium.*)$|^(.*zen.*)$|^(.*vivaldi.*)$" },
    idle_inhibit = "fullscreen"
})

-- ##===> Floating windows
-- ############################################
hl.window_rule({ match = { class = "^(vlc)$" }, float = true })
hl.window_rule({ match = { class = "^(blueman-manager)$" }, float = true })
hl.window_rule({ match = { class = "^(firefox)$", title = "^(Picture-in-Picture)$" }, float = true })
hl.window_rule({ match = { class = "^(firefox)$", title = "^(Library)$" }, float = true })
hl.window_rule({ match = { class = "^(org.kde.polkit-kde-authentication-agent-1)$" }, float = true })
hl.window_rule({ match = { class = "^(qt5ct)$" }, float = true })
hl.window_rule({ match = { class = "^(qt6ct)$" }, float = true })
hl.window_rule({ match = { class = "^(org.kde.ark)$" }, float = true })
hl.window_rule({ match = { class = "^(yad)$" }, float = true })

hl.window_rule({
    match = { class = "^(org.pulseaudio.pavucontrol)$" },
    float = true,
    size = { "(monitor_w*0.48)", "(monitor_h*0.42)" }
})

hl.window_rule({
    match = { class = "^(gnome-calculator)$" },
    float = true,
    center = true,
    size = { "(monitor_w*0.19)", "(monitor_h*0.47)" }
})

hl.window_rule({
    match = { class = "^(org.gnome.Loupe)$" },
    float = true,
    center = true,
    size = { "(monitor_w*0.63)", "(monitor_h*0.74)" }
})

hl.window_rule({
    match = { class = "^(org.gnome.FileRoller)$" },
    float = true,
    center = true,
    size = { "(monitor_w*0.63)", "(monitor_h*0.74)" }
})

hl.window_rule({
    match = { class = "^(com.meowrch.HotkeyHub)$" },
    float = true,
    center = true,
    size = { "(monitor_w*0.63)", "(monitor_h*0.74)" }
})

hl.window_rule({
    match = { class = "^(qalculate-gtk)$" },
    float = true,
    center = true,
    size = { "(monitor_w*0.45)", "(monitor_h*0.55)" }
})

-- ##===> Modals
-- ############################################
hl.window_rule({ match = { title = "^(Open)$" }, float = true })
hl.window_rule({ match = { title = "^(Authentication Required)$" }, float = true })
hl.window_rule({ match = { title = "^(Add Folder to Workspace)$" }, float = true })
hl.window_rule({ match = { initial_title = "^(Open File)$" }, float = true })
hl.window_rule({ match = { title = "^(Choose Files)$" }, float = true })
hl.window_rule({ match = { title = "^(Save As)$" }, float = true })
hl.window_rule({ match = { title = "^(Confirm to replace files)$" }, float = true })
hl.window_rule({ match = { title = "^(File Operation Progress)$" }, float = true })
hl.window_rule({ match = { title = "^(File Upload)(.*)$" }, float = true })
hl.window_rule({ match = { title = "^(Choose wallpaper)(.*)$" }, float = true })
hl.window_rule({ match = { title = "^(Library)(.*)$" }, float = true })
hl.window_rule({ match = { class = "^(.*dialog.*)$" }, float = true })
hl.window_rule({ match = { title = "^(.*dialog.*)$" }, float = true })

-- ##===> Portals
-- ############################################
hl.window_rule({ match = { class = "^(org.freedesktop.impl.portal.desktop.hyprland)$" }, float = true, center = true })
hl.window_rule({ match = { class = "^(org.freedesktop.impl.portal.desktop.gtk)$" }, float = true, center = true })
hl.window_rule({ match = { class = "^([Xx]dg-desktop-portal-gtk)$" }, float = true, center = true })

-- ##===> Layer rules
-- ############################################
hl.layer_rule({
    match = { namespace = "rofi" },
    blur = true,
    ignore_alpha = 0
})

hl.layer_rule({
    match = { namespace = "notifications" },
    blur = true,
    ignore_alpha = 0
})

hl.layer_rule({
    match = { namespace = "swaync-notification-window" },
    blur = true,
    ignore_alpha = 0
})

hl.layer_rule({
    match = { namespace = "swaync-control-center" },
    blur = true,
    ignore_alpha = 0
})

hl.layer_rule({
    match = { namespace = "waybar" },
    blur = true,
    ignore_alpha = 0
})

hl.layer_rule({
    match = { namespace = "selection" },
    no_anim = true
})