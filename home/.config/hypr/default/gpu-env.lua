
-- ▒█▀▀█ ▒█▀▀█ ▒█░▒█ 　 ▒█▀▀▄ ▒█▀▀▀ ▀▀█▀▀ ▒█▀▀▀ ▒█▀▀█ ▀▀█▀▀ 
-- ▒█░▄▄ ▒█▄▄█ ▒█░▒█ 　 ▒█░▒█ ▒█▀▀▀ ░▒█░░ ▒█▀▀▀ ▒█░░░ ░▒█░░ 
-- ▒█▄▄█ ▒█░░░ ░▀▄▄▀ 　 ▒█▄▄▀ ▒█▄▄▄ ░▒█░░ ▒█▄▄▄ ▒█▄▄█ ░▒█░░

-- GPU Auto-detection (default/gpu)
-- Fallback for non-UWSM sessions. Uses unified detector script to set GPU_SETUP and source profile.

local gpu_setup = os.getenv("GPU_SETUP") or "unknown"

-- FALLBACK IN CASE OF STARTUP WITHOUT UWSM:
-- If we're launching directly via TTY (no variable in the environment),
-- we'll quickly and easily run your script in a single pass.
if not gpu_setup or gpu_setup == "" then
    local handle = io.popen("sh $HOME/.local/bin/gpu-detect-profile.sh 2>/dev/null")
    if handle then
        gpu_setup = handle:read("*l")
        handle:close()
    end
end

gpu_setup = gpu_setup or "unknown"

-- A func to check for the presence of an NVIDIA VA-API driver
local function has_nvidia_vaapi()
    local f1 = io.open("/usr/lib/dri/nvidia_drv_video.so", "r")
    local f2 = io.open("/usr/lib64/dri/nvidia_drv_video.so", "r")
    if f1 then f1:close() return true end
    if f2 then f2:close() return true end
    return false
end

-- Announcing the default tables for the Hyprland configuration
local cursor_settings = { 
    no_hardware_cursors = false,
    use_cpu_buffer = false 
}
local env_vars = {}


if gpu_setup == "nvidia-only" then
    -- █▀▀▄ ▀█░█▀ ░▀░ █▀▀▄ ░▀░ █▀▀█ 
    -- █░░█ ░█▄█░ ▀█▀ █░░█ ▀█▀ █▄▄█ 
    -- ▀░░▀ ░░▀░░ ▀▀▀ ▀▀▀░ ▀▀▀ ▀░░▀
    -- See https://wiki.hyprland.org/Nvidia/

    env_vars = {
        "LIBVA_DRIVER_NAME, nvidia",
        "__GLX_VENDOR_LIBRARY_NAME, nvidia", -- Disable this if you have issues with screensharing
        "__GL_VRR_ALLOWED, 1"
    }

    -- If you want to try hardware cursors,
    -- you can enable them by setting `cursor:no_hardware_cursors = false` ,
    -- but it will also require enabling `cursor.use_cpu_buffer`
    table.insert(env_vars, "WLR_NO_HARDWARE_CURSORS, 1")
    cursor_settings.no_hardware_cursors = true -- Set to true to avoid hitches
    -- cursor_settings.use_cpu_buffer = true


    -- https://wiki.hyprland.org/Nvidia/#va-api-hardware-video-acceleration
    -- Hardware video acceleration on Nvidia and Wayland is
    -- possible with the nvidia-vaapi-driver.
    -- This may solve specific issues in Electron apps.
    -- Conditionally enable Nvidia VA-API backend when libva-nvidia-driver is present
    if has_nvidia_vaapi() then
        table.insert(env_vars, "NVD_BACKEND, direct") -- Requires 'libva-nvidia-driver' package
    end

    -- https://wiki.hyprland.org/Nvidia/#regarding-environment-variables
    -- If you encounter crashes in Firefox, remove this line
    table.insert(env_vars, "GBM_BACKEND, nvidia-drm")

    -- If you have a multi-GPU setup and you are facing lag in external monitor.
    -- See https://wiki.hyprland.org/Configuring/Multi-GPU/

elseif gpu_setup == "hybrid-intel-nvidia" then
    -- ▒█▄░▒█ ▒█░░▒█ ▀█▀ ▒█▀▀▄ ▀█▀ ░█▀▀█ 　 ▀█▀ ▒█▄░▒█ ▀▀█▀▀ ▒█▀▀▀ ▒█░░░ 
    -- ▒█▒█▒█ ░▒█▒█░ ▒█░ ▒█░▒█ ▒█░ ▒█▄▄█ 　 ▒█░ ▒█▒█▒█ ░▒█░░ ▒█▀▀▀ ▒█░░░ 
    -- ▒█░░▀█ ░░▀▄▀░ ▄█▄ ▒█▄▄▀ ▄█▄ ▒█░▒█ 　 ▄█▄ ▒█░░▀█ ░▒█░░ ▒█▄▄▄ ▒█▄▄█
    -- Hybrid Intel + NVIDIA

    -- Disable hardware cursors to avoid potential hitches on some NVIDIA setups.
    cursor_settings.no_hardware_cursors = true
    
    env_vars = {
        "__GLX_VENDOR_LIBRARY_NAME, nvidia",
        "VK_LAYER_NV_optimus, 1"
    }

    -- https://wiki.hyprland.org/Nvidia/#va-api-hardware-video-acceleration
    -- Hardware video acceleration on Nvidia and Wayland is
    -- possible with the nvidia-vaapi-driver.
    -- This may solve specific issues in Electron apps.
    if has_nvidia_vaapi() then
        table.insert(env_vars, "NVD_BACKEND, direct") -- Requires 'libva-nvidia-driver' package
    end

elseif gpu_setup == "amd-only" then
    -- ░█▀▀█ ▒█▀▄▀█ ▒█▀▀▄ 
    -- ▒█▄▄█ ▒█▒█▒█ ▒█░▒█ 
    -- ▒█░▒█ ▒█░░▒█ ▒█▄▄▀ 
    -- AMD GPU specific configuration

    -- Safe defaults; avoid forcing GBM/WLR backends
    -- If needed, your system defaults will handle it.
    
    -- Hardware cursors generally work fine on AMD
    cursor_settings.no_hardware_cursors = false

elseif gpu_setup == "intel-only" then
    -- ▀█▀ █▀▀▄ ▀▀█▀▀ █▀▀ █░░ 
    -- ▒█░ █░░█ ░░█░░ █▀▀ █░░ 
    -- ▄█▄ ▀░░▀ ░░▀░░ ▀▀▀ ▀▀▀ 
    -- Intel GPU specific configuration
    -- Safe defaults; do not force debug or advanced variables.

    -- Hardware cursors generally work fine on Intel
    cursor_settings.no_hardware_cursors = false

elseif gpu_setup == "hybrid-amd-intel" then
    -- ░█▀▀█ ▒█▀▄▀█ ▒█▀▀▄ 　 　 ▀█▀ ▒█▄░▒█ ▀▀█▀▀ ▒█▀▀▀ ▒█░░░ 
    -- ▒█▄▄█ ▒█▒█▒█ ▒█░▒█ 　 　 ▒█░ ▒█▒█▒█ ░▒█░░ ▒█▀▀▀ ▒█░░░ 
    -- ▒█░▒█ ▒█░░▒█ ▒█▄▄▀ 　 　 ▄█▄ ▒█░░▀█ ░▒█░░ ▒█▄▄▄ ▒█▄▄█
    -- Hybrid AMD + Intel

    -- Environment is handled by UWSM; Hyprland-specific tweaks only.
    -- Hardware cursors generally fine with AMD/Intel.
    cursor_settings.no_hardware_cursors = false

elseif gpu_setup == "hybrid-intel-nouveau" then
    -- ▒█▄░▒█ ▒█▀▀▀█ ▒█░▒█ ▒█░░▒█ ▒█▀▀▀ ░█▀▀█ ▒█░▒█ 　 ▀█▀ ▒█▄░▒█ ▀▀█▀▀ ▒█▀▀▀ ▒█░░░ 
    -- ▒█▒█▒█ ▒█░░▒█ ▒█░▒█ ░▒█▒█░ ▒█▀▀▀ ▒█▄▄█ ▒█░▒█ 　 ▒█░ ▒█▒█▒█ ░▒█░░ ▒█▀▀▀ ▒█░░░ 
    -- ▒█░░▀█ ▒█▄▄▄█ ░▀▄▄▀ ░░▀▄▀░ ▒█▄▄▄ ▒█░▒█ ░▀▄▄▀ 　 ▄█▄ ▒█░░▀█ ░▒█░░ ▒█▄▄▄ ▒█▄▄█
    -- Hybrid Nouveau + Intel

    -- Environment is handled by UWSM; Hyprland-specific tweaks only.
    cursor_settings.no_hardware_cursors = false

elseif gpu_setup == "nouveau-only" then
    -- ▒█▄░▒█ ▒█▀▀▀█ ▒█░▒█ ▒█░░▒█ ▒█▀▀▀ ░█▀▀█ ▒█░▒█ 
    -- ▒█▒█▒█ ▒█░░▒█ ▒█░▒█ ░▒█▒█░ ▒█▀▀▀ ▒█▄▄█ ▒█░▒█ 
    -- ▒█░░▀█ ▒█▄▄▄█ ░▀▄▄▀ ░░▀▄▀░ ▒█▄▄▄ ▒█░▒█ ░▀▄▄▀

    -- Add Nouveau-specific Hyprland tweaks here if needed.
    -- (no overrides by default)
    cursor_settings.no_hardware_cursors = false

else
    -- Unknown GPU setup; no overrides applied.
    -- This file is intentionally empty.
end

-- We use environment variables via safe string parsing
for _, entry in ipairs(env_vars) do
    local key, value = entry:match("^([^,]+),%s*(.+)$")
    if key and value then
        hl.env(key, value)
    end
end

-- Applying cursor settings
hl.config({
    cursor = cursor_settings
})

-- Debug log (optional)
hl.on("hyprland.start", function()
     hl.exec_cmd(string.format(
         'notify-send -t 3000 -u low "🎮 GPU" "Profile: %s"',
         gpu_setup or "unknown"
     ))
end)