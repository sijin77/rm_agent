"""
API роуты для ролевых моделей
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.api.deps import get_db
from app.models import RoleModel, RoleProfile, ProfileAccess, Employee, EmployeeProfile, Position, OrganizationalUnit, EmployeeType
from app.schemas.role_model import (
    RoleModel as RoleModelSchema,
    RoleModelCreate, RoleModelUpdate, RoleModelList,
    RoleProfile as RoleProfileSchema,
    RoleProfileCreate, RoleProfileUpdate, RoleProfileList,
    RoleProfileWithEmployees, RoleModelStats
)

router = APIRouter()


@router.get("/", response_model=RoleModelList)
async def get_role_models(
    page: int = Query(1, ge=1, description="Номер страницы"),
    size: int = Query(50, ge=1, le=100, description="Размер страницы"),
    search: str | None = Query(None, description="Поиск по названию"),
    status: str | None = Query(None, description="Статус модели"),
    db: AsyncSession = Depends(get_db)
):
    """Получить список ролевых моделей"""
    query = select(RoleModel).options(
        selectinload(RoleModel.profiles)
    )
    
    # Фильтры
    conditions = []
    if search:
        conditions.append(RoleModel.name.ilike(f"%{search}%"))
    if status:
        conditions.append(RoleModel.is_active == (status == "active"))
    
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
    query = query.order_by(RoleModel.created_at.desc())
    
    result = await db.execute(query)
    role_models = result.scalars().all()
    
    # Преобразование в схемы с подсчетом профилей
    items = []
    for rm in role_models:
        items.append(RoleModelSchema(
            id=rm.id,
            name=rm.name,
            description=rm.description,
            author=rm.author,
            version=rm.version,
            is_active=rm.is_active,
            created_at=rm.created_at,
            updated_at=rm.updated_at,
            profiles_count=len(rm.profiles),
            employees_covered=None  # Будет вычисляться отдельно
        ))
    
    return RoleModelList(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size
    )


@router.post("/", response_model=RoleModelSchema)
async def create_role_model(
    role_model_data: RoleModelCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создать ролевую модель"""
    db_role_model = RoleModel(**role_model_data.model_dump())
    db.add(db_role_model)
    await db.flush()
    await db.refresh(db_role_model)
    return db_role_model


@router.get("/{role_model_id}", response_model=RoleModelSchema)
async def get_role_model(
    role_model_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить ролевую модель по ID"""
    result = await db.execute(
        select(RoleModel)
        .options(selectinload(RoleModel.profiles))
        .where(RoleModel.id == role_model_id)
    )
    role_model = result.scalar_one_or_none()
    if not role_model:
        raise HTTPException(status_code=404, detail="Ролевая модель не найдена")
    
    return RoleModelSchema(
        id=role_model.id,
        name=role_model.name,
        description=role_model.description,
        author=role_model.author,
        version=role_model.version,
        is_active=role_model.is_active,
        created_at=role_model.created_at,
        updated_at=role_model.updated_at,
        profiles_count=len(role_model.profiles),
        employees_covered=None
    )


@router.put("/{role_model_id}", response_model=RoleModelSchema)
async def update_role_model(
    role_model_id: int,
    role_model_data: RoleModelUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Обновить ролевую модель"""
    result = await db.execute(
        select(RoleModel).where(RoleModel.id == role_model_id)
    )
    role_model = result.scalar_one_or_none()
    if not role_model:
        raise HTTPException(status_code=404, detail="Ролевая модель не найдена")
    
    update_data = role_model_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(role_model, field, value)
    
    await db.flush()
    await db.refresh(role_model)
    return role_model


@router.delete("/{role_model_id}")
async def delete_role_model(
    role_model_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Удалить ролевую модель"""
    result = await db.execute(
        select(RoleModel).where(RoleModel.id == role_model_id)
    )
    role_model = result.scalar_one_or_none()
    if not role_model:
        raise HTTPException(status_code=404, detail="Ролевая модель не найдена")
    
    await db.delete(role_model)
    return {"message": "Ролевая модель удалена"}


@router.get("/{role_model_id}/profiles", response_model=RoleProfileList)
async def get_role_model_profiles(
    role_model_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Получить профили ролевой модели"""
    # Проверяем существование ролевой модели
    role_model_result = await db.execute(
        select(RoleModel).where(RoleModel.id == role_model_id)
    )
    if not role_model_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Ролевая модель не найдена")
    
    query = select(RoleProfile).options(
        selectinload(RoleProfile.profile_accesses)
    ).where(RoleProfile.role_model_id == role_model_id)
    
    # Подсчет общего количества
    count_query = select(func.count()).select_from(
        query.subquery()
    )
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Пагинация и сортировка
    query = query.offset((page - 1) * size).limit(size)
    query = query.order_by(RoleProfile.name)
    
    result = await db.execute(query)
    profiles = result.scalars().all()
    
    # Преобразование в схемы
    items = []
    for profile in profiles:
        items.append(RoleProfileSchema(
            id=profile.id,
            role_model_id=profile.role_model_id,
            name=profile.name,
            description=profile.description,
            criteria=profile.criteria,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
            matched_employees_count=None,  # Будет вычисляться отдельно
            accesses_count=len(profile.profile_accesses)
        ))
    
    return RoleProfileList(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size
    )


@router.get("/{role_model_id}/stats", response_model=RoleModelStats)
async def get_role_model_stats(
    role_model_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить статистику ролевой модели"""
    # Проверяем существование ролевой модели
    role_model_result = await db.execute(
        select(RoleModel).where(RoleModel.id == role_model_id)
    )
    role_model = role_model_result.scalar_one_or_none()
    if not role_model:
        raise HTTPException(status_code=404, detail="Ролевая модель не найдена")
    
    # Получаем профили модели
    profiles_result = await db.execute(
        select(RoleProfile).where(RoleProfile.role_model_id == role_model_id)
    )
    profiles = profiles_result.scalars().all()
    
    total_profiles = len(profiles)
    total_accesses_assigned = 0
    total_employees_covered = 0
    
    profiles_summary = []
    coverage_by_org_units = {}
    coverage_by_positions = {}
    
    for profile in profiles:
        # Подсчитываем доступы
        accesses_count = len(profile.profile_accesses)
        total_accesses_assigned += accesses_count
        
        # Подсчитываем сотрудников по критериям профиля
        employees_count = await _count_matching_employees(profile.criteria, db)
        total_employees_covered += employees_count
        
        # Добавляем в сводку
        profiles_summary.append({
            "profile_name": profile.name,
            "employees_count": employees_count,
            "accesses_count": accesses_count,
            "coverage_percentage": 0.0  # Будет вычислено позже
        })
    
    # Вычисляем проценты покрытия
    if total_employees_covered > 0:
        for summary in profiles_summary:
            summary["coverage_percentage"] = round(
                (summary["employees_count"] / total_employees_covered) * 100, 1
            )
    
    return RoleModelStats(
        total_profiles=total_profiles,
        total_employees_covered=total_employees_covered,
        total_accesses_assigned=total_accesses_assigned,
        coverage_by_org_units=coverage_by_org_units,
        coverage_by_positions=coverage_by_positions,
        profiles_summary=profiles_summary
    )


# ===== ROLE PROFILES =====

@router.get("/profiles/{profile_id}", response_model=RoleProfileSchema)
async def get_role_profile(
    profile_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить профиль роли по ID"""
    result = await db.execute(
        select(RoleProfile)
        .options(selectinload(RoleProfile.profile_accesses))
        .where(RoleProfile.id == profile_id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Профиль роли не найден")
    
    # Подсчитываем количество подходящих сотрудников
    employees_count = await _count_matching_employees(profile.criteria, db)
    
    return RoleProfileSchema(
        id=profile.id,
        role_model_id=profile.role_model_id,
        name=profile.name,
        description=profile.description,
        criteria=profile.criteria,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
        matched_employees_count=employees_count,
        accesses_count=len(profile.profile_accesses)
    )


@router.get("/profiles/{profile_id}/employees", response_model=RoleProfileWithEmployees)
async def get_profile_matching_employees(
    profile_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Получить сотрудников, подходящих под критерии профиля"""
    # Получаем профиль
    profile_result = await db.execute(
        select(RoleProfile).where(RoleProfile.id == profile_id)
    )
    profile = profile_result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Профиль роли не найден")
    
    # Получаем сотрудников по критериям
    employees = await _get_matching_employees(profile.criteria, db, page, size)
    
    # Подсчитываем общее количество
    total_count = await _count_matching_employees(profile.criteria, db)
    
    return RoleProfileWithEmployees(
        id=profile.id,
        role_model_id=profile.role_model_id,
        name=profile.name,
        description=profile.description,
        criteria=profile.criteria,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
        matched_employees_count=total_count,
        accesses_count=0,  # Будет загружено отдельно
        matched_employees=employees
    )


@router.get("/profiles/{profile_id}/employees/count")
async def get_profile_employees_count(
    profile_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить количество сотрудников, подходящих под критерии профиля"""
    # Получаем профиль
    profile_result = await db.execute(
        select(RoleProfile).where(RoleProfile.id == profile_id)
    )
    profile = profile_result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Профиль роли не найден")
    
    # Подсчитываем сотрудников по критериям
    count = await _count_matching_employees(profile.criteria, db)
    
    return {"profile_id": profile_id, "employees_count": count}


# ===== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====

async def _count_matching_employees(criteria: dict, db: AsyncSession) -> int:
    """Подсчитать количество сотрудников, подходящих под критерии"""
    query = select(func.count(Employee.id))
    
    conditions = []
    
    # Критерии из JSON поля criteria
    if "employee_profiles" in criteria:
        # Поиск по названиям профилей сотрудников
        profile_names = criteria["employee_profiles"]
        if profile_names:
            conditions.append(
                Employee.profile.has(EmployeeProfile.name.in_(profile_names))
            )
    
    if "positions" in criteria:
        # Поиск по названиям должностей
        position_names = criteria["positions"]
        if position_names:
            conditions.append(
                Employee.position.has(Position.title.in_(position_names))
            )
    
    if "org_units_type" in criteria:
        # Поиск по типам подразделений
        org_types = criteria["org_units_type"]
        if org_types:
            conditions.append(
                Employee.org_unit.has(OrganizationalUnit.type.in_(org_types))
            )
    
    if "employee_types" in criteria:
        # Поиск по типам сотрудников
        employee_type_names = criteria["employee_types"]
        if employee_type_names:
            conditions.append(
                Employee.employee_type.has(EmployeeType.name.in_(employee_type_names))
            )
    
    if "all_employees" in criteria and criteria["all_employees"]:
        # Если критерий "все сотрудники", то не добавляем дополнительных условий
        pass
    elif conditions:
        query = query.where(and_(*conditions))
    else:
        # Если нет критериев, возвращаем 0
        return 0
    
    result = await db.execute(query)
    return result.scalar() or 0


async def _get_matching_employees(criteria: dict, db: AsyncSession, page: int = 1, size: int = 50) -> List[dict]:
    """Получить список сотрудников, подходящих под критерии"""
    query = select(Employee).options(
        selectinload(Employee.profile),
        selectinload(Employee.position),
        selectinload(Employee.org_unit),
        selectinload(Employee.employee_type)
    )
    
    conditions = []
    
    # Критерии из JSON поля criteria
    if "employee_profiles" in criteria:
        profile_names = criteria["employee_profiles"]
        if profile_names:
            conditions.append(
                Employee.profile.has(EmployeeProfile.name.in_(profile_names))
            )
    
    if "positions" in criteria:
        position_names = criteria["positions"]
        if position_names:
            conditions.append(
                Employee.position.has(Position.title.in_(position_names))
            )
    
    if "org_units_type" in criteria:
        org_types = criteria["org_units_type"]
        if org_types:
            conditions.append(
                Employee.org_unit.has(OrganizationalUnit.type.in_(org_types))
            )
    
    if "employee_types" in criteria:
        employee_type_names = criteria["employee_types"]
        if employee_type_names:
            conditions.append(
                Employee.employee_type.has(EmployeeType.name.in_(employee_type_names))
            )
    
    if "all_employees" in criteria and criteria["all_employees"]:
        # Если критерий "все сотрудники", то не добавляем дополнительных условий
        pass
    elif conditions:
        query = query.where(and_(*conditions))
    else:
        # Если нет критериев, возвращаем пустой список
        return []
    
    # Пагинация и сортировка
    query = query.offset((page - 1) * size).limit(size)
    query = query.order_by(Employee.full_name)
    
    result = await db.execute(query)
    employees = result.scalars().all()
    
    # Преобразование в словари
    employee_list = []
    for emp in employees:
        employee_list.append({
            "id": emp.id,
            "full_name": emp.full_name,
            "employee_number": emp.employee_number,
            "profile_name": emp.profile.name if emp.profile else None,
            "position_title": emp.position.title if emp.position else None,
            "org_unit_name": emp.org_unit.name if emp.org_unit else None,
            "employee_type_name": emp.employee_type.name if emp.employee_type else None,
            "status": emp.status
        })
    
    return employee_list
