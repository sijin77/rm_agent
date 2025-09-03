"""
🗑️ СКРИПТ ОЧИСТКИ БАЗЫ ДАННЫХ
=============================

Удаляет файл базы данных для полного пересоздания.
Используйте когда нужно начать заново.

Автор: Ириска 💖
"""
from app.utils import logger

import os
from pathlib import Path

def reset_database():
    """Удаляет файл базы данных SQLite"""
    
    db_path = Path("data/rm_agent.db")
    
    if db_path.exists():
        try:
            os.remove(db_path)
            print("✅ База данных удалена:", db_path)
            logger.info("🚀 Теперь можно запустить: python setup_database.py")
        except Exception as e:
            logger.info("❌ Ошибка при удалении БД: {e}")
    else:
        print("ℹ️ Файл базы данных не найден:", db_path)
        logger.info("🚀 Можно сразу запустить: python setup_database.py")

if __name__ == "__main__":
    logger.info("🗑️ Сброс базы данных RM Agent...")
    reset_database()
