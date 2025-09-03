"""
Модели для ML компонентов и агента
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import String, Integer, Text, ForeignKey, JSON, LargeBinary, Float, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class MLModel(Base):
    """Обученные ML модели"""
    __tablename__ = "ml_models"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    model_type: Mapped[str] = mapped_column(String(50), nullable=False)  # clustering/recommendation/classification
    model_name: Mapped[str] = mapped_column(String(200), nullable=False)
    model_data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)  # Pickle данные
    model_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    
    # Метрики качества
    accuracy: Mapped[Optional[float]] = mapped_column(Float)
    precision: Mapped[Optional[float]] = mapped_column(Float)
    recall: Mapped[Optional[float]] = mapped_column(Float)
    f1_score: Mapped[Optional[float]] = mapped_column(Float)
    
    trained_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Cluster(Base, TimestampMixin):
    """Результаты кластеризации"""
    __tablename__ = "clusters"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    role_model_id: Mapped[Optional[int]] = mapped_column(ForeignKey("role_models.id"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    employee_ids: Mapped[List[int]] = mapped_column(JSON, nullable=False)
    center_coordinates: Mapped[Optional[List[float]]] = mapped_column(JSON)
    silhouette_score: Mapped[Optional[float]] = mapped_column(Float)
    clustering_method: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Relationships
    role_model: Mapped[Optional["RoleModel"]] = relationship("RoleModel", back_populates="clusters")


class AgentConversation(Base):
    """Диалоги с агентом"""
    __tablename__ = "agent_conversations"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[str] = mapped_column(String(100), nullable=False)
    user_message: Mapped[str] = mapped_column(Text, nullable=False)
    agent_response: Mapped[str] = mapped_column(Text, nullable=False)
    context_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Feedback(Base, TimestampMixin):
    """Обратная связь для ML моделей"""
    __tablename__ = "feedback"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)  # cluster/recommendation/role_profile
    entity_id: Mapped[int] = mapped_column(Integer, nullable=False)
    feedback_type: Mapped[str] = mapped_column(String(20), nullable=False)  # like/dislike/comment
    comment: Mapped[Optional[str]] = mapped_column(Text)
