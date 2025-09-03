"""
API роуты для сотрудников
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.api.deps import get_db
from app.models import Employee
from app.schemas.employee import (
    Employee as EmployeeSchema,
    EmployeeCreate, EmployeeUpdate, EmployeeList, EmployeeShort,
    EmployeeFilter, EmployeeStats
)

router = APIRouter()


@router.get("/", response_model=EmployeeList)
async def get_employees(
    page: int = Query(1, ge=1, description="Номер страницы"),
    size: int = Query(50, ge=1, le=100, description="Размер страницы"),
    search: str | None = Query(None, description="Поиск по ФИО"),
    org_unit_id: int | None = Query(None, description="Фильтр по подразделению"),
    position_id: int | None = Query(None, description="Фильтр по должности"),
    profile_id: int | None = Query(None, description="Фильтр по профилю"),
    employee_type_id: int | None = Query(None, description="Фильтр по типу сотрудника"),
    agile_team_id: int | None = Query(None, description="Фильтр по agile команде"),
    status: str | None = Query(None, description="Статус сотрудника"),
    db: AsyncSession = Depends(get_db)
):
    """Получить список сотрудников"""
    # Запрос с загрузкой связанных данных для отображения
    query = select(Employee).options(
        selectinload(Employee.org_unit),
        selectinload(Employee.position),
        selectinload(Employee.profile),
        selectinload(Employee.agile_team)
    )
    
    # Фильтры
    conditions = []
    if search:
        conditions.append(Employee.full_name.ilike(f"%{search}%"))
    if org_unit_id is not None:
        conditions.append(Employee.org_unit_id == org_unit_id)
    if position_id is not None:
        conditions.append(Employee.position_id == position_id)
    if profile_id is not None:
        conditions.append(Employee.profile_id == profile_id)
    if employee_type_id is not None:
        conditions.append(Employee.employee_type_id == employee_type_id)
    if agile_team_id is not None:
        conditions.append(Employee.agile_team_id == agile_team_id)
    if status:
        conditions.append(Employee.status == status)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    # Подсчет общего количества
    count_query = select(func.count()).select_from(
        query.subquery()
    )
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Пагинация и сортировка
    query = query.offset((page - 1) * size).limit(size)
    query = query.order_by(Employee.full_name)
    
    result = await db.execute(query)
    employees = result.scalars().all()
    
    # Преобразование в краткий формат для списка
    items = []
    for emp in employees:
        items.append(EmployeeShort(
            id=emp.id,
            full_name=emp.full_name,
            employee_number=emp.employee_number,
            position_title=emp.position.title if emp.position else None,
            profile_name=emp.profile.name if emp.profile else None,
            org_unit_name=emp.org_unit.name if emp.org_unit else None,
            agile_team_name=emp.agile_team.name if emp.agile_team else None,
            status=emp.status
        ))
    
    return EmployeeList(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size
    )


@router.post("/", response_model=EmployeeSchema)
async def create_employee(
    employee_data: EmployeeCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создать сотрудника"""
    db_employee = Employee(**employee_data.model_dump())
    db.add(db_employee)
    await db.flush()
    await db.refresh(db_employee, [
        "org_unit", "position", "profile", "employee_type", 
        "agile_team", "team_role"
    ])
    return db_employee


@router.get("/{employee_id}", response_model=EmployeeSchema)
async def get_employee(
    employee_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить сотрудника по ID"""
    result = await db.execute(
        select(Employee)
        .options(
            selectinload(Employee.org_unit),
            selectinload(Employee.position),
            selectinload(Employee.profile),
            selectinload(Employee.employee_type),
            selectinload(Employee.agile_team),
            selectinload(Employee.team_role)
        )
        .where(Employee.id == employee_id)
    )
    employee = result.scalar_one_or_none()
    if not employee:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")
    
    # Преобразование связанных объектов в словари для Pydantic
    employee_dict = {
        **employee.__dict__,
        "org_unit": employee.org_unit.__dict__ if employee.org_unit else None,
        "position": employee.position.__dict__ if employee.position else None,
        "profile": employee.profile.__dict__ if employee.profile else None,
        "employee_type": employee.employee_type.__dict__ if employee.employee_type else None,
        "agile_team": employee.agile_team.__dict__ if employee.agile_team else None,
        "team_role": employee.team_role.__dict__ if employee.team_role else None,
    }
    
    return EmployeeSchema.model_validate(employee_dict)


@router.put("/{employee_id}", response_model=EmployeeSchema)
async def update_employee(
    employee_id: int,
    employee_data: EmployeeUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Обновить сотрудника"""
    result = await db.execute(
        select(Employee).where(Employee.id == employee_id)
    )
    employee = result.scalar_one_or_none()
    if not employee:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")
    
    update_data = employee_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(employee, field, value)
    
    await db.flush()
    await db.refresh(employee, [
        "org_unit", "position", "profile", "employee_type", 
        "agile_team", "team_role"
    ])
    return employee


@router.delete("/{employee_id}")
async def delete_employee(
    employee_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Удалить сотрудника"""
    result = await db.execute(
        select(Employee).where(Employee.id == employee_id)
    )
    employee = result.scalar_one_or_none()
    if not employee:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")
    
    await db.delete(employee)
    return {"message": "Сотрудник удален"}


@router.post("/filter", response_model=EmployeeList)
async def filter_employees(
    filters: EmployeeFilter,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Расширенный поиск сотрудников по фильтрам"""
    query = select(Employee).options(
        selectinload(Employee.org_unit),
        selectinload(Employee.position),
        selectinload(Employee.profile),
        selectinload(Employee.agile_team)
    )
    
    conditions = []
    
    # Фильтры по ID
    if filters.org_unit_ids:
        conditions.append(Employee.org_unit_id.in_(filters.org_unit_ids))
    if filters.position_ids:
        conditions.append(Employee.position_id.in_(filters.position_ids))
    if filters.profile_ids:
        conditions.append(Employee.profile_id.in_(filters.profile_ids))
    if filters.employee_type_ids:
        conditions.append(Employee.employee_type_id.in_(filters.employee_type_ids))
    if filters.agile_team_ids:
        conditions.append(Employee.agile_team_id.in_(filters.agile_team_ids))
    if filters.team_role_ids:
        conditions.append(Employee.team_role_id.in_(filters.team_role_ids))
    
    # Фильтры по технологиям и навыкам
    if filters.tech_stack:
        for tech in filters.tech_stack:
            conditions.append(Employee.tech_stack.contains([tech]))
    if filters.skills:
        for skill in filters.skills:
            conditions.append(Employee.skills.contains([skill]))
    
    # Фильтры по опыту
    if filters.experience_years_min is not None:
        conditions.append(Employee.experience_years >= filters.experience_years_min)
    if filters.experience_years_max is not None:
        conditions.append(Employee.experience_years <= filters.experience_years_max)
    
    # Прочие фильтры
    if filters.status:
        conditions.append(Employee.status == filters.status)
    if filters.search:
        conditions.append(Employee.full_name.ilike(f"%{filters.search}%"))
    
    if conditions:
        query = query.where(and_(*conditions))
    
    # Подсчет и пагинация
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    query = query.offset((page - 1) * size).limit(size)
    query = query.order_by(Employee.full_name)
    
    result = await db.execute(query)
    employees = result.scalars().all()
    
    # Преобразование в краткий формат
    items = []
    for emp in employees:
        items.append(EmployeeShort(
            id=emp.id,
            full_name=emp.full_name,
            employee_number=emp.employee_number,
            position_title=emp.position.title if emp.position else None,
            profile_name=emp.profile.name if emp.profile else None,
            org_unit_name=emp.org_unit.name if emp.org_unit else None,
            agile_team_name=emp.agile_team.name if emp.agile_team else None,
            status=emp.status
        ))
    
    return EmployeeList(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size
    )


@router.get("/stats/overview", response_model=EmployeeStats)
async def get_employee_stats(
    db: AsyncSession = Depends(get_db)
):
    """Получить статистику по сотрудникам"""
    # Общие счетчики
    total_result = await db.execute(select(func.count(Employee.id)))
    total_employees = total_result.scalar()
    
    active_result = await db.execute(
        select(func.count(Employee.id)).where(Employee.status == "active")
    )
    active_employees = active_result.scalar()
    
    inactive_employees = total_employees - active_employees
    
    # Статистика по подразделениям (заглушка - нужно джойнить с org_units)
    by_org_units = {"ИТ-блок": 85, "Бизнес-блок": 65}
    by_positions = {"Инженер": 45, "Главный инженер": 35}
    by_profiles = {"Senior разработчик": 25, "Middle разработчик": 35}
    by_employee_types = {"Внутренний сотрудник": 120, "Аутстаффер": 30}
    
    # Средние значения
    avg_exp_result = await db.execute(
        select(func.avg(Employee.experience_years)).where(Employee.experience_years.isnot(None))
    )
    avg_experience_years = avg_exp_result.scalar() or 0.0
    
    avg_tenure_result = await db.execute(
        select(func.avg(Employee.company_tenure_months)).where(Employee.company_tenure_months.isnot(None))
    )
    avg_tenure_months = avg_tenure_result.scalar() or 0.0
    
    return EmployeeStats(
        total_employees=total_employees,
        active_employees=active_employees,
        inactive_employees=inactive_employees,
        by_org_units=by_org_units,
        by_positions=by_positions,
        by_profiles=by_profiles,
        by_employee_types=by_employee_types,
        avg_experience_years=float(avg_experience_years),
        avg_tenure_months=float(avg_tenure_months)
    )
