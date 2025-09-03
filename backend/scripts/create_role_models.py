"""
Создание базовых ролевых моделей для начального обучения
"""
import asyncio
from app.utils import logger
from app.core.database import AsyncSessionLocal
from app.models import RoleModel, RoleProfile, ProfileAccess


async def create_base_role_models():
    """Создание базовых ролевых моделей"""
    logger.info("🎯 Создаём базовые ролевые модели...")
    
    role_models_data = [
        {
            "name": "IT Разработчик",
            "description": "Базовая ролевая модель для разработчиков ПО",
            "author": "Система",
            "profiles": [
                {
                    "name": "Java Backend Developer",
                    "criteria": {
                        "employee_profiles": ["Java Developer", "Backend Developer", "Fullstack Developer"],
                        "positions": ["Инженер", "Главный инженер", "Ведущий специалист", "Главный специалист"],
                        "org_units_type": ["IT"]
                    },
                    "accesses": [
                        # Основные системы разработки
                        {"system_name": "GitLab", "roles": ["Developer", "Maintainer"]},
                        {"system_name": "Jira Service Management", "roles": ["Developer", "Reporter"]},
                        {"system_name": "Confluence", "roles": ["Author", "Editor"]},
                        {"system_name": "Jenkins CI/CD", "roles": ["Developer", "Viewer"]},
                        {"system_name": "SonarQube", "roles": ["Developer", "Viewer"]},
                        {"system_name": "Nexus Repository", "roles": ["Developer", "Viewer"]},
                        {"system_name": "Тестовая среда разработки", "roles": ["Developer"]},
                    ]
                },
                {
                    "name": "Frontend Developer",
                    "criteria": {
                        "employee_profiles": ["Frontend Developer", "React Developer", "Fullstack Developer"],
                        "positions": ["Инженер", "Главный инженер", "Ведущий специалист", "Главный специалист"],
                        "org_units_type": ["IT"]
                    },
                    "accesses": [
                        {"system_name": "GitLab", "roles": ["Developer"]},
                        {"system_name": "Jira Service Management", "roles": ["Developer", "Reporter"]},
                        {"system_name": "Confluence", "roles": ["Author", "Editor"]},
                        {"system_name": "Тестовая среда разработки", "roles": ["Developer"]},
                    ]
                }
            ]
        },
        {
            "name": "DevOps Инженер",
            "description": "Ролевая модель для специалистов по инфраструктуре и автоматизации",
            "author": "Система",
            "profiles": [
                {
                    "name": "DevOps Engineer",
                    "criteria": {
                        "employee_profiles": ["DevOps Engineer", "System Administrator"],
                        "positions": ["Инженер", "Главный инженер", "Ведущий специалист", "Главный специалист"],
                        "org_units_type": ["IT"]
                    },
                    "accesses": [
                        {"system_name": "GitLab", "roles": ["Maintainer", "Developer"]},
                        {"system_name": "Jenkins CI/CD", "roles": ["Build Engineer", "Developer"]},
                        {"system_name": "Kubernetes Dashboard", "roles": ["DevOps Engineer", "Viewer"]},
                        {"system_name": "Zabbix Monitoring", "roles": ["DevOps Engineer", "Viewer"]},
                        {"system_name": "Grafana", "roles": ["Dashboard Editor", "Viewer"]},
                        {"system_name": "VPN Система", "roles": ["Network Engineer", "VPN User"]},
                        {"system_name": "Система резервного копирования", "roles": ["Backup Operator"]},
                    ]
                }
            ]
        },
        {
            "name": "Бухгалтер",
            "description": "Ролевая модель для сотрудников бухгалтерии",
            "author": "Система",
            "profiles": [
                {
                    "name": "Бухгалтер",
                    "criteria": {
                        "employee_profiles": ["Бухгалтер", "Главный бухгалтер"],
                        "positions": ["Специалист", "Ведущий специалист", "Главный специалист", "Эксперт"],
                        "org_units_type": ["Business"]
                    },
                    "accesses": [
                        {"system_name": "1С:ERP Управление предприятием", "roles": ["Бухгалтер", "Главный бухгалтер"]},
                        {"system_name": "SAP ERP", "roles": ["Финансовый контролер", "Конечный пользователь"]},
                        {"system_name": "Система учета рабочего времени", "roles": ["HR Специалист", "Сотрудник"]},
                        {"system_name": "Self-Service Командировки", "roles": ["Бухгалтер", "Администратор"]},
                    ]
                }
            ]
        },
        {
            "name": "Менеджер продаж",
            "description": "Ролевая модель для менеджеров по продажам",
            "author": "Система",
            "profiles": [
                {
                    "name": "Sales Manager",
                    "criteria": {
                        "employee_profiles": ["Менеджер по продажам", "Руководитель продаж"],
                        "positions": ["Менеджер", "Главный специалист", "Эксперт"],
                        "org_units_type": ["Business"]
                    },
                    "accesses": [
                        {"system_name": "CRM Система", "roles": ["Менеджер продаж", "Руководитель отдела продаж"]},
                        {"system_name": "1С:ERP Управление предприятием", "roles": ["Менеджер продаж", "Пользователь"]},
                        {"system_name": "Портал отчетов", "roles": ["Менеджер", "Пользователь"]},
                    ]
                }
            ]
        },
        {
            "name": "Универсальный сотрудник",
            "description": "Базовые доступы для всех сотрудников",
            "author": "Система",
            "profiles": [
                {
                    "name": "Базовые доступы",
                    "criteria": {
                        "employee_types": ["Внутренний сотрудник", "Аутстаффер", "Сотрудник компании партнера"],
                        "all_employees": True
                    },
                    "accesses": [
                        {"system_name": "Microsoft Office 365", "roles": ["User"]},
                        {"system_name": "Корпоративный портал", "roles": ["Сотрудник"]},
                        {"system_name": "Система бронирования переговорных", "roles": ["Сотрудник"]},
                        {"system_name": "Система видеоконференций", "roles": ["Участник"]},
                        {"system_name": "Active Directory", "roles": ["Domain User"]},
                    ]
                }
            ]
        }
    ]
    
    async with AsyncSessionLocal() as session:
        role_model_id = 1
        profile_id = 1
        profile_access_id = 1
        
        for rm_data in role_models_data:
            # Создаем ролевую модель
            role_model = RoleModel(
                id=role_model_id,
                name=rm_data["name"],
                description=rm_data["description"],
                author=rm_data["author"],
                version="1.0",
                is_active=True
            )
            session.add(role_model)
            
            logger.info("📋 Создана ролевая модель: {rm_data['name']}")
            
            # Создаем профили для модели
            for profile_data in rm_data["profiles"]:
                role_profile = RoleProfile(
                    id=profile_id,
                    role_model_id=role_model_id,
                    name=profile_data["name"],
                    criteria=profile_data["criteria"],
                    description=f"Профиль для {profile_data['name']}"
                )
                session.add(role_profile)
                
                logger.info("  👤 Профиль: {profile_data['name']} ({len(profile_data['accesses'])} доступов)")
                
                # Создаем доступы для профиля
                for access_data in profile_data["accesses"]:
                    for role_name in access_data["roles"]:
                        # Найдем access_id по системе и роли
                        # Пока создадим заглушки, потом обновим правильными ID
                        profile_access = ProfileAccess(
                            id=profile_access_id,
                            role_profile_id=profile_id,
                            access_id=1,  # Заглушка, обновим позже
                            system_name=access_data["system_name"],
                            role_name=role_name
                        )
                        session.add(profile_access)
                        profile_access_id += 1
                
                profile_id += 1
            
            role_model_id += 1
        
        await session.commit()
        
        logger.info("\n🎉 Создано {len(role_models_data)} ролевых моделей!")
        logger.info("📊 Всего профилей: {profile_id - 1}")
        logger.info("🔑 Всего связей доступов: {profile_access_id - 1}")


async def update_profile_access_ids():
    """Обновляем правильные access_id в ProfileAccess"""
    logger.info("🔄 Обновляем ID доступов в профилях...")
    
    async with AsyncSessionLocal() as session:
        # Получаем все ProfileAccess с заглушками
        from sqlalchemy import select, update
        from app.models import Access, ApplicationSystem
        
        # Получаем все ProfileAccess
        profile_accesses_result = await session.execute(
            select(ProfileAccess).where(ProfileAccess.access_id == 1)
        )
        profile_accesses = profile_accesses_result.scalars().all()
        
        updated_count = 0
        for pa in profile_accesses:
            # Найдем правильный access_id
            access_result = await session.execute(
                select(Access.id)
                .join(ApplicationSystem)
                .where(
                    ApplicationSystem.name == pa.system_name,
                    Access.role_name == pa.role_name
                )
            )
            access_id = access_result.scalar_one_or_none()
            
            if access_id:
                pa.access_id = access_id
                updated_count += 1
            else:
                logger.info("⚠️  Не найден доступ: {pa.system_name} - {pa.role_name}")
        
        await session.commit()
        logger.info("✅ Обновлено {updated_count} связей доступов")


async def main():
    """Главная функция"""
    await create_base_role_models()
    await update_profile_access_ids()


if __name__ == "__main__":
    asyncio.run(main())
