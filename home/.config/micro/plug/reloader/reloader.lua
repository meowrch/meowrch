local micro = import("micro")
local config = import("micro/config")
local os = import("os")
local time = import("time")

local last_config_mod = 0
local last_theme_mod = 0

-- Функция получения времени через нативный os.Stat из Go
function get_mod_time(path)
    local info, err = os.Stat(path)
    if err ~= nil then
        return 0
    end
    return info:ModTime():Unix()
end

function checkFiles()
    local home = os.Getenv("HOME")
    local config_path = home .. "/.config/micro/settings.json"
    
    -- 1. Чекаем конфиг
    local config_mod = get_mod_time(config_path)
    if config_mod > last_config_mod then
        if last_config_mod ~= 0 then
            micro.CurPane():HandleCommand("reload")
            micro.InfoBar():Message("Reloader: Настройки обновлены! ⚙️")
        end
        last_config_mod = config_mod
    end

    -- 2. Чекаем тему
    local current_theme = config.GetGlobalOption("colorscheme")
    if current_theme then
        local theme_path = home .. "/.config/micro/colorschemes/" .. current_theme .. ".micro"
        local theme_mod = get_mod_time(theme_path)
        if theme_mod > last_theme_mod then
            if last_theme_mod ~= 0 then
                micro.CurPane():HandleCommand("reload")
                micro.InfoBar():Message("Reloader: Тема [" .. current_theme .. "] обновлена! 🎨")
            end
            last_theme_mod = theme_mod
        end
    end

    micro.After(1 * time.Second, checkFiles)
end

function init()
    -- Сразу запоминаем текущее состояние, чтобы не релоадить при старте
    local home = os.Getenv("HOME")
    last_config_mod = get_mod_time(home .. "/.config/micro/settings.json")
    
    local current_theme = config.GetGlobalOption("colorscheme")
    if current_theme then
        last_theme_mod = get_mod_time(home .. "/.config/micro/colorschemes/" .. current_theme .. ".micro")
    end

    micro.InfoBar():Message("Reloader: Eco-Mode Active (Polling) 🍃")
    checkFiles()
end
