
-- ██╗░░░██╗░██████╗███████╗██████╗░  ██████╗░██████╗░███████╗███████╗░██████╗
-- ██║░░░██║██╔════╝██╔════╝██╔══██╗  ██╔══██╗██╔══██╗██╔════╝██╔════╝██╔════╝
-- ██║░░░██║╚█████╗░█████╗░░██████╔╝  ██████╔╝██████╔╝█████╗░░█████╗░░╚█████╗░
-- ██║░░░██║░╚═══██╗██╔══╝░░██╔══██╗  ██╔═══╝░██╔══██╗██╔══╝░░██╔══╝░░░╚═══██╗
-- ╚██████╔╝██████╔╝███████╗██║░░██║  ██║░░░░░██║░░██║███████╗██║░░░░░██████╔╝
-- ░╚═════╝░╚═════╝░╚══════╝╚═╝░░╚═╝  ╚═╝░░░░░╚═╝░░╚═╝╚══════╝╚═╝░░░░░╚═════╝░
-- Set your personal hyprland configuration here


-- ##==> Optimization for your operating mode (default.lua / powersaver.lua / gaming.lua)
-- #######################################
require("workflows/default")


-- ##==> IO
-- #######################################
-- The default settings are located in ./default/monitors.lua
-- You can override them here
hl.monitor({
    output = "",
    mode = "preferred",
    position = "auto",
    scale = "1",
})

-- The default settings are located in ./default/input.lua
-- You can override them here
hl.config({
    input = {
        touchpad = { -- 🔗 See https://wiki.hyprland.org/Configuring/Variables/#touchpad
            natural_scroll = false,
        },
    },
})


-- ##==> Hotkeys
-- #######################################
-- The default settings are located in ./default/keybindings.lua
-- You can override them here
hl.bind("SUPER + SHIFT + C", hl.dsp.exec_cmd("code")) -- Open Visual Studio Code
hl.bind("SUPER + SHIFT + F", hl.dsp.exec_cmd("firefox")) -- Open browser
hl.bind("SUPER + SHIFT + T", hl.dsp.exec_cmd("Telegram")) -- Open Telegram
hl.bind("SUPER + SHIFT + O", hl.dsp.exec_cmd("obsidian")) -- Open Obsidian
hl.bind("SUPER + SHIFT + P", hl.dsp.exec_cmd("pwvucontrol")) -- Open audio control
hl.bind("SUPER + SHIFT + Y", hl.dsp.exec_cmd("kitty -e yazi")) -- Open CLI file manager


-- ##==> Decorations
-- #############################d##########
hl.config({
    decoration = {
        screen_shader = "shaders/rounded_corners.glsl"
    }
})


-- ##==> Other
-- #######################################
-- hl.config.ecosystem.no_update_news = false
-- hl.config.ecosystem.no_donation_nag = false
