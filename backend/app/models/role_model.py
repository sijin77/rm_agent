"""
Модели ролевых моделей
"""
from typing import List, Optional
from sqlalchemy import String, Integer, Text, ForeignKey, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class RoleModel(Base, TimestampMixin):
    """Ролевые модели"""
    __tablename__ = "role_models"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    author: Mapped[str] = mapped_column(String(100), nullable=False)  # Автор модели
    version: Mapped[str] = mapped_column(String(20), default="1.0")  # Версия модели
    is_active: Mapped[bool] = mapped_column(default=True)  # Активна ли модель
    
    # Relationships
    profiles: Mapped[List["RoleProfile"]] = relationship("RoleProfile", back_populates="role_model")
    clusters: Mapped[List["Cluster"]] = relationship("Cluster", back_populates="role_model")


class RoleProfile(Base, TimestampMixin):
    """Профили ролевой модели"""
    __tablename__ = "role_profiles"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    role_model_id: Mapped[int] = mapped_column(ForeignKey("role_models.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Критерии в упрощенном JSON формате для MVP
    criteria: Mapped[dict] = mapped_column(JSON, nullable=False)
    
    # Relationships
    role_model: Mapped["RoleModel"] = relationship("RoleModel", back_populates="profiles")
    profile_accesses: Mapped[List["ProfileAccess"]] = relationship("ProfileAccess", back_populates="role_profile")
    employee_accesses: Mapped[List["EmployeeAccess"]] = relationship("EmployeeAccess", back_populates="role_profile")


class ProfileAccess(Base, TimestampMixin):
    """Доступы для профилей ролевой модели"""
    __tablename__ = "profile_accesses"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    role_profile_id: Mapped[int] = mapped_column(ForeignKey("role_profiles.id"), nullable=False)
    access_id: Mapped[int] = mapped_column(ForeignKey("accesses.id"), nullable=False)
    
    # Временные поля для удобства создания (потом уберем)
    system_name: Mapped[Optional[str]] = mapped_column(String(255))
    role_name: Mapped[Optional[str]] = mapped_column(String(200))
    
    # Relationships
    role_profile: Mapped["RoleProfile"] = relationship("RoleProfile", back_populates="profile_accesses")
    access: Mapped["Access"] = relationship("Access", back_populates="profile_accesses")
