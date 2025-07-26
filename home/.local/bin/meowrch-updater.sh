#!/bin/bash
#
# Meowrch Update Checker - система управления обновлениями
#

set -euo pipefail

# Константы
readonly GITHUB_API_URL="https://api.github.com/repos/meowrch/meowrch/releases"
readonly VERSION_FILE="/usr/local/share/meowrch/users/$(whoami)/version"
readonly NOTIFICATION_STATE="$HOME/.local/state/meowrch-notifications"

# Цвета
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly RED='\033[0;31m'
readonly NC='\033[0m'

# Функции вывода
log() {
    echo -e "${GREEN}[INFO]${NC} $1" >&2
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" >&2
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

# Получить текущую версию
get_current_version() {
    if [[ -f "$VERSION_FILE" ]]; then
        cat "$VERSION_FILE"
    else
        echo "2.0"  # По умолчанию
    fi
}

# Получить последнюю версию с GitHub
get_latest_version() {
    curl -s "$GITHUB_API_URL" | jq -r '.[0].tag_name' | sed 's/^v//'
}

# Получить все релизы, отсортированные по версии
get_all_releases() {
    curl -s "$GITHUB_API_URL" | jq -r '.[].tag_name' | sed 's/^v//' | sort -V
}

# Установить версию
set_version() {
    local version="$1"
    sudo mkdir -p "$(dirname "$VERSION_FILE")"
    echo "$version" | sudo tee "$VERSION_FILE" > /dev/null
    log "✅ Версия обновлена до $version"
}

# Сравнение версий (v1 > v2)
version_gt() {
    printf '%s\n%s\n' "$2" "$1" | sort -V -C
}

# Скачать и выполнить миграцию
run_migration() {
    local version="$1"
    local temp_dir="/tmp/meowrch-migration-$$"
    mkdir -p "$temp_dir"
    
    log "🔄 Выполняем миграцию на версию $version..."
    
    # Получаем данные релиза
    local release_data
    release_data=$(curl -s "$GITHUB_API_URL" | jq --arg version "$version" '.[] | select(.tag_name == $version)')
    
    # Получаем URL файла миграции
    local download_url
    download_url=$(echo "$release_data" | jq -r --arg filename "migrate_to_$version.py" '.assets[] | select(.name == $filename) | .browser_download_url')
    
    if [[ -z "$download_url" || "$download_url" == "null" ]]; then
        warn "Файл миграции migrate_to_$version.py не найден, пропускаем"
        set_version "$version"
        rm -rf "$temp_dir"
        return 0
    fi
    
    # Скачиваем файл миграции
    local migration_file="$temp_dir/migrate_to_$version.py"
    if ! curl -L -s "$download_url" -o "$migration_file"; then
        error "Не удалось скачать файл миграции"
        rm -rf "$temp_dir"
        return 1
    fi
    
    # Выполняем миграцию
    if python3 "$migration_file"; then
        log "✅ Миграция на версию $version выполнена успешно"
        set_version "$version"
    else
        error "Миграция на версию $version не удалась"
        rm -rf "$temp_dir"
        return 1
    fi
    
    rm -rf "$temp_dir"
    return 0
}

# Найти путь обновления между версиями
find_update_path() {
    local current_version="$1"
    local target_version="$2"
    local -a all_releases
    local -a path=()
    
    mapfile -t all_releases < <(get_all_releases)
    
    for release in "${all_releases[@]}"; do
        # Включаем все версии больше текущей и <= целевой (но не саму текущую)
        if version_gt "$release" "$current_version" && [[ "$release" != "$current_version" ]] && (version_gt "$target_version" "$release" || [[ "$release" == "$target_version" ]]); then
            path+=("$release")
        fi
    done
    
    printf '%s\n' "${path[@]}"
}

# Проверить, показывалось ли уведомление для версии
is_version_notified() {
    local version="$1"
    [[ -f "$NOTIFICATION_STATE" ]] && grep -q "^$version$" "$NOTIFICATION_STATE"
}

# Отметить версию как уведомленную
mark_version_notified() {
    local version="$1"
    mkdir -p "$(dirname "$NOTIFICATION_STATE")"
    echo "$version" >> "$NOTIFICATION_STATE"
}

notify_user() {
    local latest_version="$1"
    local current_version="$2"
    
    # Desktop уведомление
    if command -v notify-send > /dev/null 2>&1; then
        notify-send \
            "🔄 Новая версия Meowrch!" \
            "Доступна версия $latest_version (текущая: $current_version)" \
            --icon="software-update-available" \
            --urgency=normal
    fi
    
    log "🆕 Доступна новая версия: $latest_version (текущая: $current_version)"
    log "💡 Для обновления используйте: $0 update"
}

check_update() {
    local current_version
    current_version=$(get_current_version)
    
    log "Проверяем обновления... (текущая версия: $current_version)"
    
    local latest_version
    latest_version=$(get_latest_version)

    if version_gt "$latest_version" "$current_version"; then
        # Проверяем, показывали ли уже уведомление
        if is_version_notified "$latest_version"; then
            log "Уведомление для версии $latest_version уже показано"
            return 0
        fi
        
        # Показываем уведомление
        notify_user "$latest_version" "$current_version"
        mark_version_notified "$latest_version"
    else
        log "✅ У вас последняя версия ($current_version)"
    fi
}

# Показать статус текущей версии
show_status() {
    local current_version
    current_version=$(get_current_version)
    local latest_version
    latest_version=$(get_latest_version)
    
    log "📋 Текущая версия: $current_version"
    log "📋 Последняя версия: $latest_version"
    
    if [[ "$current_version" == "$latest_version" ]]; then
        log "✅ У вас последняя версия"
    elif version_gt "$latest_version" "$current_version"; then
        log "🆕 Доступно обновление до версии $latest_version"
    else
        log "ℹ️ Ваша версия новее последнего релиза"
    fi
}

# Выполнить обновление
perform_update() {
    local target_version="${1:-latest}"
    local current_version
    current_version=$(get_current_version)

    if [[ "$target_version" == "latest" ]]; then
        target_version=$(get_latest_version)
    fi

    log "🔄 Обновление с $current_version до $target_version"

    if [[ "$current_version" == "$target_version" ]]; then
        log "✅ Версия $target_version уже установлена"
        return 0
    fi

    # Находим путь обновления
    local -a update_path
    mapfile -t update_path < <(find_update_path "$current_version" "$target_version")

    if [[ ${#update_path[@]} -eq 0 ]]; then
        warn "Обновление не требуется или невозможно"
        return 0
    fi

    # Создаем красивое отображение цепочки версий
    local path_display="$current_version"
    for version in "${update_path[@]}"; do
        path_display+=" → $version"
    done
    log "📋 Путь обновления: $path_display"

    # Проходим по всем версиям и обновляем
    for version in "${update_path[@]}"; do
        if ! run_migration "$version"; then
            error "Обновление прервано на версии $version"
            return 1
        fi
    done

    log "🎉 Все обновления успешно применены!"
}

# Показать справку
show_help() {
    cat << EOF
Meowrch Update Checker - система управления обновлениями

ИСПОЛЬЗОВАНИЕ:
    $0 COMMAND [VERSION]

КОМАНДЫ:
    check-update     Проверить наличие обновлений и уведомить
    status          Показать статус версий
    update          Обновиться до последней версии
    update VERSION  Обновиться до указанной версии
    help            Показать эту справку

ПРИМЕРЫ:
    $0 check-update      # Проверить обновления
    $0 status           # Показать статус
    $0 update           # Обновиться до последней версии
    $0 update 3.0.0     # Обновиться до версии 3.0.0

EOF
}

main() {
    for cmd in curl jq; do
        if ! command -v "$cmd" > /dev/null 2>&1; then
            error "Требуется утилита: $cmd"
            exit 1
        fi
    done

    local command="${1:-check-update}"
    
    case "$command" in
        check-update)
            check_update
            ;;
        status)
            show_status
            ;;
        update)
            perform_update "${2:-latest}"
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            error "Неизвестная команда: $command"
            show_help
            exit 1
            ;;
    esac
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
