"""
API роуты для организационной структуры
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.api.deps import get_db
from app.models import (
    OrganizationalUnit, Position, EmployeeProfile, EmployeeType,
    TeamRole, Tribe, Product, AgileTeam
)
from app.schemas.organization import (
    # OrganizationalUnit schemas
    OrganizationalUnit as OrganizationalUnitSchema,
    OrganizationalUnitCreate, OrganizationalUnitUpdate, OrganizationalUnitList,
    # Position schemas  
    Position as PositionSchema, PositionCreate, PositionUpdate, PositionList,
    # EmployeeProfile schemas
    EmployeeProfile as EmployeeProfileSchema, EmployeeProfileCreate, EmployeeProfileUpdate,
    # EmployeeType schemas
    EmployeeType as EmployeeTypeSchema, EmployeeTypeCreate,
    # TeamRole schemas
    TeamRole as TeamRoleSchema, TeamRoleCreate,
    # Agile schemas
    Tribe as TribeSchema, TribeCreate, TribeUpdate, TribeList,
    Product as ProductSchema, ProductCreate, ProductUpdate,
    AgileTeam as AgileTeamSchema, AgileTeamCreate, AgileTeamUpdate
)

router = APIRouter()


# ===== ORGANIZATIONAL UNITS =====

@router.get("/org-units/", response_model=OrganizationalUnitList)
async def get_organizational_units(
    page: int = Query(1, ge=1, description="Номер страницы"),
    size: int = Query(50, ge=1, le=100, description="Размер страницы"),
    parent_id: int | None = Query(None, description="ID родительского подразделения"),
    unit_type: str | None = Query(None, description="Тип подразделения"),
    is_active: bool | None = Query(None, description="Только активные"),
    db: AsyncSession = Depends(get_db)
):
    """Получить список подразделений"""
    query = select(OrganizationalUnit)
    
    # Фильтры
    if parent_id is not None:
        query = query.where(OrganizationalUnit.parent_id == parent_id)
    if unit_type:
        query = query.where(OrganizationalUnit.unit_type == unit_type)
    if is_active is not None:
        query = query.where(OrganizationalUnit.is_active == is_active)
    
    # Подсчет общего количества
    total_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(total_query)
    total = total_result.scalar()
    
    # Пагинация
    query = query.offset((page - 1) * size).limit(size)
    query = query.order_by(OrganizationalUnit.level, OrganizationalUnit.name)
    
    result = await db.execute(query)
    items = result.scalars().all()
    
    return OrganizationalUnitList(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size
    )


@router.post("/org-units/", response_model=OrganizationalUnitSchema)
async def create_organizational_unit(
    unit_data: OrganizationalUnitCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создать подразделение"""
    # Генерация path
    path = None
    if unit_data.parent_id:
        parent_result = await db.execute(
            select(OrganizationalUnit).where(OrganizationalUnit.id == unit_data.parent_id)
        )
        parent = parent_result.scalar_one_or_none()
        if not parent:
            raise HTTPException(status_code=404, detail="Родительское подразделение не найдено")
        path = f"{parent.path or ''}/{unit_data.parent_id}"
    
    db_unit = OrganizationalUnit(
        **unit_data.model_dump(),
        path=path
    )
    db.add(db_unit)
    await db.flush()
    await db.refresh(db_unit)
    
    return db_unit


@router.get("/org-units/{unit_id}", response_model=OrganizationalUnitSchema)
async def get_organizational_unit(
    unit_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить подразделение по ID"""
    result = await db.execute(
        select(OrganizationalUnit).where(OrganizationalUnit.id == unit_id)
    )
    unit = result.scalar_one_or_none()
    if not unit:
        raise HTTPException(status_code=404, detail="Подразделение не найдено")
    return unit


@router.put("/org-units/{unit_id}", response_model=OrganizationalUnitSchema)
async def update_organizational_unit(
    unit_id: int,
    unit_data: OrganizationalUnitUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Обновить подразделение"""
    result = await db.execute(
        select(OrganizationalUnit).where(OrganizationalUnit.id == unit_id)
    )
    unit = result.scalar_one_or_none()
    if not unit:
        raise HTTPException(status_code=404, detail="Подразделение не найдено")
    
    update_data = unit_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(unit, field, value)
    
    await db.flush()
    await db.refresh(unit)
    return unit


@router.delete("/org-units/{unit_id}")
async def delete_organizational_unit(
    unit_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Удалить подразделение"""
    result = await db.execute(
        select(OrganizationalUnit).where(OrganizationalUnit.id == unit_id)
    )
    unit = result.scalar_one_or_none()
    if not unit:
        raise HTTPException(status_code=404, detail="Подразделение не найдено")
    
    await db.delete(unit)
    return {"message": "Подразделение удалено"}


# ===== POSITIONS =====

@router.get("/positions/", response_model=PositionList)
async def get_positions(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    is_active: bool | None = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Получить список должностей"""
    query = select(Position)
    
    if is_active is not None:
        query = query.where(Position.is_active == is_active)
    
    # Подсчет общего количества
    total_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(total_query)
    total = total_result.scalar()
    
    # Пагинация
    query = query.offset((page - 1) * size).limit(size)
    query = query.order_by(Position.hierarchy_level, Position.title)
    
    result = await db.execute(query)
    items = result.scalars().all()
    
    return PositionList(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size
    )


@router.post("/positions/", response_model=PositionSchema)
async def create_position(
    position_data: PositionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создать должность"""
    db_position = Position(**position_data.model_dump())
    db.add(db_position)
    await db.flush()
    await db.refresh(db_position)
    return db_position


@router.get("/positions/{position_id}", response_model=PositionSchema)
async def get_position(
    position_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить должность по ID"""
    result = await db.execute(
        select(Position).where(Position.id == position_id)
    )
    position = result.scalar_one_or_none()
    if not position:
        raise HTTPException(status_code=404, detail="Должность не найдена")
    return position


@router.put("/positions/{position_id}", response_model=PositionSchema)
async def update_position(
    position_id: int,
    position_data: PositionUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Обновить должность"""
    result = await db.execute(
        select(Position).where(Position.id == position_id)
    )
    position = result.scalar_one_or_none()
    if not position:
        raise HTTPException(status_code=404, detail="Должность не найдена")
    
    update_data = position_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(position, field, value)
    
    await db.flush()
    await db.refresh(position)
    return position


# ===== EMPLOYEE PROFILES =====

@router.get("/employee-profiles/", response_model=List[EmployeeProfileSchema])
async def get_employee_profiles(
    db: AsyncSession = Depends(get_db)
):
    """Получить список профилей сотрудников"""
    result = await db.execute(
        select(EmployeeProfile).order_by(EmployeeProfile.name)
    )
    return result.scalars().all()


@router.post("/employee-profiles/", response_model=EmployeeProfileSchema)
async def create_employee_profile(
    profile_data: EmployeeProfileCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создать профиль сотрудника"""
    db_profile = EmployeeProfile(**profile_data.model_dump())
    db.add(db_profile)
    await db.flush()
    await db.refresh(db_profile)
    return db_profile


# ===== EMPLOYEE TYPES =====

@router.get("/employee-types/", response_model=List[EmployeeTypeSchema])
async def get_employee_types(
    db: AsyncSession = Depends(get_db)
):
    """Получить список типов сотрудников"""
    result = await db.execute(
        select(EmployeeType).order_by(EmployeeType.name)
    )
    return result.scalars().all()


@router.post("/employee-types/", response_model=EmployeeTypeSchema)
async def create_employee_type(
    type_data: EmployeeTypeCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создать тип сотрудника"""
    db_type = EmployeeType(**type_data.model_dump())
    db.add(db_type)
    await db.flush()
    await db.refresh(db_type)
    return db_type


# ===== TEAM ROLES =====

@router.get("/team-roles/", response_model=List[TeamRoleSchema])
async def get_team_roles(
    db: AsyncSession = Depends(get_db)
):
    """Получить список ролей в командах"""
    result = await db.execute(
        select(TeamRole).order_by(TeamRole.name)
    )
    return result.scalars().all()


@router.post("/team-roles/", response_model=TeamRoleSchema)
async def create_team_role(
    role_data: TeamRoleCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создать роль в команде"""
    db_role = TeamRole(**role_data.model_dump())
    db.add(db_role)
    await db.flush()
    await db.refresh(db_role)
    return db_role


# ===== TRIBES =====

@router.get("/tribes/", response_model=TribeList)
async def get_tribes(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    is_active: bool | None = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Получить список трайбов"""
    query = select(Tribe)
    
    if is_active is not None:
        query = query.where(Tribe.is_active == is_active)
    
    # Подсчет общего количества
    total_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(total_query)
    total = total_result.scalar()
    
    # Пагинация
    query = query.offset((page - 1) * size).limit(size)
    query = query.order_by(Tribe.name)
    
    result = await db.execute(query)
    items = result.scalars().all()
    
    return TribeList(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size
    )


@router.post("/tribes/", response_model=TribeSchema)
async def create_tribe(
    tribe_data: TribeCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создать трайб"""
    db_tribe = Tribe(**tribe_data.model_dump())
    db.add(db_tribe)
    await db.flush()
    await db.refresh(db_tribe)
    return db_tribe


# ===== PRODUCTS =====

@router.get("/products/", response_model=List[ProductSchema])
async def get_products(
    tribe_id: int | None = Query(None, description="Фильтр по трайбу"),
    is_active: bool | None = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Получить список продуктов"""
    query = select(Product).options(selectinload(Product.tribe))
    
    if tribe_id is not None:
        query = query.where(Product.tribe_id == tribe_id)
    if is_active is not None:
        query = query.where(Product.is_active == is_active)
    
    query = query.order_by(Product.name)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/products/", response_model=ProductSchema)
async def create_product(
    product_data: ProductCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создать продукт"""
    db_product = Product(**product_data.model_dump())
    db.add(db_product)
    await db.flush()
    await db.refresh(db_product, ["tribe"])
    return db_product


# ===== AGILE TEAMS =====

@router.get("/agile-teams/", response_model=List[AgileTeamSchema])
async def get_agile_teams(
    product_id: int | None = Query(None, description="Фильтр по продукту"),
    team_type: str | None = Query(None, description="Тип команды: Change/Run"),
    is_active: bool | None = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Получить список agile команд"""
    query = select(AgileTeam).options(selectinload(AgileTeam.product))
    
    if product_id is not None:
        query = query.where(AgileTeam.product_id == product_id)
    if team_type:
        query = query.where(AgileTeam.team_type == team_type)
    if is_active is not None:
        query = query.where(AgileTeam.is_active == is_active)
    
    query = query.order_by(AgileTeam.name)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/agile-teams/", response_model=AgileTeamSchema)
async def create_agile_team(
    team_data: AgileTeamCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создать agile команду"""
    db_team = AgileTeam(**team_data.model_dump())
    db.add(db_team)
    await db.flush()
    await db.refresh(db_team, ["product"])
    return db_team
