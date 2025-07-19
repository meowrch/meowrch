import re
import tempfile
import subprocess
from pathlib import Path
from typing import List, Optional, Set
from enum import Enum
from loguru import logger
from .mkinitcpio_rules import MkinitcpioRules


class Position(Enum):
    """Позиции для вставки элементов"""
    START = "start"
    END = "end"
    BEFORE = "before"
    AFTER = "after"


class MkinitcpioConfigEditor:
    """Утилита для редактирования конфигурации mkinitcpio"""

    def __init__(self, mkinitcpio_path: Path = Path("/etc/mkinitcpio.conf")):
        self.mkinitcpio_path = mkinitcpio_path
        self.rules = MkinitcpioRules()  # База знаний о правильном порядке

    def _run_sudo(self, command: List[str], input: Optional[str] = None) -> str:
        """Выполнить команду с sudo"""
        result = subprocess.run(
            ["sudo"] + command,
            input=input,
            text=True,
            capture_output=True,
            check=True,
        )
        return result.stdout

    def _safe_file_edit(self, path: Path, edit_callback: callable):
        """Безопасно редактировать файл через временный файл"""
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp:
            original_content = self._run_sudo(["cat", str(path)])
            tmp.write(original_content)
            tmp.flush()

            edit_callback(Path(tmp.name))
            if Path(tmp.name).read_text() != original_content:
                self._run_sudo(["cp", tmp.name, str(path)])

    def _calculate_insert_position(self, hooks: List[str], new_hook: str, position: Optional[str] = None, 
                                  reference_hook: Optional[str] = None, after_hook: Optional[str] = None, 
                                  before_hook: Optional[str] = None) -> int:
        """Умное вычисление позиции для вставки с учетом правил
        
        Args:
            hooks: Текущий список хуков
            new_hook: Новый хук для добавления
            position: Базовая позиция ('start', 'end', 'before', 'after')
            reference_hook: Референсный хук для position
            after_hook: Хук, после которого нужно вставить
            before_hook: Хук, до которого нужно вставить
            
        Returns:
            int: Оптимальная позиция для вставки
        """
        # Если указаны конкретные ограничения after/before
        if after_hook or before_hook:
            # Используем базу знаний для разрешения конфликтов
            return self.rules.resolve_position_conflict(hooks, new_hook, after_hook, before_hook)
        
        # Обычная логика position + reference_hook
        if position == "before" and reference_hook and reference_hook in hooks:
            return hooks.index(reference_hook)
        elif position == "after" and reference_hook and reference_hook in hooks:
            return hooks.index(reference_hook) + 1
        elif position == "start":
            return 0
        elif position == "end":
            return len(hooks)
        else:
            # По умолчанию используем рекомендации из базы знаний
            suggestion = self.rules.suggest_hook_placement(hooks, new_hook)
            logger.info(f"Использована рекомендация для {new_hook}: {suggestion['description']}")
            return suggestion['position']

    def add_hook(self, hook: str, position: Optional[str] = None, reference_hook: Optional[str] = None,
                 after_hook: Optional[str] = None, before_hook: Optional[str] = None):
        """Добавить хук в конфигурацию mkinitcpio
        
        Args:
            hook: Название хука для добавления
            position: Базовая позиция ('start', 'end', 'before', 'after')
            reference_hook: Референсный хук для position
            after_hook: Хук, после которого нужно вставить (приоритет над position)
            before_hook: Хук, до которого нужно вставить (работает вместе с after_hook)
        """

        def edit_mkinitcpio(tmp_path: Path):
            content = tmp_path.read_text()
            match = re.search(r"^HOOKS=\((.*?)\)", content, re.M)

            if not match:
                logger.error("HOOKS не найдены в mkinitcpio.conf")
                return

            hooks = match.group(1).split()

            if hook in hooks:
                logger.info(f"Хук {hook} уже существует в конфигурации")
                return

            # Определяем позицию для вставки
            insert_index = self._calculate_insert_position(
                hooks, hook, position, reference_hook, after_hook, before_hook
            )
            
            hooks.insert(insert_index, hook)
            new_hooks_str = f"HOOKS=({' '.join(hooks)})"
            tmp_path.write_text(content.replace(match.group(0), new_hooks_str))

        logger.info("Добавление хука в mkinitcpio.conf...")
        self._safe_file_edit(self.mkinitcpio_path, edit_mkinitcpio)
        logger.success("Хук успешно добавлен!")

    def remove_hook(self, hook: str):
        """Удалить хук из конфигурации mkinitcpio"""

        def edit_mkinitcpio(tmp_path: Path):
            content = tmp_path.read_text()
            match = re.search(r"^HOOKS=\((.*?)\)", content, re.M)

            if not match:
                logger.error("HOOKS не найдены в mkinitcpio.conf")
                return

            hooks = match.group(1).split()

            if hook not in hooks:
                logger.info(f"Хук {hook} не найден в конфигурации")
                return

            hooks.remove(hook)

            new_hooks_str = f"HOOKS=({' '.join(hooks)})"
            tmp_path.write_text(content.replace(match.group(0), new_hooks_str))

        logger.info("Удаление хука из mkinitcpio.conf...")
        self._safe_file_edit(self.mkinitcpio_path, edit_mkinitcpio)
        logger.success("Хук успешно удален!")

    def list_hooks(self) -> List[str]:
        """Получить текущий список хуков из mkinitcpio.conf"""
        try:
            content = self._run_sudo(["cat", str(self.mkinitcpio_path)])
            match = re.search(r"^HOOKS=\((.*?)\)", content, re.M)

            if match:
                return match.group(1).split()
            else:
                logger.warning("HOOKS не найдены в mkinitcpio.conf")
                return []
        except Exception as e:
            logger.error(f"Ошибка при чтении mkinitcpio.conf: {e}")
            return []

    def add_modules(self, modules: List[str], position: Position = Position.END, reference_module: Optional[str] = None) -> bool:
        """Добавить модули в конфигурацию mkinitcpio
        
        Args:
            modules: Список модулей для добавления
            position: Позиция вставки (START, END, BEFORE, AFTER)
            reference_module: Референсный модуль для позиций BEFORE/AFTER
            
        Returns:
            bool: True если были внесены изменения
        """
        changes_made = False
        
        def edit_modules(tmp_path: Path):
            nonlocal changes_made
            content = tmp_path.read_text()
            
            # Ищем строку MODULES
            match = re.search(r'^(#?\s*)(MODULES=)(\(.*?\))', content, re.M | re.S)
            
            if not match:
                logger.warning("MODULES не найдены в mkinitcpio.conf, создаем новую строку")
                # Добавляем новую строку MODULES в конец файла
                modules_str = ' '.join(modules)
                content += f"\nMODULES=({modules_str})\n"
                tmp_path.write_text(content)
                changes_made = True
                return
            
            # Если строка закомментирована, убираем комментарий
            is_commented = match.group(1).strip().startswith('#')
            
            # Извлекаем текущие модули
            modules_content = match.group(3)[1:-1].strip()  # Убираем скобки
            current_modules = [m.strip() for m in modules_content.split() if m.strip()]
            
            # Добавляем только новые модули
            new_modules = [m for m in modules if m not in current_modules]
            if not new_modules:
                logger.info("Все указанные модули уже присутствуют в конфигурации")
                return
            
            # Определяем позицию вставки
            if position == Position.BEFORE and reference_module and reference_module in current_modules:
                index = current_modules.index(reference_module)
                for i, module in enumerate(new_modules):
                    current_modules.insert(index + i, module)
            elif position == Position.AFTER and reference_module and reference_module in current_modules:
                index = current_modules.index(reference_module) + 1
                for i, module in enumerate(new_modules):
                    current_modules.insert(index + i, module)
            elif position == Position.START:
                current_modules = new_modules + current_modules
            else:  # Position.END
                current_modules.extend(new_modules)
            
            # Формируем новую строку
            modules_str = ' '.join(current_modules)
            new_line = f"MODULES=({modules_str})"
            
            # Заменяем в контенте
            tmp_path.write_text(content.replace(match.group(0), new_line))
            changes_made = True
            logger.info(f"Добавлены модули: {', '.join(new_modules)}")
        
        logger.info("Добавление модулей в mkinitcpio.conf...")
        self._safe_file_edit(self.mkinitcpio_path, edit_modules)
        return changes_made
    
    def remove_modules(self, modules: List[str]) -> bool:
        """Удалить модули из конфигурации mkinitcpio
        
        Args:
            modules: Список модулей для удаления
            
        Returns:
            bool: True если были внесены изменения
        """
        changes_made = False
        
        def edit_modules(tmp_path: Path):
            nonlocal changes_made
            content = tmp_path.read_text()
            
            # Ищем строку MODULES
            match = re.search(r'^(#?\s*)(MODULES=)(\(.*?\))', content, re.M | re.S)
            
            if not match:
                logger.warning("MODULES не найдены в mkinitcpio.conf")
                return
            
            # Извлекаем текущие модули
            modules_content = match.group(3)[1:-1].strip()  # Убираем скобки
            current_modules = [m.strip() for m in modules_content.split() if m.strip()]
            
            # Удаляем указанные модули
            modules_to_remove = [m for m in modules if m in current_modules]
            if not modules_to_remove:
                logger.info("Указанные модули не найдены в конфигурации")
                return
            
            remaining_modules = [m for m in current_modules if m not in modules]
            
            # Формируем новую строку
            modules_str = ' '.join(remaining_modules)
            new_line = f"MODULES=({modules_str})"
            
            # Заменяем в контенте
            tmp_path.write_text(content.replace(match.group(0), new_line))
            changes_made = True
            logger.info(f"Удалены модули: {', '.join(modules_to_remove)}")
        
        logger.info("Удаление модулей из mkinitcpio.conf...")
        self._safe_file_edit(self.mkinitcpio_path, edit_modules)
        return changes_made
    
    def list_modules(self) -> List[str]:
        """Получить текущий список модулей из mkinitcpio.conf"""
        try:
            content = self._run_sudo(["cat", str(self.mkinitcpio_path)])
            match = re.search(r'^#?\s*MODULES=\((.*?)\)', content, re.M | re.S)
            
            if match:
                modules_content = match.group(1).strip()
                return [m.strip() for m in modules_content.split() if m.strip()]
            else:
                logger.warning("MODULES не найдены в mkinitcpio.conf")
                return []
        except Exception as e:
            logger.error(f"Ошибка при чтении mkinitcpio.conf: {e}")
            return []
    
    def bulk_add_hooks(self, hooks_config: List[dict], rebuild: bool = True) -> bool:
        """Массово добавить хуки с настройками позиций
        
        Args:
            hooks_config: Список конфигураций хуков в формате:
                [{'hook': 'hook_name', 'position': 'before', 'reference': 'other_hook'}, ...]
            rebuild: Запустить mkinitcpio -P после всех изменений
            
        Returns:
            bool: True если были внесены изменения
        """
        changes_made = False
        
        for config in hooks_config:
            hook = config['hook']
            position = config.get('position', 'end')
            reference = config.get('reference')
            
            try:
                self.add_hook(hook, position, reference)
                changes_made = True
            except Exception as e:
                logger.error(f"Ошибка при добавлении хука {hook}: {e}")
        
        if changes_made and rebuild:
            self.apply_hooks()
        
        return changes_made
    
    def apply_hooks(self):
        """Запустить mkinitcpio -P для применения изменений"""
        logger.info("Применение изменений mkinitcpio...")
        self._run_sudo(["mkinitcpio", "-P"])
        logger.success("Изменения успешно применены!")

