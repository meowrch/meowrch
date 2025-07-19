import re
import tempfile
import subprocess
from pathlib import Path
from typing import List, Optional, Set
from loguru import logger


class GrubConfigEditor:
    """Утилита для редактирования конфигурации GRUB"""
    
    def __init__(self, grub_path: Path = Path("/etc/default/grub")):
        self.grub_path = grub_path
    
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
    
    def add_cmdline_params(self, params: Set[str], update_grub: bool = True) -> bool:
        """
        Добавить параметры в GRUB_CMDLINE_LINUX_DEFAULT
        
        Args:
            params: Набор параметров для добавления
            update_grub: Запустить update-grub после изменений
            
        Returns:
            bool: True если были внесены изменения
        """
        changes_made = False
        
        def edit_grub(tmp_path: Path):
            nonlocal changes_made
            content = tmp_path.read_text()
            match = re.search(
                r'^(GRUB_CMDLINE_LINUX_DEFAULT=)(["\']?)((?:\\.|[^"\'])*?)\2(\s*(#.*)?)$',
                content,
                re.MULTILINE
            )

            if not match:
                logger.error("GRUB_CMDLINE_LINUX_DEFAULT не найден или неверный формат")
                return

            current_params = set(match.group(3).split()) if match.group(3) else set()
            missing_params = params - current_params

            if missing_params:
                all_params = current_params | missing_params
                new_params_str = " ".join(sorted(all_params))
                new_line = f'GRUB_CMDLINE_LINUX_DEFAULT="{new_params_str}"'
                
                if match.group(5):  # Есть комментарий
                    new_line += match.group(5)
                
                content = content.replace(match.group(0), new_line)
                tmp_path.write_text(content)
                changes_made = True
                logger.info(f"Добавлены параметры: {', '.join(missing_params)}")

        logger.info("Обновление параметров GRUB...")
        self._safe_file_edit(self.grub_path, edit_grub)
        
        if changes_made and update_grub:
            logger.info("Запуск update-grub...")
            self._run_sudo(["update-grub"])
            
        return changes_made
    
    def remove_cmdline_params(self, params: Set[str], update_grub: bool = True) -> bool:
        """
        Удалить параметры из GRUB_CMDLINE_LINUX_DEFAULT
        
        Args:
            params: Набор параметров для удаления
            update_grub: Запустить update-grub после изменений
            
        Returns:
            bool: True если были внесены изменения
        """
        changes_made = False
        
        def edit_grub(tmp_path: Path):
            nonlocal changes_made
            content = tmp_path.read_text()
            match = re.search(
                r'^(GRUB_CMDLINE_LINUX_DEFAULT=)(["\']?)((?:\\.|[^"\'])*?)\2(\s*(#.*)?)$',
                content,
                re.MULTILINE
            )

            if not match:
                logger.error("GRUB_CMDLINE_LINUX_DEFAULT не найден или неверный формат")
                return

            current_params = set(match.group(3).split()) if match.group(3) else set()
            params_to_remove = params & current_params

            if params_to_remove:
                remaining_params = current_params - params_to_remove
                new_params_str = " ".join(sorted(remaining_params))
                new_line = f'GRUB_CMDLINE_LINUX_DEFAULT="{new_params_str}"'
                
                if match.group(5):  # Есть комментарий
                    new_line += match.group(5)
                
                content = content.replace(match.group(0), new_line)
                tmp_path.write_text(content)
                changes_made = True
                logger.info(f"Удалены параметры: {', '.join(params_to_remove)}")

        logger.info("Удаление параметров GRUB...")
        self._safe_file_edit(self.grub_path, edit_grub)
        
        if changes_made and update_grub:
            logger.info("Запуск update-grub...")
            self._run_sudo(["update-grub"])
            
        return changes_made
    
    def get_cmdline_params(self) -> Set[str]:
        """Получить текущие параметры из GRUB_CMDLINE_LINUX_DEFAULT"""
        try:
            content = self._run_sudo(["cat", str(self.grub_path)])
            match = re.search(
                r'^GRUB_CMDLINE_LINUX_DEFAULT=(["\']?)((?:\\.|[^"\'])*?)\1',
                content,
                re.MULTILINE
            )
            
            if match:
                return set(match.group(2).split()) if match.group(2) else set()
            else:
                logger.warning("GRUB_CMDLINE_LINUX_DEFAULT не найден")
                return set()
        except Exception as e:
            logger.error(f"Ошибка при чтении конфигурации GRUB: {e}")
            return set()
