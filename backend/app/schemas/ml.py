"""
Pydantic схемы для ML компонентов и агента
"""
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field


# ===== ML MODELS =====

class MLModelBase(BaseModel):
    model_type: str = Field(..., example="clustering", description="Тип модели: clustering/recommendation/classification")
    model_name: str = Field(..., example="umap_dbscan_v1", description="Название модели")
    model_metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        example={
            "algorithm": "UMAP + DBSCAN",
            "n_clusters": 6,
            "silhouette_score": 0.73,
            "features_used": ["org_unit", "position", "profile", "experience_years"]
        },
        description="Метаданные модели"
    )


class MLModelCreate(MLModelBase):
    model_data: bytes = Field(..., description="Сериализованная модель (pickle)")


class MLModelUpdate(BaseModel):
    model_metadata: Optional[Dict[str, Any]] = Field(None, description="Обновленные метаданные")


class MLModel(MLModelBase):
    id: int = Field(..., example=1)
    trained_at: datetime
    
    # Метрики качества (если есть)
    accuracy: Optional[float] = Field(None, example=0.85, description="Точность модели")
    precision: Optional[float] = Field(None, example=0.82, description="Precision")
    recall: Optional[float] = Field(None, example=0.88, description="Recall")
    f1_score: Optional[float] = Field(None, example=0.85, description="F1-score")

    class Config:
        from_attributes = True


# ===== CLUSTERS =====

class ClusterBase(BaseModel):
    role_model_id: Optional[int] = Field(None, example=1, description="ID ролевой модели")
    name: str = Field(..., example="Senior Backend разработчики", description="Название кластера")
    employee_ids: List[int] = Field(..., example=[123, 124, 125, 126], description="ID сотрудников в кластере")
    center_coordinates: Optional[List[float]] = Field(
        None,
        example=[1.2, -0.8],
        description="Координаты центра кластера в 2D пространстве"
    )
    silhouette_score: Optional[float] = Field(None, example=0.73, description="Качество кластеризации")
    clustering_method: str = Field(..., example="UMAP + DBSCAN", description="Метод кластеризации")


class ClusterCreate(ClusterBase):
    pass


class ClusterUpdate(BaseModel):
    name: Optional[str] = Field(None, example="Senior Backend разработчики v2")
    employee_ids: Optional[List[int]] = Field(None, example=[123, 124, 125])


class Cluster(ClusterBase):
    id: int = Field(..., example=1)
    created_at: datetime
    
    # Дополнительная информация
    employees_count: int = Field(..., example=4, description="Количество сотрудников")
    avg_experience_years: Optional[float] = Field(None, example=5.2, description="Средний опыт")
    common_tech_stack: Optional[List[str]] = Field(
        None,
        example=["Java", "Spring"],
        description="Общие технологии"
    )

    class Config:
        from_attributes = True


class ClusterWithEmployees(Cluster):
    """Кластер с детальной информацией о сотрудниках"""
    employees: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Детальная информация о сотрудниках"
    )


# ===== AGENT CONVERSATIONS =====

class AgentConversationBase(BaseModel):
    session_id: str = Field(..., example="session_123456", description="ID сессии диалога")
    user_message: str = Field(..., example="Создай ролевую модель для ИТ-подразделения", description="Сообщение пользователя")
    agent_response: str = Field(..., example="Анализирую ИТ-подразделение... Найдено 85 сотрудников.", description="Ответ агента")
    context_data: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        example={
            "current_step": "initialization",
            "role_model_id": 1,
            "selected_org_units": [1, 5, 12],
            "clustering_strategy": "hybrid"
        },
        description="Контекстные данные диалога"
    )


class AgentConversationCreate(AgentConversationBase):
    pass


class AgentConversation(AgentConversationBase):
    id: int = Field(..., example=1)
    timestamp: datetime

    class Config:
        from_attributes = True


class AgentSession(BaseModel):
    """Сессия диалога с агентом"""
    session_id: str = Field(..., example="session_123456")
    conversations: List[AgentConversation] = Field(default_factory=list)
    created_at: datetime
    last_activity: datetime
    context: Dict[str, Any] = Field(default_factory=dict, description="Общий контекст сессии")


# ===== FEEDBACK =====

class FeedbackBase(BaseModel):
    entity_type: str = Field(..., example="cluster", description="Тип сущности: cluster/recommendation/role_profile")
    entity_id: int = Field(..., example=1, description="ID сущности")
    feedback_type: str = Field(..., example="like", description="Тип обратной связи: like/dislike/comment")
    comment: Optional[str] = Field(None, example="Хорошая группировка, но Иванов не подходит", description="Комментарий")


class FeedbackCreate(FeedbackBase):
    pass


class Feedback(FeedbackBase):
    id: int = Field(..., example=1)
    created_at: datetime

    class Config:
        from_attributes = True


# ===== CLUSTERING REQUESTS =====

class ClusteringRequest(BaseModel):
    """Запрос на кластеризацию"""
    org_unit_ids: Optional[List[int]] = Field(None, example=[1, 5, 12], description="ID подразделений для анализа")
    strategy: str = Field(
        "hybrid",
        example="hybrid",
        description="Стратегия кластеризации: formal_attributes/access_history/hybrid"
    )
    target_clusters_count: Optional[int] = Field(None, example=6, description="Желаемое количество кластеров")
    features: Optional[List[str]] = Field(
        None,
        example=["org_unit", "position", "profile", "experience_years", "tech_stack"],
        description="Признаки для кластеризации"
    )


class ClusteringResult(BaseModel):
    """Результат кластеризации"""
    clusters: List[Cluster] = Field(default_factory=list, description="Найденные кластеры")
    quality_metrics: Dict[str, float] = Field(
        default_factory=dict,
        example={"silhouette_score": 0.73, "calinski_harabasz": 145.2},
        description="Метрики качества кластеризации"
    )
    recommendations: List[str] = Field(
        default_factory=list,
        example=[
            "Рекомендую объединить кластеры 3 и 4 - они очень похожи",
            "Кластер 1 слишком разнородный, стоит разделить"
        ],
        description="Рекомендации агента"
    )
    visualization_data: Optional[Dict[str, Any]] = Field(
        None,
        example={
            "scatter_plot": {"x": [1.2, 2.1, -0.5], "y": [-0.8, 0.5, 1.3]},
            "cluster_colors": ["#FF6B6B", "#4ECDC4", "#45B7D1"]
        },
        description="Данные для визуализации"
    )


# ===== ACCESS RECOMMENDATIONS =====

class AccessRecommendationRequest(BaseModel):
    """Запрос рекомендаций доступов"""
    cluster_id: Optional[int] = Field(None, example=1, description="ID кластера")
    role_profile_id: Optional[int] = Field(None, example=5, description="ID профиля роли")
    employee_ids: Optional[List[int]] = Field(None, example=[123, 124, 125], description="ID конкретных сотрудников")
    confidence_threshold: float = Field(0.7, example=0.7, description="Минимальный порог уверенности")


class AccessRecommendation(BaseModel):
    """Рекомендация доступа"""
    access_id: int = Field(..., example=1)
    access_name: str = Field(..., example="GitLab Developer")
    system_name: str = Field(..., example="GitLab")
    confidence: float = Field(..., example=0.85, description="Уверенность рекомендации")
    explanation: str = Field(
        ...,
        example="11 из 12 сотрудников кластера активно используют этот доступ",
        description="Объяснение рекомендации"
    )
    current_coverage: float = Field(..., example=0.92, description="Текущий охват (доля имеющих доступ)")
    usage_pattern: Optional[str] = Field(None, example="daily", description="Паттерн использования")


class AccessRecommendationResult(BaseModel):
    """Результат рекомендаций доступов"""
    high_confidence: List[AccessRecommendation] = Field(default_factory=list, description="Высокая уверенность (>80%)")
    medium_confidence: List[AccessRecommendation] = Field(default_factory=list, description="Средняя уверенность (60-80%)")
    low_confidence: List[AccessRecommendation] = Field(default_factory=list, description="Низкая уверенность (<60%)")
    
    warnings: List[str] = Field(
        default_factory=list,
        example=["Доступ 'Admin права' имеет высокую критичность - требует дополнительного согласования"],
        description="Предупреждения"
    )


# ===== CONFLICT DETECTION =====

class ConflictDetectionRequest(BaseModel):
    """Запрос на детекцию конфликтов"""
    employee_id: Optional[int] = Field(None, example=123, description="ID сотрудника")
    role_profile_id: Optional[int] = Field(None, example=5, description="ID профиля роли")
    access_ids: List[int] = Field(..., example=[1, 2, 3], description="ID доступов для проверки")


class ConflictDetection(BaseModel):
    """Обнаруженный конфликт"""
    conflict_type: str = Field(..., example="privilege_escalation_risk", description="Тип конфликта")
    severity: str = Field(..., example="high", description="Серьезность: low/medium/high/critical")
    conflicting_accesses: List[int] = Field(..., example=[1, 2], description="Конфликтующие доступы")
    explanation: str = Field(
        ...,
        example="Комбинация просмотра продакшн-подов и возможности деплоя создает риск",
        description="Объяснение конфликта"
    )
    affected_systems: List[str] = Field(..., example=["Kubernetes", "GitLab"], description="Затронутые системы")
    risk_scenario: str = Field(
        ...,
        example="Возможность случайного воздействия на продакшн через CI/CD",
        description="Сценарий риска"
    )
    recommendations: List[str] = Field(
        default_factory=list,
        example=["Ограничить CI/CD права", "Убрать прямой доступ к K8s Prod"],
        description="Рекомендации по устранению"
    )


class ConflictDetectionResult(BaseModel):
    """Результат детекции конфликтов"""
    has_conflicts: bool = Field(..., example=True, description="Есть ли конфликты")
    conflict_probability: float = Field(..., example=0.87, description="Вероятность конфликта")
    detected_conflicts: List[ConflictDetection] = Field(default_factory=list, description="Обнаруженные конфликты")
    
    explanation_features: List[Dict[str, float]] = Field(
        default_factory=list,
        example=[
            {"feature": "prod_environment", "importance": 0.4},
            {"feature": "deploy_permissions", "importance": 0.3}
        ],
        description="Важность признаков для решения"
    )
