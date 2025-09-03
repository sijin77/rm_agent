"""
Скрипт для очистки логов во всех скриптах
"""
import os
import re
from pathlib import Path

def cleanup_file(file_path):
    """Очистка логов в одном файле"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Добавляем импорт logger если его нет
        if 'from app.utils import logger' not in content and 'print(' in content:
            # Находим место для импорта
            import_match = re.search(r'from app\.', content)
            if import_match:
                content = content[:import_match.start()] + 'from app.utils import logger\n' + content[import_match.start():]
            else:
                # Добавляем в начало после docstring
                docstring_end = content.find('"""', content.find('"""') + 3) + 3
                if docstring_end > 2:
                    content = content[:docstring_end] + '\nfrom app.utils import logger' + content[docstring_end:]
        
        # Замены для print на logger
        replacements = [
            # Обычные информационные сообщения
            (r'print\(f?"([^"]*)"\)', r'logger.info("\1")'),
            (r'print\(f?"✅ ([^"]*)"\)', r'logger.success("\1")'),
            (r'print\(f?"❌ ([^"]*)"\)', r'logger.error("\1")'),
            (r'print\(f?"⚠️  ([^"]*)"\)', r'logger.warning("\1")'),
            (r'print\(f?"🔍 ([^"]*)"\)', r'logger.warning("\1")'),
            (r'print\(f?"📊 ([^"]*)"\)', r'logger.info("\1")'),
            (r'print\(f?"📋 ([^"]*)"\)', r'logger.info("\1")'),
            (r'print\(f?"🎯 ([^"]*)"\)', r'logger.info("\1")'),
            (r'print\(f?"🎉 ([^"]*)"\)', r'logger.success("\1")'),
            (r'print\(f?"💾 ([^"]*)"\)', r'logger.info("\1")'),
            (r'print\(f?"👥 ([^"]*)"\)', r'logger.info("\1")'),
            (r'print\(f?"🔑 ([^"]*)"\)', r'logger.info("\1")'),
            (r'print\(f?"📝 ([^"]*)"\)', r'logger.info("\1")'),
            (r'print\(f?"🏢 ([^"]*)"\)', r'logger.info("\1")'),
            (r'print\(f?"💻 ([^"]*)"\)', r'logger.info("\1")'),
            (r'print\(f?"🧠 ([^"]*)"\)', r'logger.info("\1")'),
            (r'print\(f?"👨‍💼 ([^"]*)"\)', r'logger.info("\1")'),
            (r'print\(f?"🎲 ([^"]*)"\)', r'logger.info("\1")'),
            (r'print\(f?"🖥️ ([^"]*)"\)', r'logger.info("\1")'),
            (r'print\(f?"🌐 ([^"]*)"\)', r'logger.info("\1")'),
            (r'print\(f?"🔄 ([^"]*)"\)', r'logger.info("\1")'),
            (r'print\(f?"ℹ️  ([^"]*)"\)', r'logger.info("\1")'),
        ]
        
        for pattern, replacement in replacements:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        
        # Если файл изменился, сохраняем
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"❌ Ошибка при обработке {file_path}: {e}")
        return False

def cleanup_all_scripts():
    """Очистка логов во всех скриптах"""
    scripts_dir = Path("scripts")
    
    if not scripts_dir.exists():
        print("❌ Папка scripts не найдена")
        return
    
    cleaned_files = []
    
    for file_path in scripts_dir.glob("*.py"):
        if file_path.name in ["__init__.py", "cleanup_logs.py"]:
            continue
            
        print(f"🔄 Обрабатываем {file_path.name}...")
        if cleanup_file(file_path):
            cleaned_files.append(file_path.name)
            print(f"✅ {file_path.name} очищен")
        else:
            print(f"ℹ️  {file_path.name} не требует изменений")
    
    print(f"\n🎉 Обработано {len(cleaned_files)} файлов:")
    for file_name in cleaned_files:
        print(f"   • {file_name}")

if __name__ == "__main__":
    cleanup_all_scripts()
