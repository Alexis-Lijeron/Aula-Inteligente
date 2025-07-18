from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
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

# 🆕 NUEVO: Imports para el sistema de notificaciones
from app.services.notification_service import NotificationService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/evaluaciones", tags=["Evaluaciones"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 🆕 NUEVA: Función helper para manejar notificaciones automáticas
def _verificar_y_notificar_calificacion_baja(db: Session, evaluacion: Evaluacion):
    """Helper para verificar y enviar notificaciones de calificaciones bajas"""
    if evaluacion and evaluacion.valor < 50:
        try:
            notificaciones = (
                NotificationService.verificar_y_notificar_calificacion_baja(
                    db, evaluacion.id
                )
            )
            if notificaciones:
                logger.info(
                    f"Enviadas {len(notificaciones)} notificaciones para evaluación {evaluacion.id} (valor: {evaluacion.valor})"
                )
            return len(notificaciones)
        except Exception as e:
            logger.error(
                f"Error enviando notificaciones para evaluación {evaluacion.id}: {e}"
            )
            return 0
    return 0


@router.post("/", response_model=EvaluacionOut)
def crear(
    datos: EvaluacionCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(docente_o_admin_required),
):
    evaluacion = crud.crear_evaluacion(db, datos)

    # 🆕 NUEVO: Verificar y notificar si es calificación baja
    _verificar_y_notificar_calificacion_baja(db, evaluacion)

    return evaluacion


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

    # 🆕 NUEVO: Verificar y notificar si la actualización resultó en calificación baja
    _verificar_y_notificar_calificacion_baja(db, e)

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
    evaluacion = crud.crear_evaluacion(db, datos)

    # 🆕 NUEVO: Verificar y notificar si es calificación baja
    _verificar_y_notificar_calificacion_baja(db, evaluacion)

    return evaluacion


@router.post("/registrar/tarea", response_model=EvaluacionOut)
def registrar_tarea(
    datos: EvaluacionCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(docente_o_admin_required),
):
    datos.tipo_evaluacion_id = obtener_id_tipo(db, "Tareas")
    evaluacion = crud.crear_evaluacion(db, datos)

    # 🆕 NUEVO: Verificar y notificar si es calificación baja
    _verificar_y_notificar_calificacion_baja(db, evaluacion)

    return evaluacion


@router.post("/registrar/exposicion", response_model=EvaluacionOut)
def registrar_exposicion(
    datos: EvaluacionCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(docente_o_admin_required),
):
    datos.tipo_evaluacion_id = obtener_id_tipo(db, "Exposiciones")
    evaluacion = crud.crear_evaluacion(db, datos)

    # 🆕 NUEVO: Verificar y notificar si es calificación baja
    _verificar_y_notificar_calificacion_baja(db, evaluacion)

    return evaluacion


@router.post("/registrar/participacion", response_model=EvaluacionOut)
def registrar_participacion(
    datos: EvaluacionCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(docente_o_admin_required),
):
    datos.tipo_evaluacion_id = obtener_id_tipo(db, "Participaciones")
    evaluacion = crud.crear_evaluacion(db, datos)

    # 🆕 NUEVO: Verificar y notificar si es calificación baja
    _verificar_y_notificar_calificacion_baja(db, evaluacion)

    return evaluacion


@router.post("/registrar/asistencia", response_model=EvaluacionOut)
def registrar_asistencia(
    datos: EvaluacionCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(docente_o_admin_required),
):
    datos.tipo_evaluacion_id = obtener_id_tipo(db, "Asistencia")
    evaluacion = crud.crear_evaluacion(db, datos)

    # 🆕 NUEVO: Verificar y notificar si es calificación baja
    _verificar_y_notificar_calificacion_baja(db, evaluacion)

    return evaluacion


@router.post("/registrar/practica", response_model=EvaluacionOut)
def registrar_practica(
    datos: EvaluacionCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(docente_o_admin_required),
):
    datos.tipo_evaluacion_id = obtener_id_tipo(db, "Prácticas")
    evaluacion = crud.crear_evaluacion(db, datos)

    # 🆕 NUEVO: Verificar y notificar si es calificación baja
    _verificar_y_notificar_calificacion_baja(db, evaluacion)

    return evaluacion


@router.post("/registrar/proyecto", response_model=EvaluacionOut)
def registrar_proyecto_final(
    datos: EvaluacionCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(docente_o_admin_required),
):
    datos.tipo_evaluacion_id = obtener_id_tipo(db, "Proyecto final")
    evaluacion = crud.crear_evaluacion(db, datos)

    # 🆕 NUEVO: Verificar y notificar si es calificación baja
    _verificar_y_notificar_calificacion_baja(db, evaluacion)

    return evaluacion


@router.post("/registrar/grupal", response_model=EvaluacionOut)
def registrar_trabajo_grupal(
    datos: EvaluacionCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(docente_o_admin_required),
):
    datos.tipo_evaluacion_id = obtener_id_tipo(db, "Trabajo grupal")
    evaluacion = crud.crear_evaluacion(db, datos)

    # 🆕 NUEVO: Verificar y notificar si es calificación baja
    _verificar_y_notificar_calificacion_baja(db, evaluacion)

    return evaluacion


@router.post("/registrar/ensayo", response_model=EvaluacionOut)
def registrar_ensayo(
    datos: EvaluacionCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(docente_o_admin_required),
):
    datos.tipo_evaluacion_id = obtener_id_tipo(db, "Ensayos")
    evaluacion = crud.crear_evaluacion(db, datos)

    # 🆕 NUEVO: Verificar y notificar si es calificación baja
    _verificar_y_notificar_calificacion_baja(db, evaluacion)

    return evaluacion


@router.post("/registrar/cuestionario", response_model=EvaluacionOut)
def registrar_cuestionario(
    datos: EvaluacionCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(docente_o_admin_required),
):
    datos.tipo_evaluacion_id = obtener_id_tipo(db, "Cuestionarios")
    evaluacion = crud.crear_evaluacion(db, datos)

    # 🆕 NUEVO: Verificar y notificar si es calificación baja
    _verificar_y_notificar_calificacion_baja(db, evaluacion)

    return evaluacion


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
    notificaciones_enviadas = 0  # 🆕 NUEVO: Contador de notificaciones

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

    # 🆕 NUEVO: Verificar notificaciones para asistencias con valor < 50
    for est in estudiantes:
        est_id = est["id"]
        estado = est["estado"].lower()
        valor, _ = estado_valores[estado]

        if valor < 50:  # Falta o tarde
            evaluacion_creada = (
                db.query(Evaluacion)
                .filter_by(
                    estudiante_id=est_id,
                    materia_id=materia_id,
                    periodo_id=periodo_id,
                    fecha=fecha,
                    tipo_evaluacion_id=5,
                    valor=valor,
                )
                .first()
            )

            if evaluacion_creada:
                count = _verificar_y_notificar_calificacion_baja(db, evaluacion_creada)
                notificaciones_enviadas += count

    return {
        "mensaje": f"Asistencia registrada para estudiantes: {registros}",
        "periodo_id": periodo_id,
        "gestion_id": gestion_id,
        "notificaciones_enviadas": notificaciones_enviadas,  # 🆕 NUEVO
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
    notificaciones_enviadas = 0  # 🆕 NUEVO: Contador de notificaciones

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

    # 🆕 NUEVO: Verificar notificaciones para participaciones bajas
    for est in estudiantes:
        est_id = est["id"]
        valor = est["valor"]

        if valor < 50:
            evaluacion_creada = (
                db.query(Evaluacion)
                .filter_by(
                    estudiante_id=est_id,
                    materia_id=materia_id,
                    periodo_id=periodo_id,
                    fecha=fecha,
                    tipo_evaluacion_id=4,
                    valor=valor,
                )
                .first()
            )

            if evaluacion_creada:
                count = _verificar_y_notificar_calificacion_baja(db, evaluacion_creada)
                notificaciones_enviadas += count

    return {
        "mensaje": f"Participaciones registradas para estudiantes: {registros}",
        "periodo_id": periodo_id,
        "gestion_id": gestion_id,
        "notificaciones_enviadas": notificaciones_enviadas,  # 🆕 NUEVO
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
    notificaciones_enviadas = 0  # 🆕 NUEVO: Contador de notificaciones

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

    # 🆕 NUEVO: Verificar y notificar calificaciones bajas
    for est in estudiantes:
        est_id = est["id"]
        valor = est["valor"]

        if valor < 50:
            # Buscar la evaluación recién creada
            evaluacion_creada = (
                db.query(Evaluacion)
                .filter(
                    Evaluacion.estudiante_id == est_id,
                    Evaluacion.materia_id == materia_id,
                    Evaluacion.tipo_evaluacion_id == tipo_evaluacion_id,
                    Evaluacion.fecha == fecha,
                    Evaluacion.valor == valor,
                )
                .order_by(Evaluacion.id.desc())
                .first()
            )

            if evaluacion_creada:
                count = _verificar_y_notificar_calificacion_baja(db, evaluacion_creada)
                notificaciones_enviadas += count

    return {
        "mensaje": f"Evaluaciones '{tipo_nombre}' registradas para estudiantes: {registros}",
        "periodo_id": periodo_id,
        "gestion_id": gestion_id,
        "tipo_evaluacion": tipo_nombre,
        "notificaciones_enviadas": notificaciones_enviadas,  # 🆕 NUEVO
    }


# 🆕 NUEVO: Endpoint para verificar notificaciones manualmente
@router.post("/verificar-notificaciones/{evaluacion_id}")
def verificar_notificaciones_evaluacion(
    evaluacion_id: int,
    umbral: float = Query(
        50.0, ge=0, le=100, description="Umbral mínimo para notificar"
    ),
    db: Session = Depends(get_db),
    payload: dict = Depends(docente_o_admin_required),
):
    """🔔 Verificar manualmente si una evaluación necesita notificaciones"""
    try:
        notificaciones = NotificationService.verificar_y_notificar_calificacion_baja(
            db, evaluacion_id, umbral
        )

        return {
            "success": True,
            "mensaje": f"{len(notificaciones)} notificaciones enviadas",
            "notificaciones_ids": notificaciones,
            "umbral_usado": umbral,
            "evaluacion_id": evaluacion_id,
        }

    except Exception as e:
        logger.error(
            f"Error verificando notificaciones para evaluación {evaluacion_id}: {e}"
        )
        raise HTTPException(status_code=500, detail="Error interno del servidor")


# 🆕 NUEVO: Endpoint para reenviar notificaciones de evaluaciones existentes
@router.post("/reenviar-notificaciones-bajas")
def reenviar_notificaciones_calificaciones_bajas(
    materia_id: int = Query(..., description="ID de la materia"),
    periodo_id: int = Query(..., description="ID del periodo"),
    umbral: float = Query(
        50.0, ge=0, le=100, description="Umbral para calificaciones bajas"
    ),
    db: Session = Depends(get_db),
    payload: dict = Depends(docente_o_admin_required),
):
    """🔄 Reenviar notificaciones para todas las calificaciones bajas existentes"""
    try:
        # Buscar todas las evaluaciones con valor menor al umbral
        evaluaciones_bajas = (
            db.query(Evaluacion)
            .filter(
                Evaluacion.materia_id == materia_id,
                Evaluacion.periodo_id == periodo_id,
                Evaluacion.valor < umbral,
            )
            .all()
        )

        total_notificaciones = 0
        evaluaciones_procesadas = 0

        for evaluacion in evaluaciones_bajas:
            try:
                notificaciones = (
                    NotificationService.verificar_y_notificar_calificacion_baja(
                        db, evaluacion.id, umbral
                    )
                )
                total_notificaciones += len(notificaciones)
                evaluaciones_procesadas += 1
            except Exception as e:
                logger.error(f"Error procesando evaluación {evaluacion.id}: {e}")
                continue

        return {
            "success": True,
            "mensaje": f"Proceso completado: {total_notificaciones} notificaciones enviadas",
            "evaluaciones_procesadas": evaluaciones_procesadas,
            "total_evaluaciones_bajas": len(evaluaciones_bajas),
            "notificaciones_enviadas": total_notificaciones,
            "umbral_usado": umbral,
        }

    except Exception as e:
        logger.error(f"Error en reenviar_notificaciones_calificaciones_bajas: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


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
