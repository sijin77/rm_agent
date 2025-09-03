"""
Pydantic схемы для организационной структуры
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


# ===== ORGANIZATIONAL UNITS =====

class OrganizationalUnitBase(BaseModel):
    name: str = Field(..., example="ИТ-блок", description="Название подразделения")
    code: Optional[str] = Field(None, example="IT", description="Код подразделения")
    unit_type: str = Field(..., example="block", description="Тип: block/department/directorate/division")
    parent_id: Optional[int] = Field(None, example=1, description="ID родительского подразделения")
    level: int = Field(..., example=1, description="Уровень в иерархии")
    description: Optional[str] = Field(None, example="Информационные технологии", description="Описание")
    is_active: bool = Field(True, description="Активно ли подразделение")


class OrganizationalUnitCreate(OrganizationalUnitBase):
    head_employee_id: Optional[int] = Field(None, example=123, description="ID руководителя")


class OrganizationalUnitUpdate(BaseModel):
    name: Optional[str] = Field(None, example="ИТ-блок (обновлен)")
    code: Optional[str] = Field(None, example="IT_NEW")
    description: Optional[str] = Field(None)
    head_employee_id: Optional[int] = Field(None)
    is_active: Optional[bool] = Field(None)


class OrganizationalUnit(OrganizationalUnitBase):
    id: int = Field(..., example=1)
    path: Optional[str] = Field(None, example="/1/5/12", description="Путь в иерархии")
    head_employee_id: Optional[int] = Field(None, example=123)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===== POSITIONS =====

class PositionBase(BaseModel):
    title: str = Field(..., example="Главный инженер", description="Название должности")
    code: Optional[str] = Field(None, example="CHIEF_ENG", description="Код должности")
    hierarchy_level: int = Field(..., example=2, description="Уровень в иерархии")
    description: Optional[str] = Field(None, example="Старшая инженерная должность")
    is_active: bool = Field(True, description="Активна ли должность")


class PositionCreate(PositionBase):
    pass


class PositionUpdate(BaseModel):
    title: Optional[str] = Field(None, example="Ведущий инженер")
    description: Optional[str] = Field(None)
    is_active: Optional[bool] = Field(None)


class Position(PositionBase):
    id: int = Field(..., example=1)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===== EMPLOYEE PROFILES =====

class EmployeeProfileBase(BaseModel):
    name: str = Field(..., example="Senior Java разработчик", description="Название профиля")


class EmployeeProfileCreate(EmployeeProfileBase):
    pass


class EmployeeProfileUpdate(BaseModel):
    name: Optional[str] = Field(None, example="Senior Python разработчик")


class EmployeeProfile(EmployeeProfileBase):
    id: int = Field(..., example=1)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===== EMPLOYEE TYPES =====

class EmployeeTypeBase(BaseModel):
    name: str = Field(..., example="Внутренний сотрудник", description="Тип сотрудника")


class EmployeeTypeCreate(EmployeeTypeBase):
    pass


class EmployeeType(EmployeeTypeBase):
    id: int = Field(..., example=1)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===== TEAM ROLES =====

class TeamRoleBase(BaseModel):
    name: str = Field(..., example="Tech Lead", description="Роль в команде")


class TeamRoleCreate(TeamRoleBase):
    pass


class TeamRole(TeamRoleBase):
    id: int = Field(..., example=1)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===== AGILE STRUCTURE =====

class TribeBase(BaseModel):
    name: str = Field(..., example="Платформа", description="Название трайба")
    description: Optional[str] = Field(None, example="Платформенные решения")
    is_active: bool = Field(True, description="Активен ли трайб")


class TribeCreate(TribeBase):
    pass


class TribeUpdate(BaseModel):
    name: Optional[str] = Field(None, example="Платформа v2")
    description: Optional[str] = Field(None)
    is_active: Optional[bool] = Field(None)


class Tribe(TribeBase):
    id: int = Field(..., example=1)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    name: str = Field(..., example="API Gateway", description="Название продукта/сервиса")
    tribe_id: int = Field(..., example=1, description="ID трайба")
    type: str = Field("product", example="product", description="Тип: product/service")
    is_active: bool = Field(True, description="Активен ли продукт")


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, example="API Gateway v2")
    type: Optional[str] = Field(None, example="service")
    is_active: Optional[bool] = Field(None)


class Product(ProductBase):
    id: int = Field(..., example=1)
    created_at: datetime
    updated_at: datetime
    tribe: Optional[Tribe] = None

    class Config:
        from_attributes = True


class AgileTeamBase(BaseModel):
    name: str = Field(..., example="Gateway Change Team", description="Название команды")
    product_id: int = Field(..., example=1, description="ID продукта")
    team_type: str = Field(..., example="Change", description="Тип команды: Change/Run")
    is_active: bool = Field(True, description="Активна ли команда")


class AgileTeamCreate(AgileTeamBase):
    pass


class AgileTeamUpdate(BaseModel):
    name: Optional[str] = Field(None, example="Gateway Team v2")
    team_type: Optional[str] = Field(None, example="Run")
    is_active: Optional[bool] = Field(None)


class AgileTeam(AgileTeamBase):
    id: int = Field(..., example=1)
    created_at: datetime
    updated_at: datetime
    product: Optional[Product] = None

    class Config:
        from_attributes = True


# ===== СПИСКИ С ПАГИНАЦИЕЙ =====

class OrganizationalUnitList(BaseModel):
    items: List[OrganizationalUnit]
    total: int = Field(..., example=25, description="Общее количество")
    page: int = Field(1, example=1, description="Текущая страница")
    size: int = Field(50, example=50, description="Размер страницы")
    pages: int = Field(..., example=1, description="Общее количество страниц")


class PositionList(BaseModel):
    items: List[Position]
    total: int = Field(..., example=4)
    page: int = Field(1, example=1)
    size: int = Field(50, example=50)
    pages: int = Field(..., example=1)


class TribeList(BaseModel):
    items: List[Tribe]
    total: int = Field(..., example=5)
    page: int = Field(1, example=1)
    size: int = Field(50, example=50)
    pages: int = Field(..., example=1)
