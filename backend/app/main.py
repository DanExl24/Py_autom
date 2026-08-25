import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import FRONTEND_DIST
from app.controllers.fichas_controller import router as fichas_router
from app.controllers.sync_controller import router as sync_router

app = FastAPI(
    title="SENA Fichas API",
    description="API modular con arquitectura MVC para gestión y visualización de formaciones SENA Caquetá",
    version="2.0.0"
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusión de Controladores / Routers
app.include_router(fichas_router)
app.include_router(sync_router)

# Servir archivos estáticos del frontend compilado si existen
if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="static")
else:
    @app.get("/")
    def index():
        return {
            "message": "Servidor API funcionando. El frontend puede desarrollarse en Vite o compilarse a frontend/dist."
        }
