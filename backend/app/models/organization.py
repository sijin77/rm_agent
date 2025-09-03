"""
Модели организационной структуры
"""
from typing import List, Optional
from sqlalchemy import String, Integer, Boolean, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class OrganizationalUnit(Base, TimestampMixin):
    """Организационная структура: Блок/Департамент/Управление/Отдел"""
    __tablename__ = "organizational_units"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[Optional[str]] = mapped_column(String(50))
    unit_type: Mapped[str] = mapped_column(String(20), nullable=False)  # block/department/directorate/division
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("organizational_units.id"))
    level: Mapped[int] = mapped_column(Integer, nullable=False)
    path: Mapped[Optional[str]] = mapped_column(String(500))  # /1/5/12/25
    head_employee_id: Mapped[Optional[int]] = mapped_column(ForeignKey("employees.id"))
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    parent: Mapped[Optional["OrganizationalUnit"]] = relationship("OrganizationalUnit", remote_side=[id], back_populates="children")
    children: Mapped[List["OrganizationalUnit"]] = relationship("OrganizationalUnit", back_populates="parent")
    employees: Mapped[List["Employee"]] = relationship("Employee", back_populates="org_unit", foreign_keys="Employee.org_unit_id")
    # Сотрудники, которые руководят этим подразделением
    headed_by: Mapped[Optional["Employee"]] = relationship("Employee", foreign_keys=[head_employee_id], post_update=True)


class Position(Base, TimestampMixin):
    """Справочник должностей"""
    __tablename__ = "positions"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    code: Mapped[Optional[str]] = mapped_column(String(20), unique=True)
    hierarchy_level: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    employees: Mapped[List["Employee"]] = relationship("Employee", back_populates="position")


class EmployeeProfile(Base, TimestampMixin):
    """Справочник профилей сотрудников"""
    __tablename__ = "employee_profiles"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    
    # Relationships
    employees: Mapped[List["Employee"]] = relationship("Employee", back_populates="profile")


class EmployeeType(Base, TimestampMixin):
    """Справочник типов сотрудников"""
    __tablename__ = "employee_types"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    
    # Relationships
    employees: Mapped[List["Employee"]] = relationship("Employee", back_populates="employee_type")


class TeamRole(Base, TimestampMixin):
    """Справочник ролей в командах"""
    __tablename__ = "team_roles"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    
    # Relationships  
    employees: Mapped[List["Employee"]] = relationship("Employee", back_populates="team_role")


class Tribe(Base, TimestampMixin):
    """Agile структура: Трайбы"""
    __tablename__ = "tribes"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    products: Mapped[List["Product"]] = relationship("Product", back_populates="tribe")


class Product(Base, TimestampMixin):
    """Agile структура: Продукты/Сервисы"""
    __tablename__ = "products"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    tribe_id: Mapped[int] = mapped_column(ForeignKey("tribes.id"), nullable=False)
    type: Mapped[str] = mapped_column(String(50), default="product")  # product/service
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    tribe: Mapped["Tribe"] = relationship("Tribe", back_populates="products")
    agile_teams: Mapped[List["AgileTeam"]] = relationship("AgileTeam", back_populates="product")


class AgileTeam(Base, TimestampMixin):
    """Agile структура: Команды"""
    __tablename__ = "agile_teams"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    team_type: Mapped[str] = mapped_column(String(20), nullable=False)  # Change/Run
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="agile_teams")
    employees: Mapped[List["Employee"]] = relationship("Employee", back_populates="agile_team")
