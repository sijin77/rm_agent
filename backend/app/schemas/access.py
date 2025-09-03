"""
Pydantic схемы для системы доступов
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ===== APPLICATION SYSTEMS =====

class ApplicationSystemBase(BaseModel):
    name: str = Field(..., example="GitLab", description="Название АС")
    criticality: str = Field(..., example="high", description="Критичность: low/medium/high/critical")
    system_type: str = Field(..., example="IT", description="Тип системы: IT/Business")


class ApplicationSystemCreate(ApplicationSystemBase):
    pass


class ApplicationSystemUpdate(BaseModel):
    name: Optional[str] = Field(None, example="GitLab CE")
    criticality: Optional[str] = Field(None, example="critical")
    system_type: Optional[str] = Field(None, example="IT")


class ApplicationSystem(ApplicationSystemBase):
    id: int = Field(..., example=1)
    created_at: datetime

    class Config:
        from_attributes = True


# ===== ACCESSES =====

class AccessBase(BaseModel):
    system_id: int = Field(..., example=1, description="ID системы")
    role_name: str = Field(..., example="Developer", description="Название роли в системе")
    criticality: str = Field(..., example="medium", description="Критичность доступа")


class AccessCreate(AccessBase):
    pass


class AccessUpdate(BaseModel):
    role_name: Optional[str] = Field(None, example="Senior Developer")
    criticality: Optional[str] = Field(None, example="high")


class Access(AccessBase):
    id: int = Field(..., example=1)
    created_at: datetime
    system: Optional[ApplicationSystem] = None

    class Config:
        from_attributes = True


class AccessWithSystem(BaseModel):
    """Доступ с информацией о системе"""
    id: int = Field(..., example=1)
    role_name: str = Field(..., example="Developer")
    criticality: str = Field(..., example="medium")
    system_name: str = Field(..., example="GitLab")
    system_type: str = Field(..., example="IT")
    system_criticality: str = Field(..., example="high")

    class Config:
        from_attributes = True


# ===== EMPLOYEE ACCESSES =====

class EmployeeAccessBase(BaseModel):
    employee_id: int = Field(..., example=123, description="ID сотрудника")
    access_id: int = Field(..., example=1, description="ID доступа")
    assignment_type: str = Field(..., example="auto_role", description="Тип назначения: auto_role/manual_request")
    role_profile_id: Optional[int] = Field(None, example=5, description="ID профиля роли (для auto_role)")


class EmployeeAccessCreate(EmployeeAccessBase):
    pass


class EmployeeAccessUpdate(BaseModel):
    assignment_type: Optional[str] = Field(None, example="manual_request")
    role_profile_id: Optional[int] = Field(None, example=None)


class EmployeeAccess(EmployeeAccessBase):
    id: int = Field(..., example=1)
    assigned_at: datetime
    last_used: Optional[datetime] = Field(None, description="Последнее использование")
    
    # Связанные объекты
    access: Optional[AccessWithSystem] = None
    employee_name: Optional[str] = Field(None, example="Иванов Иван Иванович")
    role_profile_name: Optional[str] = Field(None, example="Senior Backend разработчики")

    class Config:
        from_attributes = True


class EmployeeAccessList(BaseModel):
    items: List[EmployeeAccess]
    total: int = Field(..., example=250)
    page: int = Field(1, example=1)
    size: int = Field(50, example=50)
    pages: int = Field(..., example=5)


class EmployeeAccessFilter(BaseModel):
    """Фильтры для поиска назначений доступов"""
    employee_ids: Optional[List[int]] = Field(None, example=[123, 124], description="ID сотрудников")
    access_ids: Optional[List[int]] = Field(None, example=[1, 2], description="ID доступов")
    system_ids: Optional[List[int]] = Field(None, example=[1, 2], description="ID систем")
    assignment_type: Optional[str] = Field(None, example="auto_role", description="Тип назначения")
    role_profile_ids: Optional[List[int]] = Field(None, example=[5, 6], description="ID профилей ролей")
    criticality: Optional[List[str]] = Field(None, example=["high", "critical"], description="Критичность")
    system_type: Optional[str] = Field(None, example="IT", description="Тип системы")


class AccessStats(BaseModel):
    """Статистика по доступам"""
    total_accesses: int = Field(..., example=45)
    total_assignments: int = Field(..., example=1250)
    
    by_systems: Dict[str, int] = Field(..., example={"GitLab": 120, "Jira": 85, "Confluence": 95})
    by_assignment_type: Dict[str, int] = Field(..., example={"auto_role": 950, "manual_request": 300})
    by_criticality: Dict[str, int] = Field(..., example={"low": 200, "medium": 650, "high": 350, "critical": 50})
    by_system_type: Dict[str, int] = Field(..., example={"IT": 1000, "Business": 250})
    
    unused_accesses: int = Field(..., example=15, description="Доступы без назначений")
    overused_accesses: int = Field(..., example=5, description="Доступы с >100 назначениями")


class BulkAccessAssignment(BaseModel):
    """Массовое назначение доступов"""
    employee_ids: List[int] = Field(..., example=[123, 124, 125], description="ID сотрудников")
    access_ids: List[int] = Field(..., example=[1, 2, 3], description="ID доступов")
    assignment_type: str = Field("manual_request", example="manual_request", description="Тип назначения")
    role_profile_id: Optional[int] = Field(None, example=5, description="ID профиля роли")


class BulkAccessRevocation(BaseModel):
    """Массовый отзыв доступов"""
    employee_ids: List[int] = Field(..., example=[123, 124], description="ID сотрудников")
    access_ids: List[int] = Field(..., example=[1, 2], description="ID доступов")
    reason: Optional[str] = Field(None, example="Смена роли", description="Причина отзыва")
