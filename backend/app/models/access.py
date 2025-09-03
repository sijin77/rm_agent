"""
Модели системы доступов
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class ApplicationSystem(Base, TimestampMixin):
    """Справочник прикладных систем (АС)"""
    __tablename__ = "application_systems"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    criticality: Mapped[str] = mapped_column(String(20), nullable=False)  # low/medium/high/critical
    system_type: Mapped[str] = mapped_column(String(20), nullable=False)  # IT/Business
    
    # Relationships
    accesses: Mapped[List["Access"]] = relationship("Access", back_populates="system")


class Access(Base, TimestampMixin):
    """Доступы в системах"""
    __tablename__ = "accesses"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    system_id: Mapped[int] = mapped_column(ForeignKey("application_systems.id"), nullable=False)
    role_name: Mapped[str] = mapped_column(String(200), nullable=False)
    criticality: Mapped[str] = mapped_column(String(20), nullable=False)
    
    # Relationships
    system: Mapped["ApplicationSystem"] = relationship("ApplicationSystem", back_populates="accesses")
    employee_accesses: Mapped[List["EmployeeAccess"]] = relationship("EmployeeAccess", back_populates="access")
    profile_accesses: Mapped[List["ProfileAccess"]] = relationship("ProfileAccess", back_populates="access")


class EmployeeAccess(Base):
    """Назначенные доступы сотрудникам"""
    __tablename__ = "employee_accesses"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False)
    access_id: Mapped[int] = mapped_column(ForeignKey("accesses.id"), nullable=False)
    assignment_type: Mapped[str] = mapped_column(String(20), nullable=False)  # auto_role/manual_request
    role_profile_id: Mapped[Optional[int]] = mapped_column(ForeignKey("role_profiles.id"))
    
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_used: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Relationships
    employee: Mapped["Employee"] = relationship("Employee", back_populates="employee_accesses")
    access: Mapped["Access"] = relationship("Access", back_populates="employee_accesses")
    role_profile: Mapped[Optional["RoleProfile"]] = relationship("RoleProfile", back_populates="employee_accesses")
