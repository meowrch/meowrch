-- ░▀░ █▀▀▄ █▀▀█ █░░█ ▀▀█▀▀ 
-- ▀█▀ █░░█ █░░█ █░░█ ░░█░░ 
-- ▀▀▀ ▀░░▀ █▀▀▀ ░▀▀▀ ░░▀░░
-- See https://wiki.hyprland.org/Configuring/Variables/

hl.gesture({
    fingers = 3,
    direction = "horizontal",
    action = "workspace",
})

hl.config({
    input = {
        kb_layout = "us,ru",
        kb_options = "grp:alt_shift_toggle",
        numlock_by_default = true,
        follow_mouse = 1,
        sensitivity = 0,
        force_no_accel = 1,
        accel_profile = "flat",
        touchpad = { -- 🔗 See https://wiki.hyprland.org/Configuring/Variables/#touchpad
            natural_scroll = false,
        },
    },
})

