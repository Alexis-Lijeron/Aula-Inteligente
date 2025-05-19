from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    estudiantes,
    docentes,
)

app = FastAPI(
    title="Aula Inteligente",
    description="API para gestionar estudiantes, docentes, materias, evaluaciones y predicción de rendimiento académico",
    version="1.0.0",
)

# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Routers ----------
app.include_router(estudiantes.router)
app.include_router(docentes.router)
