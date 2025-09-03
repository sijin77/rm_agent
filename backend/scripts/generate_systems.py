"""
Генерация Application Systems (АС) и ролей в них
"""
import asyncio
from app.utils import logger
from app.core.database import AsyncSessionLocal
from app.models import ApplicationSystem, Access


async def generate_application_systems():
    """Создание систем и ролей в них"""
    logger.info("🚀 Создаём корпоративные системы...")
    
    systems_data = [
        # === БИЗНЕС-СИСТЕМЫ ===
        {
            "name": "1С:ERP Управление предприятием",
            "criticality": "high",
            "system_type": "business",
            "roles": [
                {"role_name": "Администратор", "criticality": "high"},
                {"role_name": "Главный бухгалтер", "criticality": "high"},
                {"role_name": "Бухгалтер", "criticality": "medium"},
                {"role_name": "Кладовщик", "criticality": "medium"},
                {"role_name": "Менеджер продаж", "criticality": "medium"},
                {"role_name": "Аналитик", "criticality": "low"},
                {"role_name": "Пользователь", "criticality": "low"},
            ]
        },
        {
            "name": "CRM Система",
            "criticality": "high",
            "system_type": "business",
            "roles": [
                {"role_name": "Администратор CRM", "criticality": "high"},
                {"role_name": "Менеджер продаж", "criticality": "medium"},
                {"role_name": "Руководитель отдела продаж", "criticality": "medium"},
                {"role_name": "Маркетолог", "criticality": "medium"},
                {"role_name": "Аналитик продаж", "criticality": "low"},
                {"role_name": "Пользователь", "criticality": "low"},
            ]
        },
        {
            "name": "SAP ERP",
            "criticality": "high",
            "system_type": "business",
            "roles": [
                {"role_name": "SAP Администратор", "criticality": "high"},
                {"role_name": "SAP Консультант", "criticality": "high"},
                {"role_name": "Финансовый контролер", "criticality": "medium"},
                {"role_name": "Менеджер по закупкам", "criticality": "medium"},
                {"role_name": "Планировщик", "criticality": "medium"},
                {"role_name": "Конечный пользователь", "criticality": "low"},
            ]
        },
        {
            "name": "Система документооборота",
            "criticality": "medium",
            "system_type": "business",
            "roles": [
                {"role_name": "Администратор СЭД", "criticality": "high"},
                {"role_name": "Делопроизводитель", "criticality": "medium"},
                {"role_name": "Руководитель", "criticality": "medium"},
                {"role_name": "Исполнитель", "criticality": "low"},
                {"role_name": "Наблюдатель", "criticality": "low"},
            ]
        },
        {
            "name": "Система управления договорами",
            "criticality": "high",
            "system_type": "business",
            "roles": [
                {"role_name": "Администратор договоров", "criticality": "high"},
                {"role_name": "Юрист", "criticality": "medium"},
                {"role_name": "Менеджер договоров", "criticality": "medium"},
                {"role_name": "Контролер исполнения", "criticality": "low"},
                {"role_name": "Читатель", "criticality": "low"},
            ]
        },
        
        # === ИТ-СИСТЕМЫ ===
        {
            "name": "Jira Service Management",
            "criticality": "medium",
            "system_type": "it",
            "roles": [
                {"role_name": "Jira Administrator", "criticality": "high"},
                {"role_name": "Project Administrator", "criticality": "medium"},
                {"role_name": "Developer", "criticality": "medium"},
                {"role_name": "Tester", "criticality": "medium"},
                {"role_name": "Reporter", "criticality": "low"},
                {"role_name": "Viewer", "criticality": "low"},
            ]
        },
        {
            "name": "GitLab",
            "criticality": "high",
            "system_type": "it",
            "roles": [
                {"role_name": "GitLab Admin", "criticality": "high"},
                {"role_name": "Maintainer", "criticality": "high"},
                {"role_name": "Developer", "criticality": "medium"},
                {"role_name": "Reporter", "criticality": "low"},
                {"role_name": "Guest", "criticality": "low"},
            ]
        },
        {
            "name": "Confluence",
            "criticality": "medium",
            "system_type": "it",
            "roles": [
                {"role_name": "Confluence Administrator", "criticality": "high"},
                {"role_name": "Space Administrator", "criticality": "medium"},
                {"role_name": "Author", "criticality": "medium"},
                {"role_name": "Editor", "criticality": "low"},
                {"role_name": "Reader", "criticality": "low"},
            ]
        },
        {
            "name": "Jenkins CI/CD",
            "criticality": "high",
            "system_type": "it",
            "roles": [
                {"role_name": "Jenkins Administrator", "criticality": "high"},
                {"role_name": "Build Engineer", "criticality": "medium"},
                {"role_name": "Developer", "criticality": "medium"},
                {"role_name": "Viewer", "criticality": "low"},
            ]
        },
        {
            "name": "SonarQube",
            "criticality": "medium",
            "system_type": "it",
            "roles": [
                {"role_name": "SonarQube Administrator", "criticality": "high"},
                {"role_name": "Quality Gate Administrator", "criticality": "medium"},
                {"role_name": "Developer", "criticality": "medium"},
                {"role_name": "Viewer", "criticality": "low"},
            ]
        },
        {
            "name": "Nexus Repository",
            "criticality": "medium",
            "system_type": "it",
            "roles": [
                {"role_name": "Repository Administrator", "criticality": "high"},
                {"role_name": "Developer", "criticality": "medium"},
                {"role_name": "Viewer", "criticality": "low"},
            ]
        },
        {
            "name": "Zabbix Monitoring",
            "criticality": "high",
            "system_type": "it",
            "roles": [
                {"role_name": "Zabbix Super Administrator", "criticality": "high"},
                {"role_name": "Zabbix Administrator", "criticality": "high"},
                {"role_name": "DevOps Engineer", "criticality": "medium"},
                {"role_name": "Viewer", "criticality": "low"},
            ]
        },
        {
            "name": "Grafana",
            "criticality": "medium",
            "system_type": "it",
            "roles": [
                {"role_name": "Grafana Administrator", "criticality": "high"},
                {"role_name": "Dashboard Editor", "criticality": "medium"},
                {"role_name": "Viewer", "criticality": "low"},
            ]
        },
        {
            "name": "Kubernetes Dashboard",
            "criticality": "high",
            "system_type": "it",
            "roles": [
                {"role_name": "Cluster Administrator", "criticality": "high"},
                {"role_name": "DevOps Engineer", "criticality": "medium"},
                {"role_name": "Developer", "criticality": "low"},
                {"role_name": "Viewer", "criticality": "low"},
            ]
        },
        {
            "name": "PostgreSQL Admin",
            "criticality": "high",
            "system_type": "it",
            "roles": [
                {"role_name": "Database Administrator", "criticality": "high"},
                {"role_name": "Database Developer", "criticality": "medium"},
                {"role_name": "Application User", "criticality": "low"},
                {"role_name": "Read Only", "criticality": "low"},
            ]
        },
        {
            "name": "Oracle Database",
            "criticality": "high",
            "system_type": "it",
            "roles": [
                {"role_name": "Oracle DBA", "criticality": "high"},
                {"role_name": "Schema Owner", "criticality": "medium"},
                {"role_name": "Application User", "criticality": "low"},
                {"role_name": "Read Only", "criticality": "low"},
            ]
        },
        
        # === ВНУТРЕННИЕ ПОРТАЛЫ И SELF-SERVICE ===
        {
            "name": "Корпоративный портал",
            "criticality": "medium",
            "system_type": "business",
            "roles": [
                {"role_name": "Портал Администратор", "criticality": "high"},
                {"role_name": "Редактор контента", "criticality": "medium"},
                {"role_name": "Модератор", "criticality": "medium"},
                {"role_name": "Сотрудник", "criticality": "low"},
            ]
        },
        {
            "name": "Портал отчетов",
            "criticality": "medium",
            "system_type": "business",
            "roles": [
                {"role_name": "Администратор отчетов", "criticality": "high"},
                {"role_name": "Аналитик", "criticality": "medium"},
                {"role_name": "Менеджер", "criticality": "medium"},
                {"role_name": "Пользователь", "criticality": "low"},
            ]
        },
        {
            "name": "Self-Service Управление доступами",
            "criticality": "high",
            "system_type": "it",
            "roles": [
                {"role_name": "Identity Administrator", "criticality": "high"},
                {"role_name": "Access Manager", "criticality": "medium"},
                {"role_name": "Approver", "criticality": "medium"},
                {"role_name": "End User", "criticality": "low"},
            ]
        },
        {
            "name": "Self-Service Заказ КТС",
            "criticality": "medium",
            "system_type": "business",
            "roles": [
                {"role_name": "Администратор заказов", "criticality": "high"},
                {"role_name": "Менеджер КТС", "criticality": "medium"},
                {"role_name": "Согласующий", "criticality": "medium"},
                {"role_name": "Заказчик", "criticality": "low"},
            ]
        },
        {
            "name": "Self-Service HR",
            "criticality": "medium",
            "system_type": "business",
            "roles": [
                {"role_name": "HR Администратор", "criticality": "high"},
                {"role_name": "HR Специалист", "criticality": "medium"},
                {"role_name": "Руководитель", "criticality": "medium"},
                {"role_name": "Сотрудник", "criticality": "low"},
            ]
        },
        {
            "name": "Self-Service Командировки",
            "criticality": "medium",
            "system_type": "business",
            "roles": [
                {"role_name": "Администратор", "criticality": "medium"},
                {"role_name": "Бухгалтер", "criticality": "medium"},
                {"role_name": "Руководитель", "criticality": "low"},
                {"role_name": "Сотрудник", "criticality": "low"},
            ]
        },
        {
            "name": "Self-Service Заявки в ИТ",
            "criticality": "medium",
            "system_type": "it",
            "roles": [
                {"role_name": "ИТ Администратор", "criticality": "high"},
                {"role_name": "ИТ Специалист", "criticality": "medium"},
                {"role_name": "Заказчик", "criticality": "low"},
            ]
        },
        {
            "name": "Система бронирования переговорных",
            "criticality": "low",
            "system_type": "business",
            "roles": [
                {"role_name": "Администратор", "criticality": "medium"},
                {"role_name": "Сотрудник", "criticality": "low"},
            ]
        },
        {
            "name": "Система учета рабочего времени",
            "criticality": "high",
            "system_type": "business",
            "roles": [
                {"role_name": "Администратор", "criticality": "high"},
                {"role_name": "HR Специалист", "criticality": "medium"},
                {"role_name": "Руководитель", "criticality": "medium"},
                {"role_name": "Сотрудник", "criticality": "low"},
            ]
        },
        
        # === ОБЩИЕ СИСТЕМЫ ===
        {
            "name": "Microsoft Office 365",
            "criticality": "medium",
            "system_type": "business",
            "roles": [
                {"role_name": "Global Administrator", "criticality": "high"},
                {"role_name": "Exchange Administrator", "criticality": "high"},
                {"role_name": "SharePoint Administrator", "criticality": "medium"},
                {"role_name": "User", "criticality": "low"},
            ]
        },
        {
            "name": "Active Directory",
            "criticality": "high",
            "system_type": "it",
            "roles": [
                {"role_name": "Domain Administrator", "criticality": "high"},
                {"role_name": "Account Operator", "criticality": "medium"},
                {"role_name": "Help Desk", "criticality": "low"},
                {"role_name": "Domain User", "criticality": "low"},
            ]
        },
        {
            "name": "VPN Система",
            "criticality": "high",
            "system_type": "it",
            "roles": [
                {"role_name": "VPN Administrator", "criticality": "high"},
                {"role_name": "Network Engineer", "criticality": "medium"},
                {"role_name": "VPN User", "criticality": "low"},
            ]
        },
        {
            "name": "Файловое хранилище",
            "criticality": "medium",
            "system_type": "business",
            "roles": [
                {"role_name": "Storage Administrator", "criticality": "high"},
                {"role_name": "Department Admin", "criticality": "medium"},
                {"role_name": "User", "criticality": "low"},
            ]
        },
        {
            "name": "Система видеоконференций",
            "criticality": "medium",
            "system_type": "business",
            "roles": [
                {"role_name": "Администратор", "criticality": "medium"},
                {"role_name": "Организатор", "criticality": "low"},
                {"role_name": "Участник", "criticality": "low"},
            ]
        },
        {
            "name": "Антивирусная система",
            "criticality": "high",
            "system_type": "it",
            "roles": [
                {"role_name": "Security Administrator", "criticality": "high"},
                {"role_name": "Security Analyst", "criticality": "medium"},
                {"role_name": "Endpoint User", "criticality": "low"},
            ]
        },
        {
            "name": "Система резервного копирования",
            "criticality": "high",
            "system_type": "it",
            "roles": [
                {"role_name": "Backup Administrator", "criticality": "high"},
                {"role_name": "Backup Operator", "criticality": "medium"},
                {"role_name": "Restore User", "criticality": "low"},
            ]
        },
        {
            "name": "Система мониторинга безопасности",
            "criticality": "high",
            "system_type": "it",
            "roles": [
                {"role_name": "Security Administrator", "criticality": "high"},
                {"role_name": "SOC Analyst", "criticality": "high"},
                {"role_name": "Incident Responder", "criticality": "medium"},
                {"role_name": "Viewer", "criticality": "low"},
            ]
        },
        {
            "name": "Тестовая среда разработки",
            "criticality": "low",
            "system_type": "it",
            "roles": [
                {"role_name": "Environment Administrator", "criticality": "medium"},
                {"role_name": "Developer", "criticality": "low"},
                {"role_name": "Tester", "criticality": "low"},
            ]
        },
        {
            "name": "Система управления лицензиями",
            "criticality": "medium",
            "system_type": "business",
            "roles": [
                {"role_name": "License Administrator", "criticality": "high"},
                {"role_name": "IT Asset Manager", "criticality": "medium"},
                {"role_name": "Department Manager", "criticality": "low"},
                {"role_name": "User", "criticality": "low"},
            ]
        },
        {
            "name": "Корпоративная Wiki",
            "criticality": "low",
            "system_type": "business",
            "roles": [
                {"role_name": "Wiki Administrator", "criticality": "medium"},
                {"role_name": "Editor", "criticality": "low"},
                {"role_name": "Reader", "criticality": "low"},
            ]
        },
    ]
    
    async with AsyncSessionLocal() as session:
        system_id = 1
        access_id = 1
        
        for system_data in systems_data:
            # Создаем систему
            app_system = ApplicationSystem(
                id=system_id,
                name=system_data["name"],
                criticality=system_data["criticality"],
                system_type=system_data["system_type"]
            )
            session.add(app_system)
            
            logger.info("📱 Создана система: {system_data['name']} ({len(system_data['roles'])} ролей)")
            
            # Создаем роли для системы
            for role_data in system_data["roles"]:
                access = Access(
                    id=access_id,
                    system_id=system_id,
                    role_name=role_data["role_name"],
                    criticality=role_data["criticality"]
                )
                session.add(access)
                access_id += 1
            
            system_id += 1
        
        await session.commit()
        
        logger.info("\n🎉 Создано {len(systems_data)} систем с ролями!")
        logger.info("📊 Статистика:")
        logger.info("   - Всего систем: {len(systems_data)}")
        logger.info("   - Всего ролей: {access_id - 1}")
        
        # Подсчет по типам
        business_systems = sum(1 for s in systems_data if s["system_type"] == "business")
        it_systems = sum(1 for s in systems_data if s["system_type"] == "it")
        
        logger.info("   - Бизнес-систем: {business_systems}")
        logger.info("   - ИТ-систем: {it_systems}")
        
        # Подсчет по критичности
        high_crit = sum(1 for s in systems_data if s["criticality"] == "high")
        medium_crit = sum(1 for s in systems_data if s["criticality"] == "medium")
        low_crit = sum(1 for s in systems_data if s["criticality"] == "low")
        
        logger.info("   - Высокой критичности: {high_crit}")
        logger.info("   - Средней критичности: {medium_crit}")
        logger.info("   - Низкой критичности: {low_crit}")


async def main():
    """Главная функция"""
    await generate_application_systems()


if __name__ == "__main__":
    asyncio.run(main())
