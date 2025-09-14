"""
Views для ролевых моделей
"""
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.api.deps import get_db
from app.models.role_model import RoleModel, RoleProfile
from app.utils.logger import logger

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def list_role_models(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Главная страница - список ролевых моделей
    """
    try:
        # Получаем все ролевые модели с профилями
        from sqlalchemy.orm import selectinload
        result = await db.execute(select(RoleModel).options(selectinload(RoleModel.profiles)))
        role_models = result.scalars().all()
        
        # Конвертируем в обычные объекты для Jinja2
        role_models_data = []
        for rm in role_models:
            # Подсчитываем количество профилей
            profiles_count = len(rm.profiles) if rm.profiles else 0
            
            # Подсчитываем количество уникальных систем доступа
            access_systems = set()
            try:
                for profile in rm.profiles:
                    if hasattr(profile, 'profile_accesses') and profile.profile_accesses:
                        for access in profile.profile_accesses:
                            if hasattr(access, 'system_name') and access.system_name:
                                access_systems.add(access.system_name)
            except Exception as e:
                logger.warning(f"Ошибка при подсчете систем доступа для модели {rm.id}: {e}")
                access_systems = set()
            
            role_models_data.append({
                "id": rm.id,
                "name": rm.name,
                "description": rm.description,
                "created_at": rm.created_at,
                "updated_at": rm.updated_at,
                "profiles": rm.profiles,
                "access_systems": list(access_systems)
            })
        
        logger.success(f"Загружено {len(role_models_data)} ролевых моделей")
        
        return templates.TemplateResponse("role_models/list.html", {
            "request": request,
            "role_models": role_models_data,
            "page_title": "Ролевые модели"
        })
        
    except Exception as e:
        logger.error(f"Ошибка загрузки ролевых моделей: {e}")
        raise HTTPException(status_code=500, detail="Ошибка загрузки данных")


@router.get("/{role_model_id}", response_class=HTMLResponse)
async def view_role_model(
    role_model_id: int, 
    request: Request, 
    db: AsyncSession = Depends(get_db)
):
    """
    Детальный просмотр ролевой модели
    """
    try:
        # Получаем ролевую модель с профилями
        result = await db.execute(select(RoleModel).where(RoleModel.id == role_model_id))
        role_model = result.scalar_one_or_none()
        
        if not role_model:
            raise HTTPException(status_code=404, detail="Ролевая модель не найдена")
        
        # Получаем профили для этой модели
        result = await db.execute(select(RoleProfile).where(RoleProfile.role_model_id == role_model_id))
        profiles = result.scalars().all()
        
        # Конвертируем в обычные объекты для Jinja2
        role_model_data = {
            "id": role_model.id,
            "name": role_model.name,
            "description": role_model.description,
            "created_at": role_model.created_at,
            "updated_at": role_model.updated_at
        }
        
        profiles_data = []
        for profile in profiles:
            profiles_data.append({
                "id": profile.id,
                "name": profile.name,
                "description": profile.description,
                "criteria": profile.criteria,
                "created_at": profile.created_at,
                "updated_at": profile.updated_at
            })
        
        # TODO: Добавить подсчет сотрудников для каждого профиля
        # TODO: Добавить статистику по доступам
        
        logger.success(f"Загружена ролевая модель: {role_model.name}")
        
        return templates.TemplateResponse("role_models/detail.html", {
            "request": request,
            "role_model": role_model_data,
            "profiles": profiles_data,
            "page_title": f"Ролевая модель: {role_model.name}"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка загрузки ролевой модели {role_model_id}: {e}")
        raise HTTPException(status_code=500, detail="Ошибка загрузки данных")


@router.get("/{role_model_id}/edit", response_class=HTMLResponse)
async def edit_role_model(
    role_model_id: int, 
    request: Request, 
    db: AsyncSession = Depends(get_db)
):
    """
    Редактирование ролевой модели
    """
    try:
        # Получаем ролевую модель с профилями
        result = await db.execute(select(RoleModel).where(RoleModel.id == role_model_id))
        role_model = result.scalar_one_or_none()
        
        if not role_model:
            raise HTTPException(status_code=404, detail="Ролевая модель не найдена")
        
        # Получаем профили для этой модели
        result = await db.execute(select(RoleProfile).where(RoleProfile.role_model_id == role_model_id))
        profiles = result.scalars().all()
        
        # Конвертируем в обычные объекты для Jinja2
        role_model_data = {
            "id": role_model.id,
            "name": role_model.name,
            "description": role_model.description,
            "created_at": role_model.created_at,
            "updated_at": role_model.updated_at
        }
        
        profiles_data = []
        for profile in profiles:
            profiles_data.append({
                "id": profile.id,
                "name": profile.name,
                "description": profile.description,
                "criteria": profile.criteria,
                "created_at": profile.created_at,
                "updated_at": profile.updated_at
            })
        
        logger.success(f"Открыто редактирование ролевой модели: {role_model.name}")
        
        return templates.TemplateResponse("role_models/edit.html", {
            "request": request,
            "role_model": role_model_data,
            "profiles": profiles_data,
            "page_title": f"Редактирование: {role_model.name}"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка загрузки ролевой модели для редактирования {role_model_id}: {e}")
        raise HTTPException(status_code=500, detail="Ошибка загрузки данных")


@router.get("/{role_model_id}/profiles/{profile_id}/employees", response_class=HTMLResponse)
async def view_profile_employees(
    role_model_id: int,
    profile_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Просмотр сотрудников, соответствующих профилю
    """
    try:
        # Получаем ролевую модель
        result = await db.execute(select(RoleModel).where(RoleModel.id == role_model_id))
        role_model = result.scalar_one_or_none()
        
        if not role_model:
            raise HTTPException(status_code=404, detail="Ролевая модель не найдена")
        
        # Получаем профиль
        result = await db.execute(select(RoleProfile).where(
            RoleProfile.id == profile_id,
            RoleProfile.role_model_id == role_model_id
        ))
        profile = result.scalar_one_or_none()
        
        if not profile:
            raise HTTPException(status_code=404, detail="Профиль не найден")
        
        # Конвертируем в обычные объекты для Jinja2
        role_model_data = {
            "id": role_model.id,
            "name": role_model.name,
            "description": role_model.description,
            "created_at": role_model.created_at,
            "updated_at": role_model.updated_at
        }
        
        profile_data = {
            "id": profile.id,
            "name": profile.name,
            "description": profile.description,
            "criteria": profile.criteria,
            "created_at": profile.created_at,
            "updated_at": profile.updated_at
        }
        
        # TODO: Получить список сотрудников, соответствующих критериям профиля
        # TODO: Реализовать фильтрацию по критериям
        employees = []  # Заглушка
        
        logger.success(f"Загружены сотрудники для профиля: {profile.name}")
        
        return templates.TemplateResponse("profiles/employees.html", {
            "request": request,
            "role_model": role_model_data,
            "profile": profile_data,
            "employees": employees,
            "page_title": f"Сотрудники профиля: {profile.name}"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка загрузки сотрудников профиля {profile_id}: {e}")
        raise HTTPException(status_code=500, detail="Ошибка загрузки данных")