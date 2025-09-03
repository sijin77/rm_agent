"""
Pydantic схемы для сотрудников
"""
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr


class EmployeeBase(BaseModel):
    employee_number: Optional[str] = Field(None, example="EMP001", description="Табельный номер")
    full_name: str = Field(..., example="Иванов Иван Иванович", description="ФИО сотрудника")
    org_unit_id: int = Field(..., example=5, description="ID подразделения")
    position_id: int = Field(..., example=2, description="ID должности")
    profile_id: int = Field(..., example=15, description="ID профиля")
    employee_type_id: int = Field(..., example=1, description="ID типа сотрудника")
    agile_team_id: Optional[int] = Field(None, example=3, description="ID agile команды")
    team_role_id: Optional[int] = Field(None, example=7, description="ID роли в команде")
    
    tech_stack: Optional[List[str]] = Field(
        default_factory=list, 
        example=["Java", "Spring", "PostgreSQL", "Docker"], 
        description="Технологический стек"
    )
    skills: Optional[List[str]] = Field(
        default_factory=list,
        example=["AWS", "Kubernetes", "Agile", "Mentoring"],
        description="Навыки и сертификации"
    )
    experience_years: Optional[int] = Field(None, example=5, description="Общий опыт работы в годах")
    company_tenure_months: Optional[int] = Field(None, example=36, description="Стаж в компании в месяцах")
    
    email: Optional[EmailStr] = Field(None, example="ivan.ivanov@company.com", description="Email")
    phone: Optional[str] = Field(None, example="+7 (999) 123-45-67", description="Телефон")
    status: str = Field("active", example="active", description="Статус: active/inactive/on_leave")
    hire_date: Optional[date] = Field(None, example="2021-03-15", description="Дата найма")
    termination_date: Optional[date] = Field(None, example=None, description="Дата увольнения")


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    full_name: Optional[str] = Field(None, example="Иванов Иван Петрович")
    org_unit_id: Optional[int] = Field(None, example=6)
    position_id: Optional[int] = Field(None, example=3)
    profile_id: Optional[int] = Field(None, example=16)
    employee_type_id: Optional[int] = Field(None, example=1)
    agile_team_id: Optional[int] = Field(None, example=4)
    team_role_id: Optional[int] = Field(None, example=8)
    
    tech_stack: Optional[List[str]] = Field(None, example=["Python", "FastAPI", "React"])
    skills: Optional[List[str]] = Field(None, example=["GCP", "Terraform", "DevOps"])
    experience_years: Optional[int] = Field(None, example=6)
    company_tenure_months: Optional[int] = Field(None, example=42)
    
    email: Optional[EmailStr] = Field(None, example="ivan.new@company.com")
    phone: Optional[str] = Field(None, example="+7 (999) 987-65-43")
    status: Optional[str] = Field(None, example="active")
    hire_date: Optional[date] = Field(None, example="2021-03-15")
    termination_date: Optional[date] = Field(None, example=None)


class Employee(EmployeeBase):
    id: int = Field(..., example=123)
    created_at: datetime
    updated_at: datetime
    
    # Связанные объекты (опционально подгружаются)
    org_unit: Optional[Dict[str, Any]] = Field(None, description="Подразделение")
    position: Optional[Dict[str, Any]] = Field(None, description="Должность")
    profile: Optional[Dict[str, Any]] = Field(None, description="Профиль")
    employee_type: Optional[Dict[str, Any]] = Field(None, description="Тип сотрудника")
    agile_team: Optional[Dict[str, Any]] = Field(None, description="Agile команда")
    team_role: Optional[Dict[str, Any]] = Field(None, description="Роль в команде")

    class Config:
        from_attributes = True


class EmployeeShort(BaseModel):
    """Краткая информация о сотруднике для списков"""
    id: int = Field(..., example=123)
    full_name: str = Field(..., example="Иванов Иван Иванович")
    employee_number: Optional[str] = Field(None, example="EMP001")
    position_title: Optional[str] = Field(None, example="Главный инженер")
    profile_name: Optional[str] = Field(None, example="Senior Java разработчик")
    org_unit_name: Optional[str] = Field(None, example="Backend отдел")
    agile_team_name: Optional[str] = Field(None, example="Gateway Change Team")
    status: str = Field(..., example="active")

    class Config:
        from_attributes = True


class EmployeeList(BaseModel):
    items: List[EmployeeShort]
    total: int = Field(..., example=150, description="Общее количество сотрудников")
    page: int = Field(1, example=1, description="Текущая страница")
    size: int = Field(50, example=50, description="Размер страницы")
    pages: int = Field(..., example=3, description="Общее количество страниц")


class EmployeeFilter(BaseModel):
    """Фильтры для поиска сотрудников"""
    org_unit_ids: Optional[List[int]] = Field(None, example=[1, 5, 12], description="ID подразделений")
    position_ids: Optional[List[int]] = Field(None, example=[2, 3], description="ID должностей")
    profile_ids: Optional[List[int]] = Field(None, example=[15, 16], description="ID профилей")
    employee_type_ids: Optional[List[int]] = Field(None, example=[1], description="ID типов сотрудников")
    agile_team_ids: Optional[List[int]] = Field(None, example=[3, 7], description="ID agile команд")
    team_role_ids: Optional[List[int]] = Field(None, example=[7, 8], description="ID ролей в командах")
    
    tech_stack: Optional[List[str]] = Field(None, example=["Java", "Python"], description="Технологии")
    skills: Optional[List[str]] = Field(None, example=["AWS", "Kubernetes"], description="Навыки")
    
    experience_years_min: Optional[int] = Field(None, example=3, description="Минимальный опыт")
    experience_years_max: Optional[int] = Field(None, example=10, description="Максимальный опыт")
    
    status: Optional[str] = Field(None, example="active", description="Статус")
    search: Optional[str] = Field(None, example="Иванов", description="Поиск по ФИО")


class EmployeeStats(BaseModel):
    """Статистика по сотрудникам"""
    total_employees: int = Field(..., example=150)
    active_employees: int = Field(..., example=145)
    inactive_employees: int = Field(..., example=5)
    
    by_org_units: Dict[str, int] = Field(..., example={"ИТ-блок": 85, "Бизнес-блок": 65})
    by_positions: Dict[str, int] = Field(..., example={"Инженер": 45, "Главный инженер": 35})
    by_profiles: Dict[str, int] = Field(..., example={"Senior разработчик": 25, "Middle разработчик": 35})
    by_employee_types: Dict[str, int] = Field(..., example={"Внутренний сотрудник": 120, "Аутстаффер": 30})
    
    avg_experience_years: float = Field(..., example=5.2)
    avg_tenure_months: float = Field(..., example=28.5)
