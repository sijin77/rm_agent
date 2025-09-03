"""
Генерация доступов сотрудников к системам
"""
import asyncio
import random
from sqlalchemy import text
from app.core.database import AsyncSessionLocal
from app.models import Employee, Access, EmployeeAccess, RoleProfile, ProfileAccess
from app.utils import logger


async def generate_employee_accesses():
    """Генерация доступов для всех сотрудников"""
    logger.step("Генерация доступов", "Начинаем генерацию доступов сотрудников...")
    
    async with AsyncSessionLocal() as session:
        # Получаем всех сотрудников
        result = await session.execute(
            text("SELECT id, profile_id, org_unit_id, position_id, employee_type_id FROM employees")
        )
        employees = result.fetchall()
        logger.info(f"Найдено {len(employees)} сотрудников")
        
        # Получаем все доступы
        result = await session.execute(
            text("SELECT id, system_id, role_name, criticality FROM accesses")
        )
        accesses = result.fetchall()
        logger.info(f"Найдено {len(accesses)} доступов")
        
        # Получаем ролевые профили и их доступы
        result = await session.execute(text("""
            SELECT rp.id, rp.criteria, pa.access_id 
            FROM role_profiles rp 
            JOIN profile_accesses pa ON pa.role_profile_id = rp.id
        """))
        profile_accesses = result.fetchall()
        
        # Группируем доступы по профилям
        role_profiles_map = {}
        for profile_id, criteria, access_id in profile_accesses:
            if profile_id not in role_profiles_map:
                role_profiles_map[profile_id] = {
                    'criteria': criteria,
                    'accesses': []
                }
            role_profiles_map[profile_id]['accesses'].append(access_id)
        
        logger.info(f"Найдено {len(role_profiles_map)} ролевых профилей")
        
        # Базовые доступы для всех (универсальный профиль)
        universal_accesses = []
        for profile_id, profile_data in role_profiles_map.items():
            if 'all_employees' in profile_data['criteria']:
                universal_accesses = profile_data['accesses']
                break
        
        logger.info(f"Базовых доступов для всех: {len(universal_accesses)}")
        
        employee_accesses = []
        access_id_counter = 1
        
        for emp_id, profile_id, org_unit_id, position_id, employee_type_id in employees:
            employee_access_ids = set()
            
            # 1. БАЗОВЫЕ ДОСТУПЫ (для всех сотрудников)
            for access_id in universal_accesses:
                employee_accesses.append({
                    'id': access_id_counter,
                    'employee_id': emp_id,
                    'access_id': access_id,
                    'assignment_type': 'auto_role',
                    'role_profile_id': 6  # ID универсального профиля
                })
                employee_access_ids.add(access_id)
                access_id_counter += 1
            
            # 2. ЛОГИЧНЫЕ ДОСТУПЫ ПО ПРОФИЛЮ СОТРУДНИКА
            for role_profile_id, profile_data in role_profiles_map.items():
                if role_profile_id == 6:  # Пропускаем универсальный профиль
                    continue
                
                criteria = profile_data['criteria']
                matches = False
                
                # Проверяем соответствие критериям
                if 'employee_profiles' in criteria:
                    # Упрощенная проверка по ID профиля
                    # В реальности нужно получить название профиля
                    if profile_id in [1, 2, 3, 4, 5, 6]:  # IT профили
                        if role_profile_id in [1, 2, 3]:  # IT ролевые модели
                            matches = True
                    elif profile_id in [32, 33, 34, 35]:  # Бухгалтерские профили
                        if role_profile_id == 4:  # Бухгалтерская модель
                            matches = True
                    elif profile_id in [28, 29, 30, 31]:  # Продажные профили
                        if role_profile_id == 5:  # Продажная модель
                            matches = True
                
                if matches:
                    for access_id in profile_data['accesses']:
                        if access_id not in employee_access_ids:
                            employee_accesses.append({
                                'id': access_id_counter,
                                'employee_id': emp_id,
                                'access_id': access_id,
                                'assignment_type': 'auto_role',
                                'role_profile_id': role_profile_id
                            })
                            employee_access_ids.add(access_id)
                            access_id_counter += 1
            
            # 3. ДОПОЛНИТЕЛЬНЫЕ СЛУЧАЙНЫЕ ДОСТУПЫ (60-80 на сотрудника для достижения 150k)
            available_accesses = [acc[0] for acc in accesses if acc[0] not in employee_access_ids]
            if available_accesses:
                # Увеличиваем количество доступов для достижения ~150k общих доступов
                num_additional = random.randint(60, 80)
                additional_accesses = random.sample(
                    available_accesses, 
                    min(num_additional, len(available_accesses))
                )
                
                for access_id in additional_accesses:
                    employee_accesses.append({
                        'id': access_id_counter,
                        'employee_id': emp_id,
                        'access_id': access_id,
                        'assignment_type': 'manual_request',
                        'role_profile_id': None
                    })
                    employee_access_ids.add(access_id)
                    access_id_counter += 1
            
            # 4. ШУМ - нелогичные доступы (5% вероятность)
            if random.random() < 0.05:
                noise_accesses = [acc[0] for acc in accesses if acc[0] not in employee_access_ids]
                if noise_accesses:
                    noise_access = random.choice(noise_accesses)
                    employee_accesses.append({
                        'id': access_id_counter,
                        'employee_id': emp_id,
                        'access_id': noise_access,
                        'assignment_type': 'manual_request',
                        'role_profile_id': None
                    })
                    access_id_counter += 1
        
        logger.info(f"Сгенерировано {len(employee_accesses)} доступов")
        
        # Сохраняем пакетами по 1000
        batch_size = 1000
        for i in range(0, len(employee_accesses), batch_size):
            batch = employee_accesses[i:i + batch_size]
            
            # Формируем SQL запрос для массовой вставки
            values = []
            for ea in batch:
                role_profile_part = f", {ea['role_profile_id']}" if ea['role_profile_id'] else ", NULL"
                values.append(f"({ea['id']}, {ea['employee_id']}, {ea['access_id']}, '{ea['assignment_type']}'{role_profile_part})")
            
            sql = f"""
                INSERT INTO employee_accesses (id, employee_id, access_id, assignment_type, role_profile_id)
                VALUES {', '.join(values)}
            """
            
            await session.execute(text(sql))
            await session.commit()
            logger.progress(i + len(batch), len(employee_accesses), "Сохранено доступов")
    
    logger.success("Генерация доступов завершена!")


async def show_statistics():
    """Показать статистику доступов"""
    async with AsyncSessionLocal() as session:
        # Общая статистика
        result = await session.execute(text("SELECT COUNT(*) FROM employee_accesses"))
        total_accesses = result.scalar()
        
        result = await session.execute(text("SELECT COUNT(*) FROM employees"))
        total_employees = result.scalar()
        
        result = await session.execute(text("SELECT COUNT(*) FROM employee_accesses WHERE assignment_type = 'auto_role'"))
        auto_accesses = result.scalar()
        
        result = await session.execute(text("SELECT COUNT(*) FROM employee_accesses WHERE assignment_type = 'manual_request'"))
        manual_accesses = result.scalar()
        
        logger.info(f"Статистика доступов:")
        logger.info(f"   - Всего доступов: {total_accesses}")
        logger.info(f"   - Среднее на сотрудника: {total_accesses / total_employees:.1f}")
        logger.info(f"   - Автоматических (по ролевой модели): {auto_accesses} ({auto_accesses/total_accesses*100:.1f}%)")
        logger.info(f"   - Ручных запросов: {manual_accesses} ({manual_accesses/total_accesses*100:.1f}%)")


if __name__ == "__main__":
    asyncio.run(generate_employee_accesses())
    asyncio.run(show_statistics())
