from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    estudiantes,
    docentes,
    materias,
    docente_materia,
    cursos,
    curso_materia,
    gestiones,
    inscripciones,
    periodos,
    evaluaciones,
    tipo_evaluacion,
    peso_tipo_evaluacion,
    rendimiento_final,
    resumen,
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
app.include_router(materias.router)
app.include_router(docente_materia.router)
app.include_router(cursos.router)
app.include_router(curso_materia.router)
app.include_router(gestiones.router)
app.include_router(inscripciones.router)
app.include_router(periodos.router)
app.include_router(evaluaciones.router)
app.include_router(tipo_evaluacion.router)
app.include_router(peso_tipo_evaluacion.router)
app.include_router(rendimiento_final.router)
app.include_router(resumen.router)
