
-- █▀▀█ █▀▀█ █░░░█ █▀▀ █▀▀█ █▀▀ █▀▀█ ▀█░█▀ █▀▀ █▀▀█ 
-- █░░█ █░░█ █▄█▄█ █▀▀ █▄▄▀ ▀▀█ █▄▄█ ░█▄█░ █▀▀ █▄▄▀ 
-- █▀▀▀ ▀▀▀▀ ░▀░▀░ ▀▀▀ ▀░▀▀ ▀▀▀ ▀░░▀ ░░▀░░ ▀▀▀ ▀░▀▀

-- window decorations
hl.config({
    decoration = {
        rounding = 0,
        active_opacity = 1,
        inactive_opacity = 1,
        fullscreen_opacity = 1,
        shadow = {
            enabled = 0,
        },
        blur = {
            enabled = 0,
            xray = 1,
        },
    },
    general = {
        gaps_in = 0,
        gaps_out = 0,
        border_size = 1,
    }
})

-- ##===> Rules
-- ############################################# 
hl.config.animations.enabled = false

hl.window_rule({
    match = { class = "(.*)" },
    opaque = true
})

-- Disable animations for specific layers
hl.layer_rule({
  name = "powersaver_workflow",
  match = { namespace = "^(rofi|notifications|swaync-(notification-window|control-center)|logout_dialog|waybar|.*www-daemon)$" },
  blur = false,
  no_anim = true
})