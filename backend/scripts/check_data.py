"""
Проверка данных в базе
"""
import asyncio
from sqlalchemy import select, func
from app.utils import logger
from app.core.database import AsyncSessionLocal
from app.models import Employee, ApplicationSystem, Access, EmployeeAccess


async def check_data():
    """Проверка что у нас есть в базе"""
    async with AsyncSessionLocal() as session:
        # Считаем записи
        emp_count = await session.execute(select(func.count(Employee.id)))
        as_count = await session.execute(select(func.count(ApplicationSystem.id)))
        access_count = await session.execute(select(func.count(Access.id)))
        emp_access_count = await session.execute(select(func.count(EmployeeAccess.id)))
        
        logger.info("📊 Статистика базы данных:")
        logger.info("   👥 Сотрудники: {emp_count.scalar()}")
        logger.info("   🏢 Системы (AS): {as_count.scalar()}")
        logger.info("   🔑 Доступы: {access_count.scalar()}")
        logger.info("   👤 Доступы сотрудников: {emp_access_count.scalar()}")
        
        # Показываем примеры сотрудников
        employees = await session.execute(
            select(Employee.full_name, Employee.employee_number)
            .limit(5)
        )
        
        logger.info("\n👥 Примеры сотрудников:")
        for emp in employees.scalars().all():
            logger.info("   - {emp}")


if __name__ == "__main__":
    asyncio.run(check_data())
