-- █░█ █▀▀ █░░█ █▀▀▄ ░▀░ █▀▀▄ █▀▀▄ ░▀░ █▀▀▄ █▀▀▀ █▀▀ 
-- █▀▄ █▀▀ █▄▄█ █▀▀▄ ▀█▀ █░░█ █░░█ ▀█▀ █░░█ █░▀█ ▀▀█ 
-- ▀░▀ ▀▀▀ ▄▄▄█ ▀▀▀░ ▀▀▀ ▀░░▀ ▀▀▀░ ▀▀▀ ▀░░▀ ▀▀▀▀ ▀▀▀

-- ==> GLOBAL VARIABLES
------------------------------------------------------------------------------------------------
local mainMod = "SUPER"
local subMod = mainMod .. " + SHIFT"
local term = "kitty"
local bin = os.getenv("XDG_BIN_HOME") or (os.getenv("HOME") .. "/bin")
local home = os.getenv("HOME")
------------------------------------------------------------------------------------------------


-- ==> SYSTEM BINDS
------------------------------------------------------------------------------------------------
hl.bind(mainMod .. " + Return", hl.dsp.exec_cmd(term), {description = "Open terminal"})
hl.bind(mainMod .. " + E", hl.dsp.exec_cmd("nemo"), {description = "Open file manager"})
hl.bind("CTRL + SHIFT + Escape", hl.dsp.exec_cmd(term .. " -e btop"), {description = "Open system monitor"})
hl.bind(mainMod .. " + W", hl.dsp.exec_cmd("sh " .. bin .. "/rofi-menus/wallpaper-selector.sh"), {description = "Select wallpaper"})
hl.bind(mainMod .. " + T", hl.dsp.exec_cmd("sh " .. bin .. "/rofi-menus/theme-selector.sh"), {description = "Select theme"})
hl.bind("Print", hl.dsp.exec_cmd("sh " .. bin .. "/screenshot.sh"), {description = "Take screenshot GUI"})
hl.bind(mainMod .. " + Print", hl.dsp.exec_cmd("sh " .. bin .. "/screenshot.sh --full"), {description = "Take fullscreen screenshot"})
hl.bind(mainMod .. " + P", hl.dsp.exec_cmd([[bash -c '
    FLOAT=$(hyprctl -j activewindow | jq -r ".floating")
    if [ "$FLOAT" = "false" ]; then
    hyprctl dispatch '\''hl.dsp.window.float({ action = "toggle" })'\''
    fi
    hyprctl dispatch '\''hl.dsp.window.pin()'\''
']]), {description = "Pin window"})
hl.bind(mainMod .. " + V", hl.dsp.exec_cmd("sh " .. bin .. "/rofi-menus/clipboard-manager.sh"), {description = "Open clipboard manager"})
hl.bind(mainMod .. " + A", hl.dsp.exec_cmd("rofi -show drun"), {description = "Open application launcher"})
hl.bind(mainMod .. " + code:60", hl.dsp.exec_cmd("sh " .. bin .. "/rofi-menus/rofimoji.sh"), {description = "Open emoji picker"})
hl.bind(mainMod .. " + X", hl.dsp.exec_cmd("sh " .. bin .. "/rofi-menus/powermenu.sh"), {description = "Open power menu"})
hl.bind(mainMod .. " + L", hl.dsp.exec_cmd("sh " .. bin .. "/screen-lock.sh"), {description = "Lock screen"})
hl.bind(mainMod .. " + C", hl.dsp.exec_cmd("sh " .. bin .. "/color-picker.sh"), {description = "Pick color"})
hl.bind(mainMod .. " + B", hl.dsp.exec_cmd("sh " .. bin .. "/toggle-bar.sh --toggle --wm hyprland"), {description = "Toggle status bar"})
hl.bind(mainMod .. " + N", hl.dsp.exec_cmd("swaync-client -t"), {description = "Toggle Sway notification manager"})
hl.bind(subMod .. " + B", hl.dsp.exec_cmd("sh " .. bin .. "/toggle-bar.sh --next --wm hyprland"), {description = "Switch status bar"})
hl.bind("Caps_Lock", hl.dsp.exec_cmd("pkill -RTMIN+8 waybar"), {description = "Update capslock indicator in waybar", release = true})
hl.bind(mainMod .. " + SLASH", hl.dsp.exec_cmd("hotkeyhub --hyprland " .. home .. "/.config/hypr/hyprland.conf"), {description = "Hotkeys cheat sheet"})

-- ==> To disable/enable hotkeys 
-- TODO: Uncomment when issue #14578 is resolved
-- hl.bind(mainMod .. " + ESCAPE", hl.dsp.submap("passthru"), {description = "Disable all keybinds"})
-- hl.define_submap("passthru", function()
--     hl.bind(mainMod .. " + ESCAPE", hl.dsp.submap("reset"), {description = "Enable all keybinds"})
-- end)
------------------------------------------------------------------------------------------------


-- ==> SYSTEM CONTROLS
------------------------------------------------------------------------------------------------
-- VOLUME	
hl.bind("XF86AudioRaiseVolume", hl.dsp.exec_cmd("sh " .. bin .. "/volume.sh --device output --action increase"), {description = "Increase volume", repeating = true, locked = true})
hl.bind("XF86AudioLowerVolume", hl.dsp.exec_cmd("sh " .. bin .. "/volume.sh --device output --action decrease"), {description = "Decrease volume", repeating = true, locked = true})
hl.bind("XF86AudioMute", hl.dsp.exec_cmd("sh " .. bin .. "/volume.sh --device output --action toggle"), {description = "Toggle audio mute", locked = true})
hl.bind("XF86AudioMicMute", hl.dsp.exec_cmd("sh " .. bin .. "/volume.sh --device input --action toggle"), {description = "Toggle microphone mute", locked = true})

-- PLAYER
hl.bind("XF86AudioPlay", hl.dsp.exec_cmd("playerctl play-pause"), {description = "Play or pause media", locked = true})
hl.bind("XF86AudioPause", hl.dsp.exec_cmd("playerctl play-pause"), {description = "Play or pause media", locked = true})
hl.bind("XF86AudioNext", hl.dsp.exec_cmd("playerctl next"), {description = "Next track", locked = true})
hl.bind("XF86AudioPrev", hl.dsp.exec_cmd("playerctl previous"), {description = "Previous track", locked = true})
hl.bind("XF86AudioStop", hl.dsp.exec_cmd("playerctl stop"), {description = "Stop playback", locked = true})

-- BRIGHTNESS			  
hl.bind("XF86MonBrightnessUp", hl.dsp.exec_cmd("sh " .. bin .. "/brightness.sh --up"), {description = "Increase brightness", repeating = true, locked = true})
hl.bind("XF86MonBrightnessDown", hl.dsp.exec_cmd("sh " .. bin .. "/brightness.sh --down"), {description = "Decrease brightness", repeating = true, locked = true})
------------------------------------------------------------------------------------------------


-- ==> HYPRLAND
------------------------------------------------------------------------------------------------
-- Session actions
hl.bind(mainMod .. " + Delete", hl.dsp.exit(), {description = "Exit Hyprland"})
hl.bind("CTRL + SHIFT + R", hl.dsp.exec_cmd("hyprctl reload"), {description = "Reload Hyprland config"})

-- Window actions
hl.bind(mainMod .. " + Q", hl.dsp.window.close(), {description = "Close window"})
hl.bind(mainMod .. " + k", hl.dsp.window.kill(), {description = "Kill window"})
hl.bind(mainMod .. " + Space", hl.dsp.window.float({ action = "toggle" }), {description = "Toggle floating mode"})
hl.bind("ALT + Return", hl.dsp.window.fullscreen(), {description = "Toggle fullscreen"})

-- Move/Change window focus
hl.bind(mainMod .. " + right", hl.dsp.focus({ direction = "right" }), {description = "Focus window right"})
hl.bind(mainMod .. " + left", hl.dsp.focus({ direction = "left" }), {description = "Focus window left"})
hl.bind(mainMod .. " + up", hl.dsp.focus({ direction = "up" }), {description = "Focus window up"})
hl.bind(mainMod .. " + down", hl.dsp.focus({ direction = "down" }), {description = "Focus window down"})
hl.bind("ALT + Tab", hl.dsp.focus({ direction = "down" }), {description = "Switch to next window"})

-- Switch workspaces & Move focused window to a workspace
for i = 1, 10 do
    local key = i % 10 -- 10 maps to key 0
    hl.bind(mainMod .. " + " .. key, hl.dsp.focus({ workspace = i}), {description = "Switch to workspace " .. i})
    hl.bind(mainMod .. " + SHIFT + " .. key, hl.dsp.window.move({ workspace = i }), {description = "Move window to workspace " .. i})
end

hl.bind(mainMod .. " + CTRL + right", hl.dsp.focus({ workspace = "r+1" }), {description = "Next workspace"})
hl.bind(mainMod .. " + CTRL + left", hl.dsp.focus({ workspace = "r-1" }), {description = "Previous workspace"})
hl.bind(mainMod .. " + CTRL + down", hl.dsp.focus({ workspace = "empty" }), {description = "First empty workspace"})
hl.bind(mainMod .. " + mouse_down", hl.dsp.focus({ workspace = "e+1" }), {description = "Scroll workspaces forward"})
hl.bind(mainMod .. " + mouse_up", hl.dsp.focus({ workspace = "e-1" }), {description = "Scroll workspaces back"})

-- Resize windows
hl.bind(subMod .. " + right", hl.dsp.window.resize({ x = 30, y = 0, relative = true }), {description = "Resize window right", repeating = true})
hl.bind(subMod .. " + left", hl.dsp.window.resize({ x = -30, y = 0, relative = true }), {description = "Resize window left", repeating = true})
hl.bind(subMod .. " + up", hl.dsp.window.resize({ x = 0, y = -30, relative = true }), {description = "Resize window up", repeating = true})
hl.bind(subMod .. " + down", hl.dsp.window.resize({ x = 0, y = 30, relative = true }), {description = "Resize window down", repeating = true})
hl.bind(mainMod .. " + mouse:273", hl.dsp.window.resize(), {description = "Resize with mouse", mouse = true})

-- Move focused window around the current workspace
hl.bind(mainMod .. " + SHIFT + CTRL + right", hl.dsp.window.move({ direction = "right" }), {description = "Move window right"})
hl.bind(mainMod .. " + SHIFT + CTRL + left", hl.dsp.window.move({ direction = "left" }), {description = "Move window left"})
hl.bind(mainMod .. " + SHIFT + CTRL + up", hl.dsp.window.move({ direction = "up" }), {description = "Move window up"})
hl.bind(mainMod .. " + SHIFT + CTRL + down", hl.dsp.window.move({ direction = "down" }), {description = "Move window down"})
hl.bind(mainMod .. " + mouse:272", hl.dsp.window.drag(), {description = "Move window with mouse", mouse = true})

-- Silent workspaces
hl.bind(mainMod .. " + ALT + S", hl.dsp.exec_cmd([[
  bash -c '
    if hyprctl activewindow | grep -q "special:special"; then
      TARGET=$(hyprctl activeworkspace | awk "{print \$3}")
      hyprctl dispatch "hl.dsp.window.move({ workspace = $TARGET })"
    else
      hyprctl dispatch "hl.dsp.window.move({ workspace = \"special\", silent = true })"
    fi
  '
]]), {description = "Move window to special workspace"})
hl.bind(mainMod .. " + S", hl.dsp.workspace.toggle_special(), {description = "Show special workspace"})
------------------------------------------------------------------------------------------------