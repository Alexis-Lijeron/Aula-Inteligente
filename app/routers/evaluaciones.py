from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.estudiante import Estudiante
from app.models.evaluacion import Evaluacion
from app.models.inscripcion import Inscripcion
from app.models.periodo import Periodo
from app.schemas.evaluacion import EvaluacionCreate, EvaluacionUpdate, EvaluacionOut
from app.crud import evaluacion as crud
from app.auth.roles import docente_o_admin_required
from app.models.tipo_evaluacion import TipoEvaluacion

router = APIRouter(prefix="/evaluaciones", tags=["Evaluaciones"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=EvaluacionOut)
def crear(
    datos: EvaluacionCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(docente_o_admin_required),
):
    return crud.crear_evaluacion(db, datos)


@router.get("/", response_model=list[EvaluacionOut])
def listar(
    db: Session = Depends(get_db), payload: dict = Depends(docente_o_admin_required)
):
    return crud.listar_evaluaciones(db)


@router.get("/{evaluacion_id}", response_model=EvaluacionOut)
def obtener(
    evaluacion_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(docente_o_admin_required),
):
    e = crud.obtener_por_id(db, evaluacion_id)
    if not e:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada")
    return e


@router.put("/{evaluacion_id}", response_model=EvaluacionOut)
def actualizar(
    evaluacion_id: int,
    datos: EvaluacionUpdate,
    db: Session = Depends(get_db),
    payload: dict = Depends(docente_o_admin_required),
):
    e = crud.actualizar_evaluacion(db, evaluacion_id, datos)
    if not e:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada")
    return e


@router.delete("/{evaluacion_id}")
def eliminar(
    evaluacion_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(docente_o_admin_required),
):
    e = crud.eliminar_evaluacion(db, evaluacion_id)
    if not e:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada")
    return {"mensaje": "Evaluación eliminada"}


def obtener_id_tipo(db: Session, nombre_tipo: str) -> int:
    tipo = (
        db.query(TipoEvaluacion)
        .filter(TipoEvaluacion.nombre.ilike(nombre_tipo))
        .first()
    )
    if not tipo:
        raise HTTPException(
            status_code=404, detail=f"Tipo de evaluación '{nombre_tipo}' no encontrado"
        )
    return tipo.id


@router.post("/registrar/examen", response_model=EvaluacionOut)
def registrar_examen(
    datos: EvaluacionCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(docente_o_admin_required),
):
    datos.tipo_evaluacion_id = obtener_id_tipo(db, "Exámenes")
    return crud.crear_evaluacion(db, datos)


@router.post("/registrar/tarea", response_model=EvaluacionOut)
def registrar_tarea(
    datos: EvaluacionCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(docente_o_admin_required),
):
    datos.tipo_evaluacion_id = obtener_id_tipo(db, "Tareas")
    return crud.crear_evaluacion(db, datos)


@router.post("/registrar/exposicion", response_model=EvaluacionOut)
def registrar_exposicion(
    datos: EvaluacionCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(docente_o_admin_required),
):
    datos.tipo_evaluacion_id = obtener_id_tipo(db, "Exposiciones")
    return crud.crear_evaluacion(db, datos)


@router.post("/registrar/participacion", response_model=EvaluacionOut)
def registrar_participacion(
    datos: EvaluacionCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(docente_o_admin_required),
):
    datos.tipo_evaluacion_id = obtener_id_tipo(db, "Participaciones")
    return crud.crear_evaluacion(db, datos)


@router.post("/registrar/asistencia", response_model=EvaluacionOut)
def registrar_asistencia(
    datos: EvaluacionCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(docente_o_admin_required),
):
    datos.tipo_evaluacion_id = obtener_id_tipo(db, "Asistencia")
    return crud.crear_evaluacion(db, datos)


@router.post("/registrar/practica", response_model=EvaluacionOut)
def registrar_practica(
    datos: EvaluacionCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(docente_o_admin_required),
):
    datos.tipo_evaluacion_id = obtener_id_tipo(db, "Prácticas")
    return crud.crear_evaluacion(db, datos)


@router.post("/registrar/proyecto", response_model=EvaluacionOut)
def registrar_proyecto_final(
    datos: EvaluacionCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(docente_o_admin_required),
):
    datos.tipo_evaluacion_id = obtener_id_tipo(db, "Proyecto final")
    return crud.crear_evaluacion(db, datos)


@router.post("/registrar/grupal", response_model=EvaluacionOut)
def registrar_trabajo_grupal(
    datos: EvaluacionCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(docente_o_admin_required),
):
    datos.tipo_evaluacion_id = obtener_id_tipo(db, "Trabajo grupal")
    return crud.crear_evaluacion(db, datos)


@router.post("/registrar/ensayo", response_model=EvaluacionOut)
def registrar_ensayo(
    datos: EvaluacionCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(docente_o_admin_required),
):
    datos.tipo_evaluacion_id = obtener_id_tipo(db, "Ensayos")
    return crud.crear_evaluacion(db, datos)


@router.post("/registrar/cuestionario", response_model=EvaluacionOut)
def registrar_cuestionario(
    datos: EvaluacionCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(docente_o_admin_required),
):
    datos.tipo_evaluacion_id = obtener_id_tipo(db, "Cuestionarios")
    return crud.crear_evaluacion(db, datos)


# ------------------- FILTROS POR ESTUDIANTE Y PERIODO -------------------


@router.get("/asistencias/por-estudiante-periodo/", response_model=list[EvaluacionOut])
def asistencias_por_estudiante_periodo(
    estudiante_id: int,
    periodo_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(docente_o_admin_required),
):
    tipo_id = obtener_id_tipo(db, "Asistencia")
    return (
        db.query(Evaluacion)
        .filter(
            Evaluacion.estudiante_id == estudiante_id,
            Evaluacion.periodo_id == periodo_id,
            Evaluacion.tipo_evaluacion_id == tipo_id,
        )
        .all()
    )


@router.get(
    "/participaciones/por-estudiante-periodo/", response_model=list[EvaluacionOut]
)
def participaciones_por_estudiante_periodo(
    estudiante_id: int,
    periodo_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(docente_o_admin_required),
):
    tipo_id = obtener_id_tipo(db, "Participaciones")
    return (
        db.query(Evaluacion)
        .filter(
            Evaluacion.estudiante_id == estudiante_id,
            Evaluacion.periodo_id == periodo_id,
            Evaluacion.tipo_evaluacion_id == tipo_id,
        )
        .all()
    )


@router.get("/exposiciones/por-estudiante-periodo/", response_model=list[EvaluacionOut])
def exposiciones_por_estudiante_periodo(
    estudiante_id: int,
    periodo_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(docente_o_admin_required),
):
    tipo_id = obtener_id_tipo(db, "Exposiciones")
    return (
        db.query(Evaluacion)
        .filter(
            Evaluacion.estudiante_id == estudiante_id,
            Evaluacion.periodo_id == periodo_id,
            Evaluacion.tipo_evaluacion_id == tipo_id,
        )
        .all()
    )


@router.get("/tareas/por-estudiante-periodo/", response_model=list[EvaluacionOut])
def tareas_por_estudiante_periodo(
    estudiante_id: int,
    periodo_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(docente_o_admin_required),
):
    tipo_id = obtener_id_tipo(db, "Tareas")
    return (
        db.query(Evaluacion)
        .filter(
            Evaluacion.estudiante_id == estudiante_id,
            Evaluacion.periodo_id == periodo_id,
            Evaluacion.tipo_evaluacion_id == tipo_id,
        )
        .all()
    )


@router.get("/examenes/por-estudiante-periodo/", response_model=list[EvaluacionOut])
def examenes_por_estudiante_periodo(
    estudiante_id: int,
    periodo_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(docente_o_admin_required),
):
    tipo_id = obtener_id_tipo(db, "Exámenes")
    return (
        db.query(Evaluacion)
        .filter(
            Evaluacion.estudiante_id == estudiante_id,
            Evaluacion.periodo_id == periodo_id,
            Evaluacion.tipo_evaluacion_id == tipo_id,
        )
        .all()
    )


@router.get("/practicas/por-estudiante-periodo/", response_model=list[EvaluacionOut])
def practicas_por_estudiante_periodo(
    estudiante_id: int,
    periodo_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(docente_o_admin_required),
):
    tipo_id = obtener_id_tipo(db, "Prácticas")
    return (
        db.query(Evaluacion)
        .filter(
            Evaluacion.estudiante_id == estudiante_id,
            Evaluacion.periodo_id == periodo_id,
            Evaluacion.tipo_evaluacion_id == tipo_id,
        )
        .all()
    )


@router.get("/proyectos/por-estudiante-periodo/", response_model=list[EvaluacionOut])
def proyectos_por_estudiante_periodo(
    estudiante_id: int,
    periodo_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(docente_o_admin_required),
):
    tipo_id = obtener_id_tipo(db, "Proyecto final")
    return (
        db.query(Evaluacion)
        .filter(
            Evaluacion.estudiante_id == estudiante_id,
            Evaluacion.periodo_id == periodo_id,
            Evaluacion.tipo_evaluacion_id == tipo_id,
        )
        .all()
    )


@router.get("/grupales/por-estudiante-periodo/", response_model=list[EvaluacionOut])
def grupales_por_estudiante_periodo(
    estudiante_id: int,
    periodo_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(docente_o_admin_required),
):
    tipo_id = obtener_id_tipo(db, "Trabajo grupal")
    return (
        db.query(Evaluacion)
        .filter(
            Evaluacion.estudiante_id == estudiante_id,
            Evaluacion.periodo_id == periodo_id,
            Evaluacion.tipo_evaluacion_id == tipo_id,
        )
        .all()
    )


@router.get("/ensayos/por-estudiante-periodo/", response_model=list[EvaluacionOut])
def ensayos_por_estudiante_periodo(
    estudiante_id: int,
    periodo_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(docente_o_admin_required),
):
    tipo_id = obtener_id_tipo(db, "Ensayos")
    return (
        db.query(Evaluacion)
        .filter(
            Evaluacion.estudiante_id == estudiante_id,
            Evaluacion.periodo_id == periodo_id,
            Evaluacion.tipo_evaluacion_id == tipo_id,
        )
        .all()
    )


@router.get(
    "/cuestionarios/por-estudiante-periodo/", response_model=list[EvaluacionOut]
)
def cuestionarios_por_estudiante_periodo(
    estudiante_id: int,
    periodo_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(docente_o_admin_required),
):
    tipo_id = obtener_id_tipo(db, "Cuestionarios")
    return (
        db.query(Evaluacion)
        .filter(
            Evaluacion.estudiante_id == estudiante_id,
            Evaluacion.periodo_id == periodo_id,
            Evaluacion.tipo_evaluacion_id == tipo_id,
        )
        .all()
    )


# Evaluaciones por estudiante, materia, periodo y tipo
@router.get("/por-tipo", response_model=list[EvaluacionOut])
def ver_evaluaciones_por_tipo(
    estudiante_id: int,
    materia_id: int,
    periodo_id: int,
    tipo_evaluacion_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(docente_o_admin_required),
):
    return (
        db.query(Evaluacion)
        .filter(
            Evaluacion.estudiante_id == estudiante_id,
            Evaluacion.materia_id == materia_id,
            Evaluacion.periodo_id == periodo_id,
            Evaluacion.tipo_evaluacion_id == tipo_evaluacion_id,
        )
        .all()
    )


# ------------------- RESUMEN DE EVALUACIONES -------------------
from datetime import date


@router.get("/resumen/por-estudiante", response_model=dict)
def resumen_evaluaciones_auto_periodo(
    estudiante_id: int,
    materia_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(docente_o_admin_required),
):
    fecha_actual = date.today()
    periodo_id, _ = obtener_periodo_y_gestion_por_fecha(db, fecha_actual)

    tipos = db.query(TipoEvaluacion).order_by(TipoEvaluacion.id).all()
    resumen = {}

    for tipo in tipos:
        evaluaciones = (
            db.query(Evaluacion)
            .filter(
                Evaluacion.estudiante_id == estudiante_id,
                Evaluacion.materia_id == materia_id,
                Evaluacion.periodo_id == periodo_id,
                Evaluacion.tipo_evaluacion_id == tipo.id,
            )
            .all()
        )

        if not evaluaciones:
            continue

        key = str(tipo.id)
        detalle = [
            {
                "fecha": e.fecha.isoformat(),
                "descripcion": e.descripcion,
                "valor": e.valor,
            }
            for e in evaluaciones
        ]

        if tipo.nombre.lower() == "asistencia":
            presentes = sum(1 for e in evaluaciones if e.valor >= 1)
            porcentaje = round((presentes / len(evaluaciones)) * 100, 2)
            resumen[key] = {
                "id": tipo.id,
                "nombre": tipo.nombre,
                "porcentaje": porcentaje,
                "total": len(evaluaciones),
                "detalle": detalle,
            }
        else:
            promedio = round(sum(e.valor for e in evaluaciones) / len(evaluaciones), 2)
            resumen[key] = {
                "id": tipo.id,
                "nombre": tipo.nombre,
                "promedio": promedio,
                "total": len(evaluaciones),
                "detalle": detalle,
            }

    return {
        "fecha": fecha_actual.isoformat(),
        "periodo_id": periodo_id,
        "resumen": resumen,
    }


estado_valores = {
    "presente": (100, "Asistencia"),
    "falta": (0, "Falta injustificada"),
    "tarde": (50, "Llegó tarde"),
    "justificacion": (50, "Licencia médica"),
}


def obtener_periodo_y_gestion_por_fecha(db: Session, fecha: date):
    from app.models import Periodo

    periodo = (
        db.query(Periodo)
        .filter(Periodo.fecha_inicio <= fecha, Periodo.fecha_fin >= fecha)
        .first()
    )

    if not periodo:
        raise HTTPException(
            status_code=404,
            detail="La fecha no coincide con ningún periodo activo en ninguna gestión",
        )

    return periodo.id, periodo.gestion_id


@router.post("/asistencia")
def registrar_asistencia_masiva(
    docente_id: int,
    curso_id: int,
    materia_id: int,
    fecha: date,
    estudiantes: list[dict],
    db: Session = Depends(get_db),
    payload: dict = Depends(docente_o_admin_required),
):
    periodo_id, gestion_id = obtener_periodo_y_gestion_por_fecha(db, fecha)
    registros = []
    for est in estudiantes:
        est_id = est["id"]
        estado = est["estado"].lower()

        if estado not in estado_valores:
            raise HTTPException(status_code=400, detail=f"Estado inválido: {estado}")

        existente = (
            db.query(Evaluacion)
            .filter_by(
                estudiante_id=est_id,
                materia_id=materia_id,
                periodo_id=periodo_id,
                fecha=fecha,
                tipo_evaluacion_id=5,
            )
            .first()
        )
        if existente:
            continue

        valor, descripcion = estado_valores[estado]
        evaluacion = Evaluacion(
            fecha=fecha,
            descripcion=descripcion,
            valor=valor,
            estudiante_id=est_id,
            materia_id=materia_id,
            tipo_evaluacion_id=5,
            periodo_id=periodo_id,
        )
        db.add(evaluacion)
        registros.append(est_id)

    db.commit()
    return {
        "mensaje": f"Asistencia registrada para estudiantes: {registros}",
        "periodo_id": periodo_id,
        "gestion_id": gestion_id,
    }


@router.post("/participacion")
def registrar_participacion_masiva(
    docente_id: int,
    curso_id: int,
    materia_id: int,
    fecha: date,
    estudiantes: list[dict],
    db: Session = Depends(get_db),
    payload: dict = Depends(docente_o_admin_required),
):
    periodo_id, gestion_id = obtener_periodo_y_gestion_por_fecha(db, fecha)
    registros = []
    for est in estudiantes:
        est_id = est["id"]
        valor = est["valor"]
        descripcion = est.get("descripcion", "Participación")

        if not (0 <= valor <= 100):
            raise HTTPException(
                status_code=400,
                detail=f"Valor inválido para estudiante {est_id}: {valor}",
            )

        evaluacion = Evaluacion(
            fecha=fecha,
            descripcion=descripcion,
            valor=valor,
            estudiante_id=est_id,
            materia_id=materia_id,
            tipo_evaluacion_id=4,  # Participación
            periodo_id=periodo_id,
        )
        db.add(evaluacion)
        registros.append(est_id)

    db.commit()
    return {
        "mensaje": f"Participaciones registradas para estudiantes: {registros}",
        "periodo_id": periodo_id,
        "gestion_id": gestion_id,
    }


@router.get("/asistencia/masiva")
def obtener_asistencias_masiva(
    fecha: date,
    curso_id: int,
    materia_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(docente_o_admin_required),
):
    periodo_id, gestion_id = obtener_periodo_y_gestion_por_fecha(db, fecha)

    asistencias = (
        db.query(Evaluacion)
        .join(Estudiante)
        .join(Inscripcion)
        .filter(
            Evaluacion.fecha == fecha,
            Evaluacion.materia_id == materia_id,
            Evaluacion.tipo_evaluacion_id == 5,  # Asistencia
            Evaluacion.periodo_id == periodo_id,
            Inscripcion.curso_id == curso_id,
            Inscripcion.estudiante_id == Evaluacion.estudiante_id,
        )
        .all()
    )

    return {
        "fecha": fecha,
        "periodo_id": periodo_id,
        "gestion_id": gestion_id,
        "asistencias": [e.__dict__ for e in asistencias],
    }


@router.get("/participacion/masiva")
def obtener_participaciones_masiva(
    fecha: date,
    curso_id: int,
    materia_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(docente_o_admin_required),
):
    periodo_id, gestion_id = obtener_periodo_y_gestion_por_fecha(db, fecha)

    participaciones = (
        db.query(Evaluacion)
        .join(Estudiante)
        .join(Inscripcion)
        .filter(
            Evaluacion.fecha == fecha,
            Evaluacion.materia_id == materia_id,
            Evaluacion.tipo_evaluacion_id == 4,  # Participación
            Evaluacion.periodo_id == periodo_id,
            Inscripcion.curso_id == curso_id,
            Inscripcion.estudiante_id == Evaluacion.estudiante_id,
        )
        .all()
    )

    return {
        "fecha": fecha,
        "periodo_id": periodo_id,
        "gestion_id": gestion_id,
        "participaciones": [e.__dict__ for e in participaciones],
    }


@router.get("/evaluacion/masiva")
def obtener_evaluaciones_por_tipo(
    fecha: date,
    curso_id: int,
    materia_id: int,
    tipo_evaluacion_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(docente_o_admin_required),
):
    periodo_id, gestion_id = obtener_periodo_y_gestion_por_fecha(db, fecha)

    evaluaciones = (
        db.query(Evaluacion)
        .join(Estudiante)
        .join(Inscripcion)
        .filter(
            Evaluacion.fecha == fecha,
            Evaluacion.materia_id == materia_id,
            Evaluacion.tipo_evaluacion_id == tipo_evaluacion_id,
            Evaluacion.periodo_id == periodo_id,
            Inscripcion.curso_id == curso_id,
            Inscripcion.estudiante_id == Evaluacion.estudiante_id,
        )
        .all()
    )

    return {
        "fecha": fecha,
        "tipo_evaluacion_id": tipo_evaluacion_id,
        "periodo_id": periodo_id,
        "gestion_id": gestion_id,
        "evaluaciones": [e.__dict__ for e in evaluaciones],
    }


@router.post("/evaluaciones/registrar/masiva")
def registrar_evaluaciones_masiva(
    tipo_evaluacion_id: int,
    materia_id: int,
    fecha: date,
    estudiantes: list[dict],  # [{"id": 1, "valor": 85, "descripcion": "opcional"}]
    descripcion_general: str = None,
    db: Session = Depends(get_db),
    payload: dict = Depends(docente_o_admin_required),
):

    # Obtener periodo y gestión
    periodo_id, gestion_id = obtener_periodo_y_gestion_por_fecha(db, fecha)

    # Verificar tipo de evaluación
    tipo = db.query(TipoEvaluacion).filter_by(id=tipo_evaluacion_id).first()
    if not tipo:
        raise HTTPException(status_code=404, detail="Tipo de evaluación no encontrado")

    tipo_nombre = tipo.nombre
    registros = []

    for est in estudiantes:
        est_id = est["id"]
        valor = est["valor"]

        if not (0 <= valor <= 100):
            raise HTTPException(
                status_code=400,
                detail=f"Valor inválido para estudiante {est_id}: {valor}",
            )

        descripcion = est.get("descripcion") or descripcion_general or tipo_nombre

        evaluacion = Evaluacion(
            fecha=fecha,
            descripcion=descripcion,
            valor=valor,
            estudiante_id=est_id,
            materia_id=materia_id,
            tipo_evaluacion_id=tipo_evaluacion_id,
            periodo_id=periodo_id,
        )
        db.add(evaluacion)
        registros.append(est_id)

    db.commit()
    return {
        "mensaje": f"Evaluaciones '{tipo_nombre}' registradas para estudiantes: {registros}",
        "periodo_id": periodo_id,
        "gestion_id": gestion_id,
        "tipo_evaluacion": tipo_nombre,
    }
    
@router.get("/resumen/por-estudiante-periodo", response_model=dict)
def resumen_evaluaciones_por_estudiante_y_periodo(
    estudiante_id: int,
    materia_id: int,
    periodo_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(docente_o_admin_required),
):
    tipos = db.query(TipoEvaluacion).order_by(TipoEvaluacion.id).all()
    resumen = {}

    for tipo in tipos:
        evaluaciones = (
            db.query(Evaluacion)
            .filter(
                Evaluacion.estudiante_id == estudiante_id,
                Evaluacion.materia_id == materia_id,
                Evaluacion.periodo_id == periodo_id,
                Evaluacion.tipo_evaluacion_id == tipo.id,
            )
            .all()
        )

        if not evaluaciones:
            continue

        key = str(tipo.id)
        detalle = [
            {
                "fecha": e.fecha.isoformat(),
                "descripcion": e.descripcion,
                "valor": e.valor,
            }
            for e in evaluaciones
        ]

        if tipo.nombre.lower() == "asistencia":
            presentes = sum(1 for e in evaluaciones if e.valor >= 1)
            porcentaje = round((presentes / len(evaluaciones)) * 100, 2)
            resumen[key] = {
                "id": tipo.id,
                "nombre": tipo.nombre,
                "porcentaje": porcentaje,
                "total": len(evaluaciones),
                "detalle": detalle,
            }
        else:
            promedio = round(sum(e.valor for e in evaluaciones) / len(evaluaciones), 2)
            resumen[key] = {
                "id": tipo.id,
                "nombre": tipo.nombre,
                "promedio": promedio,
                "total": len(evaluaciones),
                "detalle": detalle,
            }

    return {
        "periodo_id": periodo_id,
        "resumen": resumen,
    }
