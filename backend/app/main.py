"""
Главный модуль FastAPI приложения
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from app.core.config import settings
from app.core.database import create_tables
from app.api import organization, employee, access, role_model
from app.views import role_models, ai_tools, chat

# Создание FastAPI приложения
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="ИИ-агент для проектирования ролевых моделей",
    openapi_tags=[
        {
            "name": "organization",
            "description": "Операции с организационной структурой"
        },
        {
            "name": "employees", 
            "description": "Управление сотрудниками"
        },
        {
            "name": "access",
            "description": "Система доступов"
        },
        {
            "name": "role-models",
            "description": "Ролевые модели и профили"
        }
    ]
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Статические файлы
app.mount("/static", StaticFiles(directory="static"), name="static")

# Подключение роутеров
app.include_router(
    organization.router,
    prefix="/api/v1/organization",
    tags=["organization"]
)

app.include_router(
    employee.router,
    prefix="/api/v1/employees", 
    tags=["employees"]
)

app.include_router(
    access.router,
    prefix="/api/v1/access",
    tags=["access"]
)

app.include_router(
    role_model.router,
    prefix="/api/v1/role-models",
    tags=["role-models"]
)

# Подключение view роутеров
app.include_router(
    role_models.router,
    prefix="/role-models",
    tags=["views"]
)

app.include_router(
    ai_tools.router,
    prefix="/api/v1/ai-tools",
    tags=["ai-tools"]
)

app.include_router(
    chat.router,
    prefix="/api/v1/chat",
    tags=["chat"]
)


@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске"""
    # Создание таблиц БД
    await create_tables()
    print(f"🚀 {settings.PROJECT_NAME} запущен!")
    print(f"📖 Документация: http://localhost:8000/docs")
    print(f"🗄️ База данных: {settings.DATABASE_URL}")


@app.get("/")
async def root():
    """Корневой эндпоинт - перенаправление на главную страницу"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/role-models/")

@app.get("/test", response_class=HTMLResponse)
async def test_page(request: Request):
    """Тестовая страница без базы данных"""
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="backend/templates")
    return templates.TemplateResponse("role_models/list.html", {
        "request": request,
        "role_models": [],  # Пустой список для теста
        "page_title": "Тестовая страница"
    })


@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
