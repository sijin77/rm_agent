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
        result = await db.execute(select(RoleModel))
        role_models = result.scalars().all()
        
        # TODO: Добавить подсчет сотрудников для каждого профиля
        # TODO: Добавить статистику по каждой модели
        
        logger.success(f"Загружено {len(role_models)} ролевых моделей")
        
        return templates.TemplateResponse("role_models/list.html", {
            "request": request,
            "role_models": role_models,
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
        
        # TODO: Добавить подсчет сотрудников для каждого профиля
        # TODO: Добавить статистику по доступам
        
        logger.success(f"Загружена ролевая модель: {role_model.name}")
        
        return templates.TemplateResponse("role_models/detail.html", {
            "request": request,
            "role_model": role_model,
            "profiles": profiles,
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
        
        logger.success(f"Открыто редактирование ролевой модели: {role_model.name}")
        
        return templates.TemplateResponse("role_models/edit.html", {
            "request": request,
            "role_model": role_model,
            "profiles": profiles,
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
        
        # TODO: Получить список сотрудников, соответствующих критериям профиля
        # TODO: Реализовать фильтрацию по критериям
        employees = []  # Заглушка
        
        logger.success(f"Загружены сотрудники для профиля: {profile.name}")
        
        return templates.TemplateResponse("profiles/employees.html", {
            "request": request,
            "role_model": role_model,
            "profile": profile,
            "employees": employees,
            "page_title": f"Сотрудники профиля: {profile.name}"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка загрузки сотрудников профиля {profile_id}: {e}")
        raise HTTPException(status_code=500, detail="Ошибка загрузки данных")