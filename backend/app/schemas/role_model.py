"""
Pydantic схемы для ролевых моделей
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ===== ROLE MODELS =====

class RoleModelBase(BaseModel):
    name: str = Field(..., example="Ролевая модель ИТ-подразделения", description="Название ролевой модели")
    description: Optional[str] = Field(
        None, 
        example="Ролевая модель для сотрудников ИТ-блока с учетом agile структуры",
        description="Описание ролевой модели"
    )
    author: str = Field(..., example="Система", description="Автор модели")
    version: str = Field("1.0", example="1.0", description="Версия модели")
    is_active: bool = Field(True, example=True, description="Активна ли модель")


class RoleModelCreate(RoleModelBase):
    pass


class RoleModelUpdate(BaseModel):
    name: Optional[str] = Field(None, example="Ролевая модель ИТ v2")
    description: Optional[str] = Field(None, example="Обновленная модель с новыми профилями")
    is_active: Optional[bool] = Field(None, example=True)


class RoleModel(RoleModelBase):
    id: int = Field(..., example=1)
    created_at: datetime
    updated_at: datetime
    
    # Связанные объекты
    profiles_count: Optional[int] = Field(None, example=7, description="Количество профилей")
    employees_covered: Optional[int] = Field(None, example=85, description="Охвачено сотрудников")

    class Config:
        from_attributes = True


class RoleModelWithProfiles(RoleModel):
    """Ролевая модель с профилями"""
    profiles: List["RoleProfile"] = Field(default_factory=list, description="Профили ролевой модели")


# ===== ROLE PROFILES =====

class RoleProfileBase(BaseModel):
    role_model_id: int = Field(..., example=1, description="ID ролевой модели")
    name: str = Field(..., example="Senior Backend разработчики", description="Название профиля")
    description: Optional[str] = Field(
        None,
        example="Опытные разработчики backend сервисов с навыками архитектуры",
        description="Описание профиля"
    )
    criteria: dict = Field(..., example={
        "employee_profiles": ["Java Developer", "Backend Developer"],
        "positions": ["Инженер", "Главный инженер"],
        "org_units_type": ["IT"]
    }, description="Критерии попадания в профиль в JSON формате")


class RoleProfileCreate(RoleProfileBase):
    pass


class RoleProfileUpdate(BaseModel):
    name: Optional[str] = Field(None, example="Senior Backend разработчики v2")
    description: Optional[str] = Field(None, example="Обновленное описание")
    criteria: Optional[dict] = Field(None, example={
        "employee_profiles": ["Java Developer", "Backend Developer", "Fullstack Developer"],
        "positions": ["Инженер", "Главный инженер", "Ведущий специалист"],
        "org_units_type": ["IT"]
    })


class RoleProfile(RoleProfileBase):
    id: int = Field(..., example=5)
    created_at: datetime
    updated_at: datetime
    
    # Дополнительная информация
    matched_employees_count: Optional[int] = Field(None, example=12, description="Количество подходящих сотрудников")
    accesses_count: Optional[int] = Field(None, example=8, description="Количество доступов в профиле")

    class Config:
        from_attributes = True


class RoleProfileWithAccesses(RoleProfile):
    """Профиль роли с доступами"""
    accesses: List["ProfileAccess"] = Field(default_factory=list, description="Доступы профиля")


class RoleProfileWithEmployees(RoleProfile):
    """Профиль роли с подходящими сотрудниками"""
    matched_employees: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Сотрудники, подходящие под критерии"
    )


# ===== PROFILE ACCESSES =====

class ProfileAccessBase(BaseModel):
    role_profile_id: int = Field(..., example=5, description="ID профиля роли")
    access_id: int = Field(..., example=1, description="ID доступа")


class ProfileAccessCreate(ProfileAccessBase):
    pass


class ProfileAccess(ProfileAccessBase):
    id: int = Field(..., example=1)
    created_at: datetime
    
    # Связанные объекты
    access: Optional[Dict[str, Any]] = Field(None, description="Информация о доступе")

    class Config:
        from_attributes = True


# ===== СПИСКИ И СТАТИСТИКА =====

class RoleModelList(BaseModel):
    items: List[RoleModel]
    total: int = Field(..., example=5)
    page: int = Field(1, example=1)
    size: int = Field(50, example=50)
    pages: int = Field(..., example=1)


class RoleProfileList(BaseModel):
    items: List[RoleProfile]
    total: int = Field(..., example=12)
    page: int = Field(1, example=1)
    size: int = Field(50, example=50)
    pages: int = Field(..., example=1)


class RoleModelStats(BaseModel):
    """Статистика по ролевой модели"""
    total_profiles: int = Field(..., example=7)
    total_employees_covered: int = Field(..., example=85)
    total_accesses_assigned: int = Field(..., example=156)
    
    coverage_by_org_units: Dict[str, int] = Field(..., example={"ИТ-блок": 85, "Поддержка": 12})
    coverage_by_positions: Dict[str, int] = Field(..., example={"Инженер": 35, "Главный инженер": 25})
    
    profiles_summary: List[Dict[str, Any]] = Field(
        ...,
        example=[
            {
                "profile_name": "Senior Backend разработчики",
                "employees_count": 12,
                "accesses_count": 8,
                "coverage_percentage": 14.1
            }
        ]
    )


class RoleModelFilter(BaseModel):
    """Фильтры для ролевых моделей"""
    status: Optional[str] = Field(None, example="active", description="Статус")
    author_id: Optional[int] = Field(None, example=456, description="ID автора")
    search: Optional[str] = Field(None, example="ИТ", description="Поиск по названию")


class BulkProfileAccessAssignment(BaseModel):
    """Массовое назначение доступов профилю"""
    role_profile_id: int = Field(..., example=5, description="ID профиля роли")
    access_ids: List[int] = Field(..., example=[1, 2, 3, 4], description="ID доступов для назначения")


# Forward references для циклических зависимостей
RoleModelWithProfiles.model_rebuild()
RoleProfileWithAccesses.model_rebuild()
