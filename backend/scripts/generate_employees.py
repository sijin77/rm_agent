"""
Генерация большого количества сотрудников с реалистичными данными
"""
import asyncio
import random
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.utils import logger
from app.core.database import AsyncSessionLocal
from app.models import (
    Employee, OrganizationalUnit, Position, EmployeeProfile, EmployeeType, 
    TeamRole, AgileTeam, Product
)


# Списки для генерации реалистичных данных
FIRST_NAMES = [
    "Александр", "Алексей", "Андрей", "Антон", "Артем", "Борис", "Вадим", "Валентин", "Василий", "Виктор",
    "Владимир", "Владислав", "Вячеслав", "Геннадий", "Георгий", "Григорий", "Дмитрий", "Евгений", "Егор", "Иван",
    "Игорь", "Илья", "Кирилл", "Константин", "Леонид", "Максим", "Михаил", "Николай", "Олег", "Павел",
    "Петр", "Роман", "Сергей", "Станислав", "Степан", "Федор", "Юрий", "Ярослав",
    "Александра", "Алла", "Анастасия", "Анна", "Валентина", "Вера", "Виктория", "Галина", "Дарья", "Екатерина",
    "Елена", "Жанна", "Зоя", "Ирина", "Кристина", "Лариса", "Людмила", "Марина", "Мария", "Наталья",
    "Нина", "Ольга", "Полина", "Светлана", "Татьяна", "Юлия", "Яна"
]

LAST_NAMES = [
    "Иванов", "Петров", "Сидоров", "Смирнов", "Кузнецов", "Попов", "Васильев", "Соколов", "Михайлов", "Новиков",
    "Федоров", "Морозов", "Волков", "Алексеев", "Лебедев", "Семенов", "Егоров", "Павлов", "Козлов", "Степанов",
    "Николаев", "Орлов", "Андреев", "Макаров", "Никитин", "Захаров", "Зайцев", "Соловьев", "Борисов", "Яковлев",
    "Григорьев", "Романов", "Воробьев", "Сергеев", "Кириллов", "Фролов", "Александров", "Дмитриев", "Королев", "Гусев",
    "Киселев", "Ильин", "Максимов", "Поляков", "Сорокин", "Виноградов", "Ковалев", "Белов", "Медведев", "Антонов",
    "Тарасов", "Жуков", "Баранов", "Филиппов", "Комаров", "Давыдов", "Беляев", "Герасимов", "Богданов", "Осипов"
]

MIDDLE_NAMES_MALE = [
    "Александрович", "Алексеевич", "Андреевич", "Антонович", "Артемович", "Борисович", "Вадимович", "Валентинович",
    "Васильевич", "Викторович", "Владимирович", "Владиславович", "Вячеславович", "Геннадьевич", "Георгиевич",
    "Григорьевич", "Дмитриевич", "Евгеньевич", "Егорович", "Иванович", "Игоревич", "Ильич", "Кириллович",
    "Константинович", "Леонидович", "Максимович", "Михайлович", "Николаевич", "Олегович", "Павлович",
    "Петрович", "Романович", "Сергеевич", "Станиславович", "Степанович", "Федорович", "Юрьевич", "Ярославович"
]

MIDDLE_NAMES_FEMALE = [
    "Александровна", "Алексеевна", "Андреевна", "Антоновна", "Артемовна", "Борисовна", "Вадимовна", "Валентиновна",
    "Васильевна", "Викторовна", "Владимировна", "Владиславовна", "Вячеславовна", "Геннадьевна", "Георгиевна",
    "Григорьевна", "Дмитриевна", "Евгеньевна", "Егоровна", "Ивановна", "Игоревна", "Ильинична", "Кирилловна",
    "Константиновна", "Леонидовна", "Максимовна", "Михайловна", "Николаевна", "Олеговна", "Павловна",
    "Петровна", "Романовна", "Сергеевна", "Станиславовна", "Степановна", "Федоровна", "Юрьевна", "Ярославовна"
]

# Маппинг профилей к подразделениям (для реалистичного распределения)
PROFILE_TO_DEPARTMENTS = {
    # IT профили -> IT департаменты
    "разработчик": [6, 9, 11],  # Разработка, Продуктовая разработка, Мобильная разработка
    "аналитик": [8, 9],  # Аналитика, Продуктовая разработка
    "тестировщик": [6, 9, 11],  # Разработка, Продуктовая разработка, Мобильная разработка
    "devops": [7],  # Инфраструктура
    "дизайнер": [10],  # UX/UI
    "архитектор": [6, 7, 9],  # Разработка, Инфраструктура, Продуктовая разработка
    "менеджер проектов": [6, 7, 8, 9, 10, 11],  # Все IT департаменты
    
    # Бизнес профили -> Бизнес департаменты
    "эксперт по продажам": [14],  # Продажи
    "бухгалтер": [17],  # Бухучет
    "hr специалист": [15, 16],  # Маркетинг, Клиентский сервис (условно)
    "маркетолог": [15],  # Маркетинг
    "юрист": [14, 15, 16, 17, 18, 19],  # Все бизнес департаменты
}

# Соответствие профилей командным ролям
PROFILE_TO_TEAM_ROLES = {
    "разработчик": ["Developer", "Tech Lead"],
    "аналитик": ["Business Analyst", "System Analyst", "Data Analyst"],
    "тестировщик": ["QA Engineer", "QA Lead"],
    "devops": ["DevOps Engineer"],
    "дизайнер": ["UI/UX Designer"],
    "архитектор": ["Architect", "Tech Lead"],
    "менеджер проектов": ["Project Manager", "Scrum Master", "Product Owner"],
}


async def get_reference_data():
    """Получение справочных данных"""
    async with AsyncSessionLocal() as session:
        # Получаем все справочники
        org_units = await session.execute(select(OrganizationalUnit))
        positions = await session.execute(select(Position))
        profiles = await session.execute(select(EmployeeProfile))
        emp_types = await session.execute(select(EmployeeType))
        team_roles = await session.execute(select(TeamRole))
        agile_teams = await session.execute(select(AgileTeam))
        
        return {
            'org_units': {unit.id: unit for unit in org_units.scalars().all()},
            'positions': {pos.id: pos for pos in positions.scalars().all()},
            'profiles': {prof.id: prof for prof in profiles.scalars().all()},
            'emp_types': {et.id: et for et in emp_types.scalars().all()},
            'team_roles': {tr.id: tr for tr in team_roles.scalars().all()},
            'agile_teams': {at.id: at for at in agile_teams.scalars().all()},
        }


def generate_full_name():
    """Генерация полного ФИО"""
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    
    # Определяем пол по имени (упрощенно)
    is_female = first_name in ["Александра", "Алла", "Анастасия", "Анна", "Валентина", "Вера", 
                              "Виктория", "Галина", "Дарья", "Екатерина", "Елена", "Жанна", 
                              "Зоя", "Ирина", "Кристина", "Лариса", "Людмила", "Марина", 
                              "Мария", "Наталья", "Нина", "Ольга", "Полина", "Светлана", 
                              "Татьяна", "Юлия", "Яна"]
    
    if is_female:
        middle_name = random.choice(MIDDLE_NAMES_FEMALE)
        # Женские фамилии на -а
        if last_name.endswith(('ов', 'ев', 'ин', 'ын')):
            last_name += 'а'
        elif last_name.endswith('ский'):
            last_name = last_name[:-2] + 'ая'
    else:
        middle_name = random.choice(MIDDLE_NAMES_MALE)
    
    return f"{last_name} {first_name} {middle_name}"


def get_suitable_profile_for_department(profiles, dept_id):
    """Получение подходящего профиля для департамента"""
    suitable_profiles = []
    
    for profile_id, profile in profiles.items():
        profile_name_lower = profile.name.lower()
        
        # Проверяем соответствие профиля департаменту
        for profile_key, dept_list in PROFILE_TO_DEPARTMENTS.items():
            if profile_key in profile_name_lower and dept_id in dept_list:
                suitable_profiles.append(profile_id)
                break
    
    # Если не найдено подходящих профилей, возвращаем случайный
    if not suitable_profiles:
        suitable_profiles = list(profiles.keys())
    
    return random.choice(suitable_profiles)


def get_suitable_team_role(team_roles, profile_name):
    """Получение подходящей роли в команде для профиля"""
    profile_name_lower = profile_name.lower()
    suitable_roles = []
    
    for profile_key, role_list in PROFILE_TO_TEAM_ROLES.items():
        if profile_key in profile_name_lower:
            for role_name in role_list:
                for role_id, role in team_roles.items():
                    if role.name == role_name:
                        suitable_roles.append(role_id)
            break
    
    # Если не найдено подходящих ролей, возвращаем Developer или случайную
    if not suitable_roles:
        for role_id, role in team_roles.items():
            if role.name == "Developer":
                return role_id
        suitable_roles = list(team_roles.keys())
    
    return random.choice(suitable_roles)


def generate_hire_date():
    """Генерация даты найма (от 10 лет назад до сегодня)"""
    start_date = date.today() - timedelta(days=10*365)
    end_date = date.today()
    
    time_between = end_date - start_date
    days_between = time_between.days
    random_days = random.randrange(days_between)
    
    return start_date + timedelta(days=random_days)


def get_experience_years(hire_date):
    """Вычисление лет опыта на основе даты найма"""
    today = date.today()
    years = today.year - hire_date.year
    if today.month < hire_date.month or (today.month == hire_date.month and today.day < hire_date.day):
        years -= 1
    return max(0, years)


async def generate_employees():
    """Генерация сотрудников"""
    logger.info("🚀 Начинаем генерацию сотрудников...")
    
    # Получаем справочные данные
    ref_data = await get_reference_data()
    
    # Получаем только управления (level=3) для размещения сотрудников
    directorates = {unit_id: unit for unit_id, unit in ref_data['org_units'].items() 
                   if unit.level == 3}
    
    logger.info("📊 Найдено {len(directorates)} управлений для размещения сотрудников")
    
    employees_data = []
    total_employees = 2000
    
    # Распределяем сотрудников по управлениям
    employees_per_directorate = {}
    for unit_id in directorates.keys():
        # Случайное количество от 30 до 80 сотрудников на управление
        employees_per_directorate[unit_id] = random.randint(30, 80)
    
    # Корректируем общее количество до нужного
    current_total = sum(employees_per_directorate.values())
    if current_total < total_employees:
        # Добавляем недостающих
        shortage = total_employees - current_total
        for _ in range(shortage):
            unit_id = random.choice(list(employees_per_directorate.keys()))
            employees_per_directorate[unit_id] += 1
    elif current_total > total_employees:
        # Убираем лишних
        excess = current_total - total_employees
        for _ in range(excess):
            unit_id = random.choice(list(employees_per_directorate.keys()))
            if employees_per_directorate[unit_id] > 20:  # Минимум 20 человек в управлении
                employees_per_directorate[unit_id] -= 1
    
    logger.info("📈 Планируем создать {sum(employees_per_directorate.values())} сотрудников")
    
    employee_id = 1
    
    for unit_id, employee_count in employees_per_directorate.items():
        unit = directorates[unit_id]
        logger.info("👥 Создаем {employee_count} сотрудников для '{unit.name}'")
        
        # Получаем департамент (родительский для управления)
        department = ref_data['org_units'][unit.parent_id]
        
        for i in range(employee_count):
            # Генерируем основные данные
            full_name = generate_full_name()
            hire_date = generate_hire_date()
            experience_years = get_experience_years(hire_date)
            
            # Подбираем профиль подходящий для департамента
            profile_id = get_suitable_profile_for_department(ref_data['profiles'], department.id)
            profile = ref_data['profiles'][profile_id]
            
            # Подбираем должность в зависимости от опыта
            if experience_years < 1:
                position_level = 1  # Специалист/Инженер
            elif experience_years < 3:
                position_level = 2  # Ведущий специалист/Главный инженер
            elif experience_years < 5:
                position_level = 3  # Эксперт/Главный специалист
            elif experience_years < 8:
                position_level = 4  # Менеджер/Старший консультант
            elif experience_years < 12:
                position_level = random.choice([4, 5])  # Руководитель группы/Зам начальника
            else:
                position_level = random.choice([5, 6, 7, 8])  # Высокие должности
            
            # Находим подходящую должность
            suitable_positions = [pos_id for pos_id, pos in ref_data['positions'].items() 
                                if pos.hierarchy_level == position_level]
            position_id = random.choice(suitable_positions)
            
            # Тип сотрудника (90% внутренние, 8% аутстафф, 2% партнеры)
            emp_type_weights = [90, 8, 2]
            emp_type_id = random.choices(list(ref_data['emp_types'].keys()), weights=emp_type_weights)[0]
            
            # Определяем, входит ли в agile команду (90-95% входят)
            in_agile = random.random() > 0.07  # 93% входят в agile
            
            agile_team_id = None
            team_role_id = None
            
            if in_agile:
                # Находим agile команды, связанные с этим управлением
                # (упрощенно - берем случайную команду, в реальности нужна более сложная логика)
                agile_team_id = random.choice(list(ref_data['agile_teams'].keys()))
                team_role_id = get_suitable_team_role(ref_data['team_roles'], profile.name)
            
            # Создаем запись сотрудника
            employee_data = {
                'id': employee_id,
                'full_name': full_name,
                'employee_number': f"EMP{employee_id:06d}",
                'org_unit_id': unit_id,
                'position_id': position_id,
                'profile_id': profile_id,
                'employee_type_id': emp_type_id,
                'agile_team_id': agile_team_id,
                'team_role_id': team_role_id,
                'experience_years': experience_years,
                'status': 'active',
                'hire_date': hire_date,
                'termination_date': None
            }
            
            employees_data.append(employee_data)
            employee_id += 1
    
    # Массовая вставка сотрудников
    logger.info("💾 Сохраняем {len(employees_data)} сотрудников в базу данных...")
    
    async with AsyncSessionLocal() as session:
        batch_size = 100
        for i in range(0, len(employees_data), batch_size):
            batch = employees_data[i:i + batch_size]
            
            for emp_data in batch:
                employee = Employee(**emp_data)
                session.add(employee)
            
            await session.commit()
            logger.info("✅ Сохранено {min(i + batch_size, len(employees_data))}/{len(employees_data)} сотрудников")
    
    logger.info("🎉 Генерация сотрудников завершена!")
    
    # Статистика
    agile_count = sum(1 for emp in employees_data if emp['agile_team_id'] is not None)
    non_agile_count = len(employees_data) - agile_count
    
    logger.info("📊 Статистика:")
    logger.info("   - Всего сотрудников: {len(employees_data)}")
    logger.info("   - В agile командах: {agile_count} ({agile_count/len(employees_data)*100:.1f}%)")
    logger.info("   - Не в agile: {non_agile_count} ({non_agile_count/len(employees_data)*100:.1f}%)")
    logger.info("   - Управлений с сотрудниками: {len(employees_per_directorate)}")


async def main():
    """Главная функция"""
    await generate_employees()


if __name__ == "__main__":
    asyncio.run(main())
