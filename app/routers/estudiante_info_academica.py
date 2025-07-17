# app/routers/estudiante_info_academica.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.schemas.estudiante_info_academica import (
    InfoAcademicaResponse,
    InfoAcademicaCompleta,
    CursoEstudianteResponse,
    MateriasEstudianteResponse,
    DocentesEstudianteResponse,
    InfoAcademicaResumen,
    CursoBasico,
    MateriaConDocente,
    DocenteConMaterias,
)
from app.crud import estudiante_info_academica as crud
from app.auth.roles import usuario_autenticado, estudiante_required
from typing import Optional

router = APIRouter(
    prefix="/estudiante/mi-info-academica", tags=["Información Académica Estudiante"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def obtener_estudiante_actual(payload: dict, db: Session):
    """Helper para obtener el estudiante autenticado"""
    user_id = payload.get("user_id")
    user_type = payload.get("user_type")

    if not user_id or user_type != "estudiante":
        raise HTTPException(status_code=403, detail="Solo estudiantes pueden acceder")

    estudiante = crud.obtener_estudiante_por_id(db, user_id)
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    return estudiante


@router.get("/completa", response_model=InfoAcademicaResponse)
def obtener_info_academica_completa(
    gestion_id: Optional[int] = Query(
        None,
        description="ID de la gestión (opcional, usa la gestión activa por defecto)",
    ),
    payload: dict = Depends(estudiante_required),
    db: Session = Depends(get_db),
):
    """
    📚 Obtener toda la información académica del estudiante autenticado:
    - Su curso actual
    - Las materias del curso
    - Los docentes de cada materia
    """
    estudiante = obtener_estudiante_actual(payload, db)

    info_academica = crud.obtener_info_academica_estudiante(
        db, estudiante.id, gestion_id
    )

    # Verificar si hay error en la respuesta
    if "error" in info_academica:
        return InfoAcademicaResponse(success=False, mensaje=info_academica["error"])

    # Convertir a modelo Pydantic
    data = InfoAcademicaCompleta(**info_academica)

    return InfoAcademicaResponse(
        success=True,
        data=data,
        mensaje=f"Información académica obtenida exitosamente para la gestión {info_academica['gestion']['anio']}",
    )


@router.get("/curso", response_model=CursoEstudianteResponse)
def obtener_mi_curso(
    gestion_id: Optional[int] = Query(None, description="ID de la gestión (opcional)"),
    payload: dict = Depends(estudiante_required),
    db: Session = Depends(get_db),
):
    """
    🏫 Obtener el curso actual del estudiante autenticado
    """
    estudiante = obtener_estudiante_actual(payload, db)

    curso = crud.obtener_curso_estudiante(db, estudiante.id, gestion_id)

    if not curso:
        return CursoEstudianteResponse(
            success=False, mensaje="No tienes curso asignado en esta gestión"
        )

    return CursoEstudianteResponse(
        success=True, curso=CursoBasico(**curso), mensaje="Curso obtenido exitosamente"
    )


@router.get("/materias", response_model=MateriasEstudianteResponse)
def obtener_mis_materias(
    gestion_id: Optional[int] = Query(None, description="ID de la gestión (opcional)"),
    payload: dict = Depends(estudiante_required),
    db: Session = Depends(get_db),
):
    """
    📖 Obtener las materias del estudiante autenticado con sus docentes
    """
    estudiante = obtener_estudiante_actual(payload, db)

    materias = crud.obtener_materias_estudiante(db, estudiante.id, gestion_id)

    if not materias:
        return MateriasEstudianteResponse(
            success=False,
            mensaje="No tienes materias asignadas en esta gestión",
            total=0,
        )

    # Convertir a modelos Pydantic
    materias_response = [MateriaConDocente(**materia) for materia in materias]

    return MateriasEstudianteResponse(
        success=True,
        materias=materias_response,
        total=len(materias_response),
        mensaje=f"Se encontraron {len(materias_response)} materias",
    )


@router.get("/docentes", response_model=DocentesEstudianteResponse)
def obtener_mis_docentes(
    gestion_id: Optional[int] = Query(None, description="ID de la gestión (opcional)"),
    payload: dict = Depends(estudiante_required),
    db: Session = Depends(get_db),
):
    """
    👨‍🏫 Obtener todos los docentes que enseñan al estudiante autenticado
    """
    estudiante = obtener_estudiante_actual(payload, db)

    docentes = crud.obtener_docentes_estudiante(db, estudiante.id, gestion_id)

    if not docentes:
        return DocentesEstudianteResponse(
            success=False,
            mensaje="No tienes docentes asignados en esta gestión",
            total=0,
        )

    # Convertir a modelos Pydantic
    docentes_response = [DocenteConMaterias(**docente) for docente in docentes]

    return DocentesEstudianteResponse(
        success=True,
        docentes=docentes_response,
        total=len(docentes_response),
        mensaje=f"Se encontraron {len(docentes_response)} docentes",
    )


@router.get("/resumen", response_model=dict)
def obtener_resumen_academico(
    gestion_id: Optional[int] = Query(None, description="ID de la gestión (opcional)"),
    payload: dict = Depends(estudiante_required),
    db: Session = Depends(get_db),
):
    """
    📊 Obtener un resumen de la información académica del estudiante
    """
    estudiante = obtener_estudiante_actual(payload, db)

    info_academica = crud.obtener_info_academica_estudiante(
        db, estudiante.id, gestion_id
    )

    if "error" in info_academica:
        return {"success": False, "mensaje": info_academica["error"]}

    # Crear resumen
    materias_con_docente = sum(
        1 for m in info_academica["materias"] if m["docente"] is not None
    )
    materias_sin_docente = len(info_academica["materias"]) - materias_con_docente

    resumen = {
        "success": True,
        "estudiante": info_academica["estudiante"],
        "curso": info_academica["curso"],
        "gestion": info_academica["gestion"],
        "estadisticas": {
            "total_materias": len(info_academica["materias"]),
            "materias_con_docente": materias_con_docente,
            "materias_sin_docente": materias_sin_docente,
            "total_docentes": len(
                set(
                    m["docente"]["id"]
                    for m in info_academica["materias"]
                    if m["docente"] is not None
                )
            ),
        },
        "mensaje": f"Resumen académico para la gestión {info_academica['gestion']['anio']}",
    }

    return resumen


# ================ ENDPOINTS ADICIONALES PARA FUNCIONALIDADES ESPECÍFICAS ================


@router.get("/materia/{materia_id}/docente", response_model=dict)
def obtener_docente_de_materia(
    materia_id: int,
    gestion_id: Optional[int] = Query(None, description="ID de la gestión (opcional)"),
    payload: dict = Depends(estudiante_required),
    db: Session = Depends(get_db),
):
    """
    👨‍🏫 Obtener el docente de una materia específica del estudiante
    """
    estudiante = obtener_estudiante_actual(payload, db)

    materias = crud.obtener_materias_estudiante(db, estudiante.id, gestion_id)

    # Buscar la materia específica
    materia_encontrada = None
    for materia in materias:
        if materia["materia"]["id"] == materia_id:
            materia_encontrada = materia
            break

    if not materia_encontrada:
        return {
            "success": False,
            "mensaje": "No estás inscrito en esta materia o la materia no existe",
        }

    if not materia_encontrada["docente"]:
        return {"success": False, "mensaje": "Esta materia no tiene docente asignado"}

    return {
        "success": True,
        "materia": materia_encontrada["materia"],
        "docente": materia_encontrada["docente"],
        "mensaje": "Docente encontrado exitosamente",
    }


@router.get("/verificar-inscripcion", response_model=dict)
def verificar_inscripcion_activa(
    payload: dict = Depends(estudiante_required), db: Session = Depends(get_db)
):
    """
    ✅ Verificar si el estudiante tiene una inscripción activa
    """
    estudiante = obtener_estudiante_actual(payload, db)

    curso = crud.obtener_curso_estudiante(db, estudiante.id)

    if curso:
        return {
            "success": True,
            "inscrito": True,
            "curso": curso,
            "mensaje": "Tienes inscripción activa",
        }
    else:
        return {
            "success": True,
            "inscrito": False,
            "mensaje": "No tienes inscripción activa en la gestión actual",
        }
