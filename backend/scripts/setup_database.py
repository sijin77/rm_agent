"""
🚀 МАСТЕР-СКРИПТ ЗАПОЛНЕНИЯ БАЗЫ ДАННЫХ RM AGENT
===================================================

Этот скрипт выполняет полное заполнение базы данных в правильной последовательности:
1. Создание таблиц
2. Заполнение справочников и организационной структуры
3. Создание корпоративных систем и ролей
4. Создание базовых ролевых моделей
5. Генерация 2000 сотрудников
6. Генерация доступов сотрудников (24k+ записей)

Автор: Ириска 💖
Дата: Декабрь 2024
"""

import asyncio
import sys
from pathlib import Path

# Добавляем путь к модулям приложения
sys.path.append(str(Path(__file__).parent))

from app.core.database import create_tables
from app.utils import logger


async def setup_complete_database():
    """
    🎯 ПОЛНОЕ ЗАПОЛНЕНИЕ БАЗЫ ДАННЫХ
    
    Выполняет все этапы создания и заполнения БД для RM Agent
    """
    
    logger.section("ПОЛНОЕ ЗАПОЛНЕНИЕ БАЗЫ ДАННЫХ RM AGENT")
    
    try:
        # ============================================================
        # ЭТАП 1: СОЗДАНИЕ СТРУКТУРЫ БД
        # ============================================================
        logger.step("ЭТАП 1", "Создание структуры базы данных...")
        
        await create_tables()
        logger.success("Таблицы базы данных созданы")
        
        # ============================================================
        # ЭТАП 2: СПРАВОЧНИКИ И ОРГАНИЗАЦИОННАЯ СТРУКТУРА
        # ============================================================
        logger.step("ЭТАП 2", "Заполнение справочников и орг.структуры...")
        
        # Импортируем и выполняем заполнение справочников
        from scripts.populate_data import (
            populate_positions, populate_employee_types, populate_team_roles,
            populate_employee_profiles, populate_organizational_structure,
            populate_agile_structure
        )
        
        logger.info("Заполняем справочник должностей...")
        await populate_positions()
        
        logger.info("Заполняем типы сотрудников...")
        await populate_employee_types()
        
        logger.info("Заполняем роли в командах...")
        await populate_team_roles()
        
        logger.info("Заполняем профили сотрудников...")
        await populate_employee_profiles()
        
        logger.info("Создаем организационную структуру...")
        await populate_organizational_structure()
        
        logger.info("Создаем Agile структуру...")
        await populate_agile_structure()
        
        logger.success("Справочники и структуры созданы")
        
        # ============================================================
        # ЭТАП 3: КОРПОРАТИВНЫЕ СИСТЕМЫ И РОЛИ
        # ============================================================
        logger.step("ЭТАП 3", "Создание корпоративных систем...")
        
        from scripts.generate_systems import generate_application_systems
        
        logger.info("Генерируем 36 корпоративных систем и 145 ролей...")
        await generate_application_systems()
        
        logger.success("Корпоративные системы созданы")
        
        # ============================================================
        # ЭТАП 4: БАЗОВЫЕ РОЛЕВЫЕ МОДЕЛИ
        # ============================================================
        logger.step("ЭТАП 4", "Создание базовых ролевых моделей...")
        
        from scripts.create_role_models import create_base_role_models
        
        logger.info("Создаем 5 базовых ролевых моделей для ML...")
        await create_base_role_models()
        
        logger.success("Базовые ролевые модели созданы")
        
        # ============================================================
        # ЭТАП 5: ГЕНЕРАЦИЯ СОТРУДНИКОВ
        # ============================================================
        logger.step("ЭТАП 5", "Генерация сотрудников...")
        
        from scripts.generate_employees import generate_employees
        
        logger.info("Генерируем 2000 реалистичных сотрудников...")
        await generate_employees()
        
        logger.success("Сотрудники созданы")
        
        # ============================================================
        # ЭТАП 6: ГЕНЕРАЦИЯ ДОСТУПОВ
        # ============================================================
        logger.step("ЭТАП 6", "Генерация доступов сотрудников...")
        
        from scripts.generate_employee_accesses import (
            generate_employee_accesses, show_statistics
        )
        
        logger.info("Генерируем доступы с логикой ролевых моделей...")
        logger.info("   • Базовые доступы для всех")
        logger.info("   • Логичные доступы по профилю/должности") 
        logger.info("   • Случайные дополнительные доступы")
        logger.info("   • 5% шума для реалистичности")
        
        await generate_employee_accesses()
        
        logger.info("Показываем финальную статистику...")
        await show_statistics()
        
        logger.success("Доступы сотрудников созданы")
        
        # ============================================================
        # ФИНАЛ: УСПЕШНОЕ ЗАВЕРШЕНИЕ
        # ============================================================
        logger.section("БАЗА ДАННЫХ ПОЛНОСТЬЮ ГОТОВА К РАБОТЕ!")
        
        logger.info("ИТОГОВАЯ СТАТИСТИКА:")
        logger.info("   • 2000 сотрудников")
        logger.info("   • 36 корпоративных систем")
        logger.info("   • 145 ролей в системах")
        logger.info("   • 5 базовых ролевых моделей")
        logger.info("   • ~150k доступов (75% авто + 25% ручных)")
        logger.info("   • Полная орг.структура (5 блоков)")
        logger.info("   • Agile структура (трайбы/продукты/команды)")
        
        logger.success("Можно запускать API и начинать работу с ML!")
        logger.info("   Команда запуска: python -m app.main")
        
    except Exception as e:
        logger.error(f"ОШИБКА ПРИ ЗАПОЛНЕНИИ БД: {e}")
        logger.warning("Проверьте логи выше для диагностики")
        raise


if __name__ == "__main__":
    logger.step("Запуск", "мастер-скрипта заполнения БД...")
    asyncio.run(setup_complete_database())
