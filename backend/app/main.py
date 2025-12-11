# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager


try:
    from backend.app.config import settings
except ModuleNotFoundError:
    from app.config import settings
# Routers
try:
    from backend.app.config.database import engine, Base
except ModuleNotFoundError:
    from app.config.database import engine, Base
try:
    from backend.app.routes.hukdis_routes import router as hukdis_router
except ModuleNotFoundError:
    from app.routes.hukdis_routes import router as hukdis_router
try:
    from backend.app.routes.sql_routes import router as sql_router
except ModuleNotFoundError:
    from app.routes.sql_routes import router as sql_router
try:
    from backend.app.routes.manage_routes import router as manage_router
except ModuleNotFoundError:
    from app.routes.manage_routes import router as manage_router
try:
    from backend.app.routes.history_routes import router as history_router
except ModuleNotFoundError:
    from app.routes.history_routes import router as history_router
try:
    from backend.app.routes.restore_routes import router as restore_router
except ModuleNotFoundError:
    from app.routes.restore_routes import router as restore_router
try:
    from backend.app.routes.system_routes import router as system_router
except ModuleNotFoundError:
    from app.routes.system_routes import router as system_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[INIT] Creating tables if not exist...")
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="Monitoring Hukdis API",
    version="1.0.0",
    description="Backend API for Monitoring Hukuman Disiplin",
    lifespan=lifespan
)

# CORS (Streamlit compatibility)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(hukdis_router)
app.include_router(sql_router)
app.include_router(manage_router)
app.include_router(history_router)
app.include_router(restore_router)
app.include_router(system_router)


@app.get("/")
def root():
    return {
        "message": "Monitoring Hukdis API is running",
        "routes": [
            "/hukdis/*",
            "/sql/*",
            "/manage/*",
            "/history/*",
            "/hukdis/backup",
            "/hukdis/restore",
        ],
    }