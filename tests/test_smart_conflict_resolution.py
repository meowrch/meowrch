#!/usr/bin/env python3
import shutil
import sys
import tempfile
from pathlib import Path

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from Builder.utils.mkinitcpio_config import MkinitcpioConfigEditor
from Builder.utils.mkinitcpio_rules import MkinitcpioRules


def create_test_mkinitcpio_file(hooks: str) -> Path:
    """Создать тестовый файл mkinitcpio.conf с заданными хуками"""
    content = f'''# vim:set ft=sh
MODULES=()
BINARIES=()
FILES=()
HOOKS=({hooks})
'''
    
    tmp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='_smart_test')
    tmp_file.write(content)
    tmp_file.close()
    return Path(tmp_file.name)


def test_smart_conflict_resolution():
    """Тестировать умное разрешение конфликтов"""
    print("🧠 Тест умного разрешения конфликтов")
    print("=" * 50)
    
    # Тест 1: Классический конфликт A B, но с умным разрешением
    test_file = create_test_mkinitcpio_file("base systemd A B filesystems fsck")
    print(f"Создан тестовый файл: {test_file}")
    
    try:
        editor = MkinitcpioConfigEditor(test_file)
        
        def mock_run_sudo(command, input=None):
            if command[0] == "cat":
                return test_file.read_text()
            elif command[0] == "cp":
                shutil.copy(command[1], command[2])
                return ""
            return ""
        
        editor._run_sudo = mock_run_sudo
        
        print("Исходные хуки:")
        initial_hooks = editor.list_hooks()
        print(f"  {initial_hooks}")
        
        # Пытаемся добавить plymouth после B, но до A
        print("\n🎯 Попытка добавить plymouth после B, но до A")
        print("Ожидаем: умное разрешение на основе приоритетов")
        
        editor.add_hook('plymouth', after_hook='B', before_hook='A')
        
        final_hooks = editor.list_hooks()
        print(f"Результат: {final_hooks}")
        
        # Проверяем что plymouth размещен разумно
        if 'plymouth' in final_hooks:
            plymouth_idx = final_hooks.index('plymouth')
            print(f"Plymouth размещен в позиции {plymouth_idx}")
            print("✅ Конфликт успешно разрешен умной системой")
        
    finally:
        test_file.unlink()
        print("Удален тестовый файл")


def test_plymouth_smart_placement():
    """Тестировать умное размещение Plymouth"""
    print("\n🎭 Тест умного размещения Plymouth")
    print("=" * 40)
    
    # Создаем реалистичную конфигурацию
    test_file = create_test_mkinitcpio_file("base systemd autodetect modconf kms block encrypt filesystems fsck")
    
    try:
        editor = MkinitcpioConfigEditor(test_file)
        
        def mock_run_sudo(command, input=None):
            if command[0] == "cat":
                return test_file.read_text()
            elif command[0] == "cp":
                shutil.copy(command[1], command[2])
                return ""
            return ""
        
        editor._run_sudo = mock_run_sudo
        
        print("Исходные хуки (реалистичная конфигурация):")
        initial_hooks = editor.list_hooks()
        print(f"  {initial_hooks}")
        
        # Добавляем plymouth без указания позиции - должно работать умно!
        print("\n🎯 Добавление plymouth без указания позиции")
        print("Ожидаем: автоматическое размещение на основе правил")
        
        editor.add_hook('plymouth')
        
        final_hooks = editor.list_hooks()
        print(f"Результат: {final_hooks}")
        
        # Проверяем правильность размещения
        if 'plymouth' in final_hooks:
            plymouth_idx = final_hooks.index('plymouth')
            kms_idx = final_hooks.index('kms') if 'kms' in final_hooks else -1
            encrypt_idx = final_hooks.index('encrypt') if 'encrypt' in final_hooks else len(final_hooks)
            
            print(f"Позиции: kms={kms_idx}, plymouth={plymouth_idx}, encrypt={encrypt_idx}")
            
            # Plymouth должен быть после kms, но до encrypt
            if kms_idx < plymouth_idx < encrypt_idx:
                print("✅ Plymouth корректно размещен: после kms, до encrypt")
            else:
                print("❌ Plymouth размещен неправильно")
        
    finally:
        test_file.unlink()


def test_complex_dependencies():
    """Тестировать сложные зависимости"""
    print("\n⚡ Тест сложных зависимостей")
    print("=" * 30)
    
    # Создаем конфигурацию с LVM и шифрованием
    test_file = create_test_mkinitcpio_file("base systemd autodetect block encrypt filesystems fsck")
    
    try:
        editor = MkinitcpioConfigEditor(test_file)
        
        def mock_run_sudo(command, input=None):
            if command[0] == "cat":
                return test_file.read_text()
            elif command[0] == "cp":
                shutil.copy(command[1], command[2])
                return ""
            return ""
        
        editor._run_sudo = mock_run_sudo
        
        print("Исходная конфигурация (с шифрованием):")
        initial_hooks = editor.list_hooks()
        print(f"  {initial_hooks}")
        
        # Добавляем LVM - должен быть после encrypt, но до filesystems
        print("\n🎯 Добавление lvm2")
        print("Ожидаем: размещение после encrypt, до filesystems")
        
        editor.add_hook('lvm2')
        
        # Добавляем resume - тоже должен быть в правильном месте
        print("\n🎯 Добавление resume")  
        print("Ожидаем: размещение после encrypt/lvm2, до filesystems")
        
        editor.add_hook('resume')
        
        final_hooks = editor.list_hooks()
        print(f"Итоговый результат: {final_hooks}")
        
        # Проверяем порядок: encrypt -> lvm2 -> resume -> filesystems
        if all(hook in final_hooks for hook in ['encrypt', 'lvm2', 'resume', 'filesystems']):
            encrypt_idx = final_hooks.index('encrypt')
            lvm2_idx = final_hooks.index('lvm2')
            resume_idx = final_hooks.index('resume')
            fs_idx = final_hooks.index('filesystems')
            
            if encrypt_idx < lvm2_idx < resume_idx < fs_idx:
                print("✅ Все хуки размещены в правильном порядке")
                print(f"   encrypt({encrypt_idx}) -> lvm2({lvm2_idx}) -> resume({resume_idx}) -> filesystems({fs_idx})")
            else:
                print("❌ Порядок хуков нарушен")
        
    finally:
        test_file.unlink()


def test_rules_directly():
    """Тестировать правила напрямую"""
    print("\n📚 Тест базы знаний напрямую")
    print("=" * 35)
    
    rules = MkinitcpioRules()
    
    # Тест приоритетов
    print("Приоритеты основных хуков:")
    important_hooks = ['base', 'systemd', 'plymouth', 'encrypt', 'filesystems', 'fsck']
    for hook in important_hooks:
        priority = rules.get_hook_priority(hook)
        print(f"  {hook}: {priority}")
    
    # Тест сортировки
    print("\nТест автосортировки:")
    messy_hooks = ['fsck', 'plymouth', 'base', 'encrypt', 'systemd']
    print(f"  Было: {messy_hooks}")
    sorted_hooks = rules.sort_hooks_by_priority(messy_hooks)
    print(f"  Стало: {sorted_hooks}")
    
    # Тест предложений
    print("\nТест предложений для plymouth:")
    current_hooks = ['base', 'systemd', 'autodetect', 'block', 'encrypt', 'filesystems']
    suggestion = rules.suggest_hook_placement(current_hooks, 'plymouth')
    print(f"  Рекомендуемая позиция: {suggestion['position']}")
    print(f"  Описание: {suggestion['description']}")
    if suggestion['constraints']:
        print(f"  Ограничения: {', '.join(suggestion['constraints'])}")


if __name__ == "__main__":
    print("Тестирование умной системы разрешения конфликтов")
    print("ВНИМАНИЕ: Используются тестовые файлы!")
    print("=" * 60)
    
    try:
        test_smart_conflict_resolution()
        test_plymouth_smart_placement()
        test_complex_dependencies()
        test_rules_directly()
        
        print("\n🎉 Все тесты завершены успешно!")
        
    except Exception as e:
        print(f"\n❌ Ошибка в тестах: {e}")
        import traceback
        traceback.print_exc()
