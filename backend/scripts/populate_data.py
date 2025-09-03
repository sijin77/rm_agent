"""
Скрипт для предзаполнения справочников данными
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils import logger
from app.core.database import AsyncSessionLocal, create_tables
from app.models import (
    OrganizationalUnit, Position, EmployeeProfile, EmployeeType, TeamRole,
    Tribe, Product, AgileTeam, ApplicationSystem, Access
)


async def populate_positions():
    """Заполнение справочника должностей"""
    async with AsyncSessionLocal() as session:
        positions_data = [
            # Базовые должности
            {"title": "Инженер", "hierarchy_level": 1, "description": "Базовая инженерная должность"},
            {"title": "Главный инженер", "hierarchy_level": 2, "description": "Старшая инженерная должность"},
            {"title": "Эксперт", "hierarchy_level": 3, "description": "Экспертная должность"},
            {"title": "Менеджер", "hierarchy_level": 4, "description": "Управленческая должность"},
            
            # Дополнительные должности
            {"title": "Специалист", "hierarchy_level": 1, "description": "Базовая должность специалиста"},
            {"title": "Ведущий специалист", "hierarchy_level": 2, "description": "Опытный специалист"},
            {"title": "Главный специалист", "hierarchy_level": 3, "description": "Старший специалист"},
            {"title": "Консультант", "hierarchy_level": 3, "description": "Консультирующая должность"},
            {"title": "Старший консультант", "hierarchy_level": 4, "description": "Старший консультант"},
            {"title": "Руководитель группы", "hierarchy_level": 4, "description": "Руководитель рабочей группы"},
            {"title": "Заместитель начальника", "hierarchy_level": 5, "description": "Заместитель руководителя отдела"},
            {"title": "Начальник отдела", "hierarchy_level": 6, "description": "Руководитель отдела"},
            {"title": "Заместитель директора", "hierarchy_level": 7, "description": "Заместитель директора департамента"},
            {"title": "Директор", "hierarchy_level": 8, "description": "Директор департамента/блока"},
        ]
        
        for pos_data in positions_data:
            position = Position(**pos_data)
            session.add(position)
        
        await session.commit()
        logger.info("✅ Должности созданы")


async def populate_employee_types():
    """Заполнение типов сотрудников"""
    async with AsyncSessionLocal() as session:
        types_data = [
            {"name": "Внутренний сотрудник"},
            {"name": "Аутстаффер"},
            {"name": "Компания-партнер"},
        ]
        
        for type_data in types_data:
            emp_type = EmployeeType(**type_data)
            session.add(emp_type)
        
        await session.commit()
        logger.info("✅ Типы сотрудников созданы")


async def populate_team_roles():
    """Заполнение ролей в командах"""
    async with AsyncSessionLocal() as session:
        roles_data = [
            {"name": "Developer"},
            {"name": "Tech Lead"},
            {"name": "Team Lead"},
            {"name": "Product Owner"},
            {"name": "Scrum Master"},
            {"name": "Business Analyst"},
            {"name": "System Analyst"},
            {"name": "QA Engineer"},
            {"name": "QA Lead"},
            {"name": "DevOps Engineer"},
            {"name": "UI/UX Designer"},
            {"name": "Architect"},
            {"name": "Data Analyst"},
            {"name": "Data Scientist"},
            {"name": "Security Engineer"},
            {"name": "Project Manager"},
        ]
        
        for role_data in roles_data:
            role = TeamRole(**role_data)
            session.add(role)
        
        await session.commit()
        logger.info("✅ Роли в командах созданы")


async def populate_employee_profiles():
    """Заполнение профилей сотрудников"""
    async with AsyncSessionLocal() as session:
        profiles_data = [
            # IT профили
            "Trainee Разработчик", "Junior Разработчик", "Middle Разработчик", 
            "Senior Разработчик", "Lead Разработчик", "Principal Разработчик",
            
            "Junior Аналитик", "Middle Аналитик", "Senior Аналитик", "Lead Аналитик",
            
            "Junior Тестировщик", "Middle Тестировщик", "Senior Тестировщик", "Lead Тестировщик",
            
            "Junior DevOps", "Middle DevOps", "Senior DevOps", "Lead DevOps",
            
            "Junior Дизайнер", "Middle Дизайнер", "Senior Дизайнер", "Lead Дизайнер",
            
            "Junior Архитектор", "Senior Архитектор", "Principal Архитектор",
            
            "Менеджер проектов", "Senior Менеджер проектов",
            
            # Бизнес профили
            "Junior Эксперт по продажам", "Middle Эксперт по продажам", 
            "Senior Эксперт по продажам", "Lead Эксперт по продажам",
            
            "Junior Бухгалтер", "Middle Бухгалтер", "Senior Бухгалтер", "Главный бухгалтер",
            
            "HR специалист", "Senior HR специалист", "Lead HR специалист",
            
            "Маркетолог", "Senior Маркетолог", "Lead Маркетолог",
            
            "Юрист", "Senior Юрист", "Главный юрист",
        ]
        
        for profile_name in profiles_data:
            profile = EmployeeProfile(name=profile_name)
            session.add(profile)
        
        await session.commit()
        logger.info("✅ Профили сотрудников созданы")


async def populate_organizational_structure():
    """Создание организационной структуры"""
    async with AsyncSessionLocal() as session:
        
        # ===== БЛОКИ (уровень 1) =====
        blocks_data = [
            # ИТ блоки
            {"name": "ИТ-блок", "code": "IT", "unit_type": "block", "level": 1, "path": "/1"},
            {"name": "Блок цифровых технологий", "code": "DIGITAL", "unit_type": "block", "level": 1, "path": "/2"},
            {"name": "Блок информационной безопасности", "code": "SECURITY", "unit_type": "block", "level": 1, "path": "/3"},
            
            # Бизнес блоки
            {"name": "Коммерческий блок", "code": "SALES", "unit_type": "block", "level": 1, "path": "/4"},
            {"name": "Финансовый блок", "code": "FINANCE", "unit_type": "block", "level": 1, "path": "/5"},
        ]
        
        blocks = {}
        for i, block_data in enumerate(blocks_data, 1):
            block_data["id"] = i
            block = OrganizationalUnit(**block_data)
            session.add(block)
            blocks[block_data["name"]] = i
        
        await session.flush()  # Получаем ID блоков
        
        # ===== ДЕПАРТАМЕНТЫ (уровень 2) =====
        departments_data = [
            # ИТ-блок департаменты
            {"name": "Департамент разработки", "code": "DEV", "unit_type": "department", 
             "parent_id": blocks["ИТ-блок"], "level": 2, "path": f"/{blocks['ИТ-блок']}/6"},
            {"name": "Департамент инфраструктуры", "code": "INFRA", "unit_type": "department", 
             "parent_id": blocks["ИТ-блок"], "level": 2, "path": f"/{blocks['ИТ-блок']}/7"},
            {"name": "Департамент аналитики", "code": "ANALYTICS", "unit_type": "department", 
             "parent_id": blocks["ИТ-блок"], "level": 2, "path": f"/{blocks['ИТ-блок']}/8"},
            
            # Блок цифровых технологий
            {"name": "Департамент продуктовой разработки", "code": "PRODUCT_DEV", "unit_type": "department", 
             "parent_id": blocks["Блок цифровых технологий"], "level": 2, "path": f"/{blocks['Блок цифровых технологий']}/9"},
            {"name": "Департамент UX/UI", "code": "DESIGN", "unit_type": "department", 
             "parent_id": blocks["Блок цифровых технологий"], "level": 2, "path": f"/{blocks['Блок цифровых технологий']}/10"},
            {"name": "Департамент мобильной разработки", "code": "MOBILE", "unit_type": "department", 
             "parent_id": blocks["Блок цифровых технологий"], "level": 2, "path": f"/{blocks['Блок цифровых технологий']}/11"},
            
            # Блок информационной безопасности
            {"name": "Департамент кибербезопасности", "code": "CYBER", "unit_type": "department", 
             "parent_id": blocks["Блок информационной безопасности"], "level": 2, "path": f"/{blocks['Блок информационной безопасности']}/12"},
            {"name": "Департамент аудита ИБ", "code": "AUDIT", "unit_type": "department", 
             "parent_id": blocks["Блок информационной безопасности"], "level": 2, "path": f"/{blocks['Блок информационной безопасности']}/13"},
            
            # Коммерческий блок
            {"name": "Департамент продаж", "code": "SALES_DEPT", "unit_type": "department", 
             "parent_id": blocks["Коммерческий блок"], "level": 2, "path": f"/{blocks['Коммерческий блок']}/14"},
            {"name": "Департамент маркетинга", "code": "MARKETING", "unit_type": "department", 
             "parent_id": blocks["Коммерческий блок"], "level": 2, "path": f"/{blocks['Коммерческий блок']}/15"},
            {"name": "Департамент клиентского сервиса", "code": "CUSTOMER", "unit_type": "department", 
             "parent_id": blocks["Коммерческий блок"], "level": 2, "path": f"/{blocks['Коммерческий блок']}/16"},
            
            # Финансовый блок
            {"name": "Департамент бухгалтерского учета", "code": "ACCOUNTING", "unit_type": "department", 
             "parent_id": blocks["Финансовый блок"], "level": 2, "path": f"/{blocks['Финансовый блок']}/17"},
            {"name": "Департамент финансового планирования", "code": "PLANNING", "unit_type": "department", 
             "parent_id": blocks["Финансовый блок"], "level": 2, "path": f"/{blocks['Финансовый блок']}/18"},
            {"name": "Департамент казначейства", "code": "TREASURY", "unit_type": "department", 
             "parent_id": blocks["Финансовый блок"], "level": 2, "path": f"/{blocks['Финансовый блок']}/19"},
        ]
        
        departments = {}
        for i, dept_data in enumerate(departments_data, 6):  # Начинаем с ID 6
            dept_data["id"] = i
            dept = OrganizationalUnit(**dept_data)
            session.add(dept)
            departments[dept_data["name"]] = i
        
        await session.flush()
        
        # ===== УПРАВЛЕНИЯ (уровень 3) =====
        directorates_data = [
            # Департамент разработки
            {"name": "Управление Backend разработки", "unit_type": "directorate", 
             "parent_id": departments["Департамент разработки"], "level": 3},
            {"name": "Управление Frontend разработки", "unit_type": "directorate", 
             "parent_id": departments["Департамент разработки"], "level": 3},
            {"name": "Управление интеграций", "unit_type": "directorate", 
             "parent_id": departments["Департамент разработки"], "level": 3},
            {"name": "Управление тестирования", "unit_type": "directorate", 
             "parent_id": departments["Департамент разработки"], "level": 3},
            
            # Департамент инфраструктуры
            {"name": "Управление серверной инфраструктуры", "unit_type": "directorate", 
             "parent_id": departments["Департамент инфраструктуры"], "level": 3},
            {"name": "Управление облачных технологий", "unit_type": "directorate", 
             "parent_id": departments["Департамент инфраструктуры"], "level": 3},
            {"name": "Управление сетевой инфраструктуры", "unit_type": "directorate", 
             "parent_id": departments["Департамент инфраструктуры"], "level": 3},
            
            # Департамент аналитики
            {"name": "Управление бизнес-аналитики", "unit_type": "directorate", 
             "parent_id": departments["Департамент аналитики"], "level": 3},
            {"name": "Управление системной аналитики", "unit_type": "directorate", 
             "parent_id": departments["Департамент аналитики"], "level": 3},
            {"name": "Управление данных", "unit_type": "directorate", 
             "parent_id": departments["Департамент аналитики"], "level": 3},
            
            # Департамент продуктовой разработки
            {"name": "Управление продукта A", "unit_type": "directorate", 
             "parent_id": departments["Департамент продуктовой разработки"], "level": 3},
            {"name": "Управление продукта B", "unit_type": "directorate", 
             "parent_id": departments["Департамент продуктовой разработки"], "level": 3},
            {"name": "Управление платформы", "unit_type": "directorate", 
             "parent_id": departments["Департамент продуктовой разработки"], "level": 3},
            
            # Департамент UX/UI
            {"name": "Управление UX исследований", "unit_type": "directorate", 
             "parent_id": departments["Департамент UX/UI"], "level": 3},
            {"name": "Управление UI дизайна", "unit_type": "directorate", 
             "parent_id": departments["Департамент UX/UI"], "level": 3},
            
            # Департамент мобильной разработки
            {"name": "Управление iOS разработки", "unit_type": "directorate", 
             "parent_id": departments["Департамент мобильной разработки"], "level": 3},
            {"name": "Управление Android разработки", "unit_type": "directorate", 
             "parent_id": departments["Департамент мобильной разработки"], "level": 3},
            {"name": "Управление кроссплатформенной разработки", "unit_type": "directorate", 
             "parent_id": departments["Департамент мобильной разработки"], "level": 3},
            
            # Департамент кибербезопасности
            {"name": "Управление мониторинга угроз", "unit_type": "directorate", 
             "parent_id": departments["Департамент кибербезопасности"], "level": 3},
            {"name": "Управление реагирования на инциденты", "unit_type": "directorate", 
             "parent_id": departments["Департамент кибербезопасности"], "level": 3},
            
            # Департамент аудита ИБ
            {"name": "Управление внутреннего аудита", "unit_type": "directorate", 
             "parent_id": departments["Департамент аудита ИБ"], "level": 3},
            {"name": "Управление соответствия требованиям", "unit_type": "directorate", 
             "parent_id": departments["Департамент аудита ИБ"], "level": 3},
            
            # Департамент продаж
            {"name": "Управление корпоративных продаж", "unit_type": "directorate", 
             "parent_id": departments["Департамент продаж"], "level": 3},
            {"name": "Управление розничных продаж", "unit_type": "directorate", 
             "parent_id": departments["Департамент продаж"], "level": 3},
            {"name": "Управление партнерских продаж", "unit_type": "directorate", 
             "parent_id": departments["Департамент продаж"], "level": 3},
            
            # Департамент маркетинга
            {"name": "Управление цифрового маркетинга", "unit_type": "directorate", 
             "parent_id": departments["Департамент маркетинга"], "level": 3},
            {"name": "Управление продуктового маркетинга", "unit_type": "directorate", 
             "parent_id": departments["Департамент маркетинга"], "level": 3},
            
            # Департамент клиентского сервиса
            {"name": "Управление технической поддержки", "unit_type": "directorate", 
             "parent_id": departments["Департамент клиентского сервиса"], "level": 3},
            {"name": "Управление клиентского опыта", "unit_type": "directorate", 
             "parent_id": departments["Департамент клиентского сервиса"], "level": 3},
            
            # Департамент бухгалтерского учета
            {"name": "Управление первичного учета", "unit_type": "directorate", 
             "parent_id": departments["Департамент бухгалтерского учета"], "level": 3},
            {"name": "Управление налогового учета", "unit_type": "directorate", 
             "parent_id": departments["Департамент бухгалтерского учета"], "level": 3},
            {"name": "Управление управленческого учета", "unit_type": "directorate", 
             "parent_id": departments["Департамент бухгалтерского учета"], "level": 3},
            
            # Департамент финансового планирования
            {"name": "Управление бюджетирования", "unit_type": "directorate", 
             "parent_id": departments["Департамент финансового планирования"], "level": 3},
            {"name": "Управление финансового анализа", "unit_type": "directorate", 
             "parent_id": departments["Департамент финансового планирования"], "level": 3},
            
            # Департамент казначейства
            {"name": "Управление расчетов", "unit_type": "directorate", 
             "parent_id": departments["Департамент казначейства"], "level": 3},
            {"name": "Управление ликвидности", "unit_type": "directorate", 
             "parent_id": departments["Департамент казначейства"], "level": 3},
        ]
        
        # Генерируем path для управлений
        for i, dir_data in enumerate(directorates_data, 20):  # Начинаем с ID 20
            parent_unit = await session.get(OrganizationalUnit, dir_data["parent_id"])
            dir_data["path"] = f"{parent_unit.path}/{i}"
            
            directorate = OrganizationalUnit(**dir_data)
            session.add(directorate)
        
        await session.commit()
        logger.info("✅ Организационная структура создана:")
        logger.info("   - 5 блоков")
        logger.info("   - {len(departments_data)} департаментов") 
        logger.info("   - {len(directorates_data)} управлений")


async def populate_agile_structure():
    """Создание Agile структуры"""
    async with AsyncSessionLocal() as session:
        
        # ===== ТРАЙБЫ =====
        tribes_data = [
            {"name": "Платформа", "description": "Платформенные решения и инфраструктура"},
            {"name": "Продукты", "description": "Клиентские продукты и сервисы"},
            {"name": "Данные", "description": "Аналитика и работа с данными"},
            {"name": "Безопасность", "description": "Информационная безопасность"},
            {"name": "Мобильные решения", "description": "Мобильные приложения"},
        ]
        
        tribes = {}
        for tribe_data in tribes_data:
            tribe = Tribe(**tribe_data)
            session.add(tribe)
            await session.flush()
            tribes[tribe_data["name"]] = tribe.id
        
        # ===== ПРОДУКТЫ/СЕРВИСЫ =====
        products_data = [
            # Трайб Платформа
            {"name": "API Gateway", "tribe_id": tribes["Платформа"], "type": "service"},
            {"name": "Микросервисная платформа", "tribe_id": tribes["Платформа"], "type": "service"},
            {"name": "Система мониторинга", "tribe_id": tribes["Платформа"], "type": "service"},
            
            # Трайб Продукты
            {"name": "Веб-приложение", "tribe_id": tribes["Продукты"], "type": "product"},
            {"name": "CRM система", "tribe_id": tribes["Продукты"], "type": "product"},
            {"name": "Портал самообслуживания", "tribe_id": tribes["Продукты"], "type": "product"},
            
            # Трайб Данные
            {"name": "Аналитическая платформа", "tribe_id": tribes["Данные"], "type": "service"},
            {"name": "Хранилище данных", "tribe_id": tribes["Данные"], "type": "service"},
            
            # Трайб Безопасность
            {"name": "SIEM система", "tribe_id": tribes["Безопасность"], "type": "service"},
            {"name": "Система управления доступом", "tribe_id": tribes["Безопасность"], "type": "service"},
            
            # Трайб Мобильные решения
            {"name": "iOS приложение", "tribe_id": tribes["Мобильные решения"], "type": "product"},
            {"name": "Android приложение", "tribe_id": tribes["Мобильные решения"], "type": "product"},
        ]
        
        products = {}
        for product_data in products_data:
            product = Product(**product_data)
            session.add(product)
            await session.flush()
            products[product_data["name"]] = product.id
        
        # ===== AGILE КОМАНДЫ =====
        teams_data = [
            # API Gateway
            {"name": "Gateway Change Team", "product_id": products["API Gateway"], "team_type": "Change"},
            {"name": "Gateway Run Team", "product_id": products["API Gateway"], "team_type": "Run"},
            
            # Микросервисная платформа
            {"name": "Platform Core Team", "product_id": products["Микросервисная платформа"], "team_type": "Change"},
            {"name": "Platform Support Team", "product_id": products["Микросервисная платформа"], "team_type": "Run"},
            
            # Система мониторинга
            {"name": "Monitoring Team", "product_id": products["Система мониторинга"], "team_type": "Run"},
            
            # Веб-приложение
            {"name": "Web Frontend Team", "product_id": products["Веб-приложение"], "team_type": "Change"},
            {"name": "Web Backend Team", "product_id": products["Веб-приложение"], "team_type": "Change"},
            {"name": "Web Support Team", "product_id": products["Веб-приложение"], "team_type": "Run"},
            
            # CRM система
            {"name": "CRM Development Team", "product_id": products["CRM система"], "team_type": "Change"},
            {"name": "CRM Maintenance Team", "product_id": products["CRM система"], "team_type": "Run"},
            
            # Портал самообслуживания
            {"name": "Portal Team", "product_id": products["Портал самообслуживания"], "team_type": "Change"},
            
            # Аналитическая платформа
            {"name": "Analytics Team", "product_id": products["Аналитическая платформа"], "team_type": "Change"},
            {"name": "Data Engineering Team", "product_id": products["Аналитическая платформа"], "team_type": "Run"},
            
            # Хранилище данных
            {"name": "Data Warehouse Team", "product_id": products["Хранилище данных"], "team_type": "Run"},
            
            # SIEM система
            {"name": "Security Monitoring Team", "product_id": products["SIEM система"], "team_type": "Run"},
            
            # Система управления доступом
            {"name": "IAM Team", "product_id": products["Система управления доступом"], "team_type": "Change"},
            
            # Мобильные приложения
            {"name": "iOS Development Team", "product_id": products["iOS приложение"], "team_type": "Change"},
            {"name": "Android Development Team", "product_id": products["Android приложение"], "team_type": "Change"},
            {"name": "Mobile QA Team", "product_id": products["iOS приложение"], "team_type": "Run"},  # Общая QA для мобильных
        ]
        
        for team_data in teams_data:
            team = AgileTeam(**team_data)
            session.add(team)
        
        await session.commit()
        logger.info("✅ Agile структура создана:")
        logger.info("   - {len(tribes_data)} трайбов")
        logger.info("   - {len(products_data)} продуктов/сервисов")
        logger.info("   - {len(teams_data)} agile команд")


async def main():
    """Главная функция заполнения данных"""
    logger.info("🚀 Начинаем заполнение справочников...")
    
    # Создаем таблицы если их нет
    await create_tables()
    
    # Заполняем справочники
    await populate_positions()
    await populate_employee_types()
    await populate_team_roles()
    await populate_employee_profiles()
    
    # Заполняем структуры
    await populate_organizational_structure()
    await populate_agile_structure()
    
    logger.info("🎉 Все справочники успешно заполнены!")


if __name__ == "__main__":
    asyncio.run(main())
