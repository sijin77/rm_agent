"""
API роуты для системы доступов
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, delete
from sqlalchemy.orm import selectinload

from app.api.deps import get_db
from app.models import ApplicationSystem, Access, EmployeeAccess
from app.schemas.access import (
    ApplicationSystem as ApplicationSystemSchema,
    ApplicationSystemCreate, ApplicationSystemUpdate,
    Access as AccessSchema, AccessCreate, AccessUpdate, AccessWithSystem,
    EmployeeAccess as EmployeeAccessSchema, EmployeeAccessCreate, EmployeeAccessUpdate,
    EmployeeAccessList, EmployeeAccessFilter, AccessStats,
    BulkAccessAssignment, BulkAccessRevocation
)

router = APIRouter()


# ===== APPLICATION SYSTEMS =====

@router.get("/systems/", response_model=List[ApplicationSystemSchema])
async def get_application_systems(
    system_type: str | None = Query(None, description="Тип системы: IT/Business"),
    criticality: str | None = Query(None, description="Критичность системы"),
    db: AsyncSession = Depends(get_db)
):
    """Получить список прикладных систем"""
    query = select(ApplicationSystem)
    
    if system_type:
        query = query.where(ApplicationSystem.system_type == system_type)
    if criticality:
        query = query.where(ApplicationSystem.criticality == criticality)
    
    query = query.order_by(ApplicationSystem.name)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/systems/", response_model=ApplicationSystemSchema)
async def create_application_system(
    system_data: ApplicationSystemCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создать прикладную систему"""
    db_system = ApplicationSystem(**system_data.model_dump())
    db.add(db_system)
    await db.flush()
    await db.refresh(db_system)
    return db_system


@router.get("/systems/{system_id}", response_model=ApplicationSystemSchema)
async def get_application_system(
    system_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить систему по ID"""
    result = await db.execute(
        select(ApplicationSystem).where(ApplicationSystem.id == system_id)
    )
    system = result.scalar_one_or_none()
    if not system:
        raise HTTPException(status_code=404, detail="Система не найдена")
    return system


@router.put("/systems/{system_id}", response_model=ApplicationSystemSchema)
async def update_application_system(
    system_id: int,
    system_data: ApplicationSystemUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Обновить систему"""
    result = await db.execute(
        select(ApplicationSystem).where(ApplicationSystem.id == system_id)
    )
    system = result.scalar_one_or_none()
    if not system:
        raise HTTPException(status_code=404, detail="Система не найдена")
    
    update_data = system_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(system, field, value)
    
    await db.flush()
    await db.refresh(system)
    return system


# ===== ACCESSES =====

@router.get("/", response_model=List[AccessWithSystem])
async def get_accesses(
    system_id: int | None = Query(None, description="Фильтр по системе"),
    criticality: str | None = Query(None, description="Критичность доступа"),
    system_type: str | None = Query(None, description="Тип системы"),
    db: AsyncSession = Depends(get_db)
):
    """Получить список доступов"""
    query = select(Access).options(selectinload(Access.system))
    
    if system_id is not None:
        query = query.where(Access.system_id == system_id)
    if criticality:
        query = query.where(Access.criticality == criticality)
    if system_type:
        query = query.join(ApplicationSystem).where(ApplicationSystem.system_type == system_type)
    
    query = query.order_by(Access.system_id, Access.role_name)
    
    result = await db.execute(query)
    accesses = result.scalars().all()
    
    # Преобразование в формат с информацией о системе
    items = []
    for access in accesses:
        items.append(AccessWithSystem(
            id=access.id,
            role_name=access.role_name,
            criticality=access.criticality,
            system_name=access.system.name,
            system_type=access.system.system_type,
            system_criticality=access.system.criticality
        ))
    
    return items


@router.post("/", response_model=AccessSchema)
async def create_access(
    access_data: AccessCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создать доступ"""
    # Проверяем существование системы
    system_result = await db.execute(
        select(ApplicationSystem).where(ApplicationSystem.id == access_data.system_id)
    )
    if not system_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Система не найдена")
    
    db_access = Access(**access_data.model_dump())
    db.add(db_access)
    await db.flush()
    await db.refresh(db_access, ["system"])
    return db_access


@router.get("/{access_id}", response_model=AccessSchema)
async def get_access(
    access_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить доступ по ID"""
    result = await db.execute(
        select(Access)
        .options(selectinload(Access.system))
        .where(Access.id == access_id)
    )
    access = result.scalar_one_or_none()
    if not access:
        raise HTTPException(status_code=404, detail="Доступ не найден")
    return access


@router.put("/{access_id}", response_model=AccessSchema)
async def update_access(
    access_id: int,
    access_data: AccessUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Обновить доступ"""
    result = await db.execute(
        select(Access).where(Access.id == access_id)
    )
    access = result.scalar_one_or_none()
    if not access:
        raise HTTPException(status_code=404, detail="Доступ не найден")
    
    update_data = access_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(access, field, value)
    
    await db.flush()
    await db.refresh(access, ["system"])
    return access


@router.delete("/{access_id}")
async def delete_access(
    access_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Удалить доступ"""
    result = await db.execute(
        select(Access).where(Access.id == access_id)
    )
    access = result.scalar_one_or_none()
    if not access:
        raise HTTPException(status_code=404, detail="Доступ не найден")
    
    await db.delete(access)
    return {"message": "Доступ удален"}


# ===== EMPLOYEE ACCESSES =====

@router.get("/assignments/", response_model=EmployeeAccessList)
async def get_employee_accesses(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    employee_id: int | None = Query(None, description="Фильтр по сотруднику"),
    access_id: int | None = Query(None, description="Фильтр по доступу"),
    system_id: int | None = Query(None, description="Фильтр по системе"),
    assignment_type: str | None = Query(None, description="Тип назначения"),
    db: AsyncSession = Depends(get_db)
):
    """Получить список назначений доступов"""
    query = select(EmployeeAccess).options(
        selectinload(EmployeeAccess.access).selectinload(Access.system),
        selectinload(EmployeeAccess.employee),
        selectinload(EmployeeAccess.role_profile)
    )
    
    conditions = []
    if employee_id is not None:
        conditions.append(EmployeeAccess.employee_id == employee_id)
    if access_id is not None:
        conditions.append(EmployeeAccess.access_id == access_id)
    if system_id is not None:
        conditions.append(Access.system_id == system_id)
        query = query.join(Access)
    if assignment_type:
        conditions.append(EmployeeAccess.assignment_type == assignment_type)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    # Подсчет общего количества
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Пагинация
    query = query.offset((page - 1) * size).limit(size)
    query = query.order_by(EmployeeAccess.assigned_at.desc())
    
    result = await db.execute(query)
    assignments = result.scalars().all()
    
    # Преобразование для вывода
    items = []
    for assignment in assignments:
        access_info = None
        if assignment.access:
            access_info = AccessWithSystem(
                id=assignment.access.id,
                role_name=assignment.access.role_name,
                criticality=assignment.access.criticality,
                system_name=assignment.access.system.name,
                system_type=assignment.access.system.system_type,
                system_criticality=assignment.access.system.criticality
            )
        
        items.append(EmployeeAccessSchema(
            id=assignment.id,
            employee_id=assignment.employee_id,
            access_id=assignment.access_id,
            assignment_type=assignment.assignment_type,
            role_profile_id=assignment.role_profile_id,
            assigned_at=assignment.assigned_at,
            last_used=assignment.last_used,
            access=access_info,
            employee_name=assignment.employee.full_name if assignment.employee else None,
            role_profile_name=assignment.role_profile.name if assignment.role_profile else None
        ))
    
    return EmployeeAccessList(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size
    )


@router.post("/assignments/", response_model=EmployeeAccessSchema)
async def create_employee_access(
    assignment_data: EmployeeAccessCreate,
    db: AsyncSession = Depends(get_db)
):
    """Назначить доступ сотруднику"""
    # Проверяем существование сотрудника и доступа
    from app.models import Employee
    
    employee_result = await db.execute(
        select(Employee).where(Employee.id == assignment_data.employee_id)
    )
    if not employee_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Сотрудник не найден")
    
    access_result = await db.execute(
        select(Access).where(Access.id == assignment_data.access_id)
    )
    if not access_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Доступ не найден")
    
    # Проверяем, что назначение еще не существует
    existing_result = await db.execute(
        select(EmployeeAccess).where(
            and_(
                EmployeeAccess.employee_id == assignment_data.employee_id,
                EmployeeAccess.access_id == assignment_data.access_id
            )
        )
    )
    if existing_result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Доступ уже назначен сотруднику")
    
    db_assignment = EmployeeAccess(**assignment_data.model_dump())
    db.add(db_assignment)
    await db.flush()
    await db.refresh(db_assignment, ["access", "employee", "role_profile"])
    return db_assignment


@router.delete("/assignments/{assignment_id}")
async def delete_employee_access(
    assignment_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Отозвать доступ у сотрудника"""
    result = await db.execute(
        select(EmployeeAccess).where(EmployeeAccess.id == assignment_id)
    )
    assignment = result.scalar_one_or_none()
    if not assignment:
        raise HTTPException(status_code=404, detail="Назначение не найдено")
    
    await db.delete(assignment)
    return {"message": "Доступ отозван"}


@router.post("/assignments/bulk", response_model=dict)
async def bulk_assign_accesses(
    assignment_data: BulkAccessAssignment,
    db: AsyncSession = Depends(get_db)
):
    """Массовое назначение доступов"""
    assignments_created = 0
    assignments_skipped = 0
    
    for employee_id in assignment_data.employee_ids:
        for access_id in assignment_data.access_ids:
            # Проверяем, что назначение еще не существует
            existing_result = await db.execute(
                select(EmployeeAccess).where(
                    and_(
                        EmployeeAccess.employee_id == employee_id,
                        EmployeeAccess.access_id == access_id
                    )
                )
            )
            
            if existing_result.scalar_one_or_none():
                assignments_skipped += 1
                continue
            
            db_assignment = EmployeeAccess(
                employee_id=employee_id,
                access_id=access_id,
                assignment_type=assignment_data.assignment_type,
                role_profile_id=assignment_data.role_profile_id
            )
            db.add(db_assignment)
            assignments_created += 1
    
    await db.flush()
    
    return {
        "message": "Массовое назначение завершено",
        "assignments_created": assignments_created,
        "assignments_skipped": assignments_skipped
    }


@router.post("/assignments/bulk-revoke", response_model=dict)
async def bulk_revoke_accesses(
    revocation_data: BulkAccessRevocation,
    db: AsyncSession = Depends(get_db)
):
    """Массовый отзыв доступов"""
    conditions = []
    conditions.append(EmployeeAccess.employee_id.in_(revocation_data.employee_ids))
    conditions.append(EmployeeAccess.access_id.in_(revocation_data.access_ids))
    
    # Подсчитываем количество записей для удаления
    count_result = await db.execute(
        select(func.count()).where(and_(*conditions))
    )
    assignments_revoked = count_result.scalar()
    
    # Удаляем назначения
    await db.execute(
        delete(EmployeeAccess).where(and_(*conditions))
    )
    
    return {
        "message": "Массовый отзыв завершен",
        "assignments_revoked": assignments_revoked,
        "reason": revocation_data.reason
    }


@router.get("/stats/overview", response_model=AccessStats)
async def get_access_stats(
    db: AsyncSession = Depends(get_db)
):
    """Получить статистику по доступам"""
    # Общие счетчики
    total_accesses_result = await db.execute(select(func.count(Access.id)))
    total_accesses = total_accesses_result.scalar()
    
    total_assignments_result = await db.execute(select(func.count(EmployeeAccess.id)))
    total_assignments = total_assignments_result.scalar()
    
    # Заглушки для статистики (в реальности нужны сложные запросы с GROUP BY)
    by_systems = {"GitLab": 120, "Jira": 85, "Confluence": 95}
    by_assignment_type = {"auto_role": 950, "manual_request": 300}
    by_criticality = {"low": 200, "medium": 650, "high": 350, "critical": 50}
    by_system_type = {"IT": 1000, "Business": 250}
    
    return AccessStats(
        total_accesses=total_accesses,
        total_assignments=total_assignments,
        by_systems=by_systems,
        by_assignment_type=by_assignment_type,
        by_criticality=by_criticality,
        by_system_type=by_system_type,
        unused_accesses=15,
        overused_accesses=5
    )
