"""
Knowledge base for the correct order of hooks and modules in mkinitcpio
Based on Arch Linux official documentation and best practices
"""

from typing import Dict, List
from loguru import logger


class MkinitcpioRules:
    """База знаний о правильном порядке хуков и модулей"""
    
    def __init__(self):
        # Определяем порядок хуков: чем меньше число, тем раньше должен идти хук
        self.hook_priorities = {
            # Базовые хуки (обязательные, идут первыми)
            "base": 10,
            "systemd": 15,  # Должен быть вместо udev
            "udev": 15,     # Альтернатива systemd (но systemd предпочтительнее)
            
            # Обнаружение и автоконфигурация
            "autodetect": 20,
            "microcode": 25,
            "modconf": 30,
            
            # Ранняя инициализация (до основных драйверов)
            "keyboard": 35,
            "keymap": 40,
            "consolefont": 45,
            
            # Видео и KMS (должны быть рано для Plymouth)
            "kms": 50,
            
            # Пользовательский интерфейс загрузки
            "plymouth": 55,  # После KMS, но до блочных устройств
            
            # Блочные устройства и шифрование
            "block": 60,
            "encrypt": 65,      # systemd-cryptsetup
            "sd-encrypt": 65,   # то же что encrypt, но для systemd
            "lvm2": 70,         # После шифрования
            "mdadm_udev": 75,   # RAID
            
            # Файловые системы и проверки
            "resume": 80,       # Перед файловыми системами
            "filesystems": 90,  # Почти в конце
            "fsck": 95,         # Проверка FS после монтирования
            
            # Специальные хуки
            "usr": 85,          # Если /usr на отдельном разделе
            "shutdown": 100,    # В самом конце
        }
        
        # Группы хуков для лучшего понимания зависимостей
        self.hook_groups = {
            "early": ["base", "systemd", "udev"],
            "detection": ["autodetect", "microcode", "modconf"],
            "input": ["keyboard", "keymap", "consolefont"],
            "graphics": ["kms", "plymouth"],
            "storage": ["block", "encrypt", "sd-encrypt", "lvm2", "mdadm_udev"],
            "filesystem": ["resume", "filesystems", "fsck", "usr"],
            "late": ["shutdown"]
        }
        
        # Строгие правила зависимостей
        self.hook_dependencies = {
            "plymouth": {
                "must_be_after": ["kms", "systemd", "autodetect"],
                "must_be_before": ["encrypt", "sd-encrypt", "block"],
                "description": "Plymouth нужен KMS и systemd, но должен быть до шифрования"
            },
            "encrypt": {
                "must_be_after": ["block"],
                "must_be_before": ["filesystems"],
                "description": "Шифрование после блочных устройств, но до FS"
            },
            "sd-encrypt": {
                "must_be_after": ["block"],
                "must_be_before": ["filesystems"], 
                "description": "systemd шифрование после блочных устройств"
            },
            "lvm2": {
                "must_be_after": ["encrypt", "sd-encrypt"],
                "must_be_before": ["filesystems"],
                "description": "LVM после шифрования"
            },
            "resume": {
                "must_be_after": ["encrypt", "sd-encrypt"],
                "must_be_before": ["filesystems"],
                "description": "Resume после шифрования, но до FS"
            },
            "fsck": {
                "must_be_after": ["filesystems"],
                "description": "Проверка FS только после монтирования"
            }
        }
        
        # Правила для модулей (порядок может быть важен для некоторых)
        self.module_priorities = {
            # GPU модули (должны загружаться рано)
            "nvidia": 10,
            "nvidia_modeset": 11,
            "nvidia_uvm": 12, 
            "nvidia_drm": 13,
            
            "amdgpu": 15,
            "radeon": 16,
            
            "i915": 20,
            "xe": 21,  # Intel Xe (новый драйвер)
            
            # Сетевые модули
            "r8169": 30,
            "e1000e": 31,
            "iwlwifi": 35,
            
            # Файловые системы
            "ext4": 40,
            "btrfs": 41,
            "xfs": 42,
            "ntfs3": 43,
            
            # Шифрование
            "dm_mod": 48,
            "dm_crypt": 50,
            "aes": 51,
            "xts": 52,
            "sha256": 53,
            "sha512": 54,
            "cryptd": 55,
            
            # Общие модули (в конце)
            "usb_storage": 60,
            "ahci": 65,
            "sd_mod": 70,
        }

        # Требуемые модули для конкретных хуков
        # Важно: используем только универсальные модули, доступные в большинстве конфигураций ядра
        self.hook_required_modules = {
            # LUKS / dm-crypt
            "encrypt": [
                "dm_mod",
                "dm_crypt",
                "aes",
                "xts",
                "sha256",
                "sha512",
                "cryptd",
            ],
            # systemd-cryptsetup
            "sd-encrypt": [
                "dm_mod",
                "dm_crypt",
                "aes",
                "xts",
                "sha256",
                "sha512",
                "cryptd",
            ],
        }
    
    def get_hook_priority(self, hook: str) -> int:
        """Получить приоритет хука"""
        return self.hook_priorities.get(hook, 1000)  # Неизвестные хуки - в конец
    
    def get_module_priority(self, module: str) -> int:
        """Получить приоритет модуля"""
        return self.module_priorities.get(module, 1000)

    def get_required_modules_for_hooks(self, hooks: List[str]) -> List[str]:
        """Получить список обязательных модулей для заданных хуков"""
        required_modules: List[str] = []
        for hook in hooks:
            for module in self.hook_required_modules.get(hook, []):
                if module not in required_modules:
                    required_modules.append(module)

        if not required_modules:
            return []

        return self.sort_modules_by_priority(required_modules)
    
    def validate_hook_order(self, hooks: List[str]) -> List[str]:
        """Проверить и исправить порядок хуков"""
        issues = []
        
        for hook in hooks:
            if hook in self.hook_dependencies:
                deps = self.hook_dependencies[hook]
                hook_pos = hooks.index(hook)
                
                # Проверяем must_be_after
                for required_before in deps.get("must_be_after", []):
                    if required_before in hooks:
                        required_pos = hooks.index(required_before)
                        if hook_pos <= required_pos:
                            issues.append({
                                "type": "order_violation",
                                "hook": hook,
                                "should_be_after": required_before,
                                "current_positions": {hook: hook_pos, required_before: required_pos}
                            })
                
                # Проверяем must_be_before
                for required_after in deps.get("must_be_before", []):
                    if required_after in hooks:
                        required_pos = hooks.index(required_after)
                        if hook_pos >= required_pos:
                            issues.append({
                                "type": "order_violation", 
                                "hook": hook,
                                "should_be_before": required_after,
                                "current_positions": {hook: hook_pos, required_after: required_pos}
                            })
        
        return issues
    
    def sort_hooks_by_priority(self, hooks: List[str]) -> List[str]:
        """Отсортировать хуки по приоритету"""
        def hook_sort_key(hook):
            return self.get_hook_priority(hook)
        
        sorted_hooks = sorted(hooks, key=hook_sort_key)
        
        # Логируем изменения
        if sorted_hooks != hooks:
            logger.info("Hook order changed:")
            logger.info(f"  Before: {' '.join(hooks)}")
            logger.info(f"  After: {' '.join(sorted_hooks)}")
        
        return sorted_hooks
    
    def sort_modules_by_priority(self, modules: List[str]) -> List[str]:
        """Отсортировать модули по приоритету"""
        def module_sort_key(module):
            return self.get_module_priority(module)
        
        sorted_modules = sorted(modules, key=module_sort_key)
        
        if sorted_modules != modules:
            logger.info("Module order changed:")
            logger.info(f"  Before: {' '.join(modules)}")
            logger.info(f"  After: {' '.join(sorted_modules)}")
        
        return sorted_modules
    
    def resolve_position_conflict(self, hooks: List[str], new_hook: str, 
                                 after_hook: str = None, before_hook: str = None) -> int:
        """Умное разрешение конфликтов позиций с учетом правил"""
        
        # Если нет конфликта - используем обычную логику
        after_pos = hooks.index(after_hook) + 1 if after_hook and after_hook in hooks else 0
        before_pos = hooks.index(before_hook) if before_hook and before_hook in hooks else len(hooks)
        
        if after_pos <= before_pos:
            return after_pos
        
        logger.warning(f"Position conflict for {new_hook}: after {after_hook} ({after_pos-1}) and before {before_hook} ({before_pos})")
        
        # Используем приоритеты для разрешения конфликта
        new_hook_priority = self.get_hook_priority(new_hook)
        
        # Ищем подходящую позицию рядом с хуками похожего приоритета
        best_pos = len(hooks)  # По умолчанию в конец
        
        for i, hook in enumerate(hooks):
            hook_priority = self.get_hook_priority(hook)
            
            # Если нашли хук с большим приоритетом (позже в порядке)
            if hook_priority > new_hook_priority:
                best_pos = i
                break
        
        logger.info(f"Conflict resolved: {new_hook} placed at position {best_pos} based on priority {new_hook_priority}")
        return best_pos
    
    def suggest_hook_placement(self, hooks: List[str], new_hook: str) -> Dict:
        """Предложить лучшее место для нового хука"""
        priority = self.get_hook_priority(new_hook)
        dependencies = self.hook_dependencies.get(new_hook, {})
        
        # Находим рекомендуемую позицию
        recommended_pos = len(hooks)
        for i, hook in enumerate(hooks):
            if self.get_hook_priority(hook) > priority:
                recommended_pos = i
                break
        
        # Проверяем зависимости
        constraints = []
        
        for required_before in dependencies.get("must_be_after", []):
            if required_before in hooks:
                min_pos = hooks.index(required_before) + 1
                constraints.append(f"после {required_before} (позиция >= {min_pos})")
                recommended_pos = max(recommended_pos, min_pos)
        
        for required_after in dependencies.get("must_be_before", []):
            if required_after in hooks:
                max_pos = hooks.index(required_after)
                constraints.append(f"до {required_after} (позиция < {max_pos})")
                recommended_pos = min(recommended_pos, max_pos)
        
        return {
            "position": recommended_pos,
            "priority": priority,
            "constraints": constraints,
            "description": dependencies.get("description", f"Приоритет {priority}")
        }
