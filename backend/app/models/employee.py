"""
Модели сотрудников
"""
from datetime import date
from typing import List, Optional
from sqlalchemy import String, Integer, Boolean, Date, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Employee(Base, TimestampMixin):
    """Сотрудники компании"""
    __tablename__ = "employees"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    employee_number: Mapped[Optional[str]] = mapped_column(String(50), unique=True)
    full_name: Mapped[str] = mapped_column(String(300), nullable=False)
    
    # Организационная привязка
    org_unit_id: Mapped[int] = mapped_column(ForeignKey("organizational_units.id"), nullable=False)
    position_id: Mapped[int] = mapped_column(ForeignKey("positions.id"), nullable=False)
    profile_id: Mapped[int] = mapped_column(ForeignKey("employee_profiles.id"), nullable=False)
    employee_type_id: Mapped[int] = mapped_column(ForeignKey("employee_types.id"), nullable=False)
    
    # Agile структура
    agile_team_id: Mapped[Optional[int]] = mapped_column(ForeignKey("agile_teams.id"))
    team_role_id: Mapped[Optional[int]] = mapped_column(ForeignKey("team_roles.id"))
    
    # Профессиональные характеристики
    tech_stack: Mapped[Optional[List[str]]] = mapped_column(JSON)
    skills: Mapped[Optional[List[str]]] = mapped_column(JSON)
    experience_years: Mapped[Optional[int]] = mapped_column(Integer)
    company_tenure_months: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Контакты
    email: Mapped[Optional[str]] = mapped_column(String(255))
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Статусы
    status: Mapped[str] = mapped_column(String(20), default="active")
    hire_date: Mapped[Optional[date]] = mapped_column(Date)
    termination_date: Mapped[Optional[date]] = mapped_column(Date)
    
    # Relationships
    org_unit: Mapped["OrganizationalUnit"] = relationship("OrganizationalUnit", foreign_keys=[org_unit_id], back_populates="employees")
    position: Mapped["Position"] = relationship("Position", back_populates="employees")
    profile: Mapped["EmployeeProfile"] = relationship("EmployeeProfile", back_populates="employees")
    employee_type: Mapped["EmployeeType"] = relationship("EmployeeType", back_populates="employees")
    agile_team: Mapped[Optional["AgileTeam"]] = relationship("AgileTeam", back_populates="employees")
    team_role: Mapped[Optional["TeamRole"]] = relationship("TeamRole", back_populates="employees")
    
    # Доступы
    employee_accesses: Mapped[List["EmployeeAccess"]] = relationship("EmployeeAccess", back_populates="employee")
