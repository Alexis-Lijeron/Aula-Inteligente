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
from app.auth.roles import docente_o_admin_required, usuario_autenticado
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
    payload: dict = Depends(usuario_autenticado),
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


@router.get("/resumen/por-estudiante-periodo-total", response_model=dict)
def resumen_evaluaciones_por_estudiante_y_periodo(
    estudiante_id: int,
    materia_id: int,
    periodo_id: int,
    docente_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(usuario_autenticado),
):
    from app.models import Periodo, PesoTipoEvaluacion

    # Obtener la gestión a partir del periodo
    periodo = db.query(Periodo).filter_by(id=periodo_id).first()
    if not periodo:
        raise HTTPException(status_code=404, detail="Periodo no encontrado")

    gestion_id = periodo.gestion_id

    tipos = db.query(TipoEvaluacion).order_by(TipoEvaluacion.id).all()
    resumen = {}
    total_ponderado = 0
    total_puntos = 0

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

        # ✅ Corregido: usamos tipo_evaluacion_id
        peso = (
            db.query(PesoTipoEvaluacion)
            .filter(
                PesoTipoEvaluacion.docente_id == docente_id,
                PesoTipoEvaluacion.materia_id == materia_id,
                PesoTipoEvaluacion.gestion_id == gestion_id,
                PesoTipoEvaluacion.tipo_evaluacion_id == tipo.id,
            )
            .first()
        )

        if not peso:
            continue  # si no hay peso definido, lo omitimos

        puntos_tipo = peso.porcentaje
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
                "puntos": puntos_tipo,
            }
        else:
            promedio = round(sum(e.valor for e in evaluaciones) / len(evaluaciones), 2)
            ponderado = promedio * (puntos_tipo / 100)
            total_ponderado += ponderado
            total_puntos += puntos_tipo

            resumen[key] = {
                "id": tipo.id,
                "nombre": tipo.nombre,
                "promedio": promedio,
                "total": len(evaluaciones),
                "detalle": detalle,
                "puntos": puntos_tipo,
            }

    promedio_general = (
        round((total_ponderado / total_puntos) * 100, 2) if total_puntos > 0 else 0.0
    )

    return {
        "periodo_id": periodo_id,
        "gestion_id": gestion_id,
        "promedio_general": promedio_general,
        "resumen": resumen,
    }


@router.get("/resumen/por-estudiante-periodo-definitivo", response_model=dict)
def resumen_evaluaciones_por_estudiante_y_periodo(
    estudiante_id: int,
    materia_id: int,
    periodo_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(usuario_autenticado),
):
    from app.models import Periodo, PesoTipoEvaluacion, DocenteMateria

    # Obtener gestión desde el periodo
    periodo = db.query(Periodo).filter_by(id=periodo_id).first()
    if not periodo:
        raise HTTPException(status_code=404, detail="Periodo no encontrado")
    gestion_id = periodo.gestion_id

    # Obtener el docente asignado a la materia
    docente_materia = db.query(DocenteMateria).filter_by(materia_id=materia_id).first()
    if not docente_materia:
        raise HTTPException(
            status_code=404, detail="No se encontró docente asignado a esta materia."
        )
    docente_id = docente_materia.docente_id

    tipos = db.query(TipoEvaluacion).order_by(TipoEvaluacion.id).all()
    resumen = {}
    total_ponderado = 0
    total_puntos = 0

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

        # Obtener el porcentaje definido por el docente
        peso = (
            db.query(PesoTipoEvaluacion)
            .filter(
                PesoTipoEvaluacion.docente_id == docente_id,
                PesoTipoEvaluacion.materia_id == materia_id,
                PesoTipoEvaluacion.gestion_id == gestion_id,
                PesoTipoEvaluacion.tipo_evaluacion_id == tipo.id,
            )
            .first()
        )

        if not peso:
            continue

        puntos_tipo = peso.porcentaje
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
                "puntos": puntos_tipo,
            }
        else:
            promedio = round(sum(e.valor for e in evaluaciones) / len(evaluaciones), 2)
            ponderado = promedio * (puntos_tipo / 100)
            total_ponderado += ponderado
            total_puntos += puntos_tipo

            resumen[key] = {
                "id": tipo.id,
                "nombre": tipo.nombre,
                "promedio": promedio,
                "total": len(evaluaciones),
                "detalle": detalle,
                "puntos": puntos_tipo,
            }

    promedio_general = (
        round((total_ponderado / total_puntos) * 100, 2) if total_puntos > 0 else 0.0
    )

    return {
        "periodo_id": periodo_id,
        "gestion_id": gestion_id,
        "promedio_general": promedio_general,
        "resumen": resumen,
    }


@router.get("/por-docente/{docente_id}", response_model=list[EvaluacionOut])
def evaluaciones_por_docente(
    docente_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(docente_o_admin_required),
):
    from app.models import DocenteMateria

    # Obtener las materias que enseña el docente
    materias_asignadas = (
        db.query(DocenteMateria.materia_id)
        .filter(DocenteMateria.docente_id == docente_id)
        .all()
    )

    materia_ids = [m.materia_id for m in materias_asignadas]

    if not materia_ids:
        raise HTTPException(
            status_code=404, detail="El docente no tiene materias asignadas"
        )

    # Buscar evaluaciones de esas materias
    evaluaciones = (
        db.query(Evaluacion)
        .filter(Evaluacion.materia_id.in_(materia_ids))
        .order_by(Evaluacion.fecha.desc())
        .all()
    )

    return evaluaciones


@router.get("/resumen/por-estudiante-docente-auto", response_model=dict)
def resumen_por_estudiante_docente_auto(
    estudiante_id: int,
    docente_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(usuario_autenticado),
):
    from app.models import (
        Periodo,
        Inscripcion,
        DocenteMateria,
        PesoTipoEvaluacion,
        TipoEvaluacion,
        Curso,
        Materia,
    )

    # Paso 1: determinar periodo activo por fecha actual
    fecha_actual = date.today()
    periodo = (
        db.query(Periodo)
        .filter(Periodo.fecha_inicio <= fecha_actual, Periodo.fecha_fin >= fecha_actual)
        .first()
    )
    if not periodo:
        raise HTTPException(status_code=404, detail="No se encontró un periodo activo")
    periodo_id = periodo.id
    gestion_id = periodo.gestion_id

    # Paso 2: obtener curso del estudiante en esta gestión
    inscripcion = (
        db.query(Inscripcion)
        .filter_by(estudiante_id=estudiante_id, gestion_id=gestion_id)
        .first()
    )
    if not inscripcion:
        raise HTTPException(
            status_code=404, detail="El estudiante no está inscrito en esta gestión"
        )
    curso_id = inscripcion.curso_id

    # Paso 3: obtener materia asignada al docente
    materia_docente = db.query(DocenteMateria).filter_by(docente_id=docente_id).first()
    if not materia_docente:
        raise HTTPException(
            status_code=404, detail="El docente no tiene materias asignadas"
        )
    materia_id = materia_docente.materia_id

    # Paso 4: verificar si hay evaluaciones del estudiante en esa materia y periodo
    evaluaciones_existentes = (
        db.query(Evaluacion)
        .filter_by(
            estudiante_id=estudiante_id, periodo_id=periodo_id, materia_id=materia_id
        )
        .first()
    )
    if not evaluaciones_existentes:
        raise HTTPException(
            status_code=404,
            detail="No se encontraron evaluaciones del estudiante para esa materia y periodo",
        )

    # Paso 5: construir el resumen ponderado
    tipos = db.query(TipoEvaluacion).order_by(TipoEvaluacion.id).all()
    resumen = {}
    total_ponderado = 0
    total_puntos = 0

    for tipo in tipos:
        evaluaciones = (
            db.query(Evaluacion)
            .filter_by(
                estudiante_id=estudiante_id,
                materia_id=materia_id,
                periodo_id=periodo_id,
                tipo_evaluacion_id=tipo.id,
            )
            .all()
        )
        if not evaluaciones:
            continue

        peso = (
            db.query(PesoTipoEvaluacion)
            .filter_by(
                docente_id=docente_id,
                materia_id=materia_id,
                gestion_id=gestion_id,
                tipo_evaluacion_id=tipo.id,
            )
            .first()
        )

        if not peso:
            continue

        puntos_tipo = peso.porcentaje
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
                "puntos": puntos_tipo,
            }
        else:
            promedio = round(sum(e.valor for e in evaluaciones) / len(evaluaciones), 2)
            ponderado = promedio * (puntos_tipo / 100)
            total_ponderado += ponderado
            total_puntos += puntos_tipo

            resumen[key] = {
                "id": tipo.id,
                "nombre": tipo.nombre,
                "promedio": promedio,
                "total": len(evaluaciones),
                "detalle": detalle,
                "puntos": puntos_tipo,
            }

    promedio_general = (
        round((total_ponderado / total_puntos) * 100, 2) if total_puntos > 0 else 0.0
    )

    # También retornamos los nombres si se desea mostrar en frontend
    curso = db.query(Curso).filter_by(id=curso_id).first()
    materia = db.query(Materia).filter_by(id=materia_id).first()

    return {
        "fecha_actual": fecha_actual.isoformat(),
        "periodo_id": periodo_id,
        "gestion_id": gestion_id,
        "curso": {
            "id": curso_id,
            "nombre": curso.nombre,
            "nivel": curso.nivel,
            "paralelo": curso.paralelo,
            "turno": curso.turno,
        },
        "materia": {
            "id": materia_id,
            "nombre": materia.nombre,
        },
        "promedio_general": promedio_general,
        "resumen": resumen,
    }
