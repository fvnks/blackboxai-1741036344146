from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .database import MongoDB
from .routers import auth
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de CORS
origins = os.getenv("BACKEND_CORS_ORIGINS", "").split(",")
if not origins:
    origins = [
        "http://localhost:3000",  # Frontend Next.js
        "http://localhost:8000",  # Backend FastAPI
    ]

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Código que se ejecuta al iniciar la aplicación
    await MongoDB.connect_to_database()
    yield
    # Código que se ejecuta al cerrar la aplicación
    await MongoDB.close_database_connection()

# Crear instancia de FastAPI
app = FastAPI(
    title=os.getenv("PROJECT_NAME", "Sistema de Gestión de Condominios"),
    description="API para el sistema de gestión de condominios",
    version="1.0.0",
    lifespan=lifespan
)

# Agregar middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth.router)

@app.get("/")
async def root():
    return {
        "mensaje": "Bienvenido al API del Sistema de Gestión de Condominios",
        "documentacion": "/docs",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    try:
        # Verificar conexión a MongoDB
        db = await MongoDB.db.command("ping")
        return {
            "status": "healthy",
            "database": "connected",
            "message": "El servicio está funcionando correctamente"
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"El servicio no está disponible: {str(e)}"
        )
