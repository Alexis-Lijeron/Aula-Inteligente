from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import SessionLocal
from app.auth.roles import docente_o_admin_required
from app.models import Evaluacion, RendimientoFinal, Inscripcion, Periodo

router = APIRouter(prefix="/resumen", tags=["Resumen Dashboard"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/materia/completo")
def resumen_materia_completo(
    curso_id: int,
    materia_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(docente_o_admin_required),
):
    # Obtener IDs de estudiantes en el curso
    inscripciones = db.query(Inscripcion).filter_by(curso_id=curso_id).all()
    estudiante_ids = [i.estudiante_id for i in inscripciones]
    if not estudiante_ids:
        raise HTTPException(status_code=404, detail="No hay estudiantes en este curso.")

    # Obtener periodos que tienen al menos una evaluación registrada
    periodos_con_datos = (
        db.query(Evaluacion.periodo_id)
        .filter(
            Evaluacion.materia_id == materia_id,
            Evaluacion.estudiante_id.in_(estudiante_ids),
        )
        .distinct()
        .all()
    )
    periodos_ids = [p[0] for p in periodos_con_datos]
    if not periodos_ids:
        raise HTTPException(status_code=404, detail="No hay evaluaciones registradas.")

    resumen_por_periodo = []

    for pid in periodos_ids:
        # Notas finales (rendimiento)
        rendimientos = (
            db.query(RendimientoFinal)
            .filter(
                RendimientoFinal.estudiante_id.in_(estudiante_ids),
                RendimientoFinal.materia_id == materia_id,
                RendimientoFinal.periodo_id == pid,
            )
            .all()
        )
        promedio_notas = (
            sum(r.nota_final for r in rendimientos) / len(rendimientos)
            if rendimientos
            else 0
        )

        # Asistencia
        asistencias = (
            db.query(Evaluacion)
            .filter(
                Evaluacion.estudiante_id.in_(estudiante_ids),
                Evaluacion.materia_id == materia_id,
                Evaluacion.periodo_id == pid,
                Evaluacion.tipo_evaluacion_id == 5,
            )
            .all()
        )
        promedio_asistencia = (
            sum(e.valor for e in asistencias) / len(asistencias) if asistencias else 0
        )

        # Participación
        participaciones = (
            db.query(Evaluacion)
            .filter(
                Evaluacion.estudiante_id.in_(estudiante_ids),
                Evaluacion.materia_id == materia_id,
                Evaluacion.periodo_id == pid,
                Evaluacion.tipo_evaluacion_id == 4,
            )
            .all()
        )
        promedio_participacion = (
            sum(e.valor for e in participaciones) / len(participaciones)
            if participaciones
            else 0
        )

        resumen_por_periodo.append(
            {
                "periodo_id": pid,
                "promedio_notas": round(promedio_notas, 2),
                "promedio_asistencia": round(promedio_asistencia, 2),
                "promedio_participacion": round(promedio_participacion, 2),
            }
        )

    # Promedios generales
    n = len(resumen_por_periodo)
    promedio_general = {
        "notas": round(sum(r["promedio_notas"] for r in resumen_por_periodo) / n, 2),
        "asistencia": round(
            sum(r["promedio_asistencia"] for r in resumen_por_periodo) / n, 2
        ),
        "participacion": round(
            sum(r["promedio_participacion"] for r in resumen_por_periodo) / n, 2
        ),
    }

    return {
        "total_estudiantes": len(estudiante_ids),
        "resumen_por_periodo": resumen_por_periodo,
        "promedio_general": promedio_general,
    }
