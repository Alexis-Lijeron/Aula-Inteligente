from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, desc, func
from app.models.notificacion import Notificacion
from app.models.estudiante import Estudiante
from app.models.evaluacion import Evaluacion
from app.models.materia import Materia
from app.schemas.notificacion import NotificacionCreate, NotificacionUpdate
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


def crear_notificacion(db: Session, notificacion: NotificacionCreate) -> Notificacion:
    """Crear una nueva notificación"""
    db_notificacion = Notificacion(**notificacion.dict())
    db.add(db_notificacion)
    db.commit()
    db.refresh(db_notificacion)
    logger.info(f"Notificación creada: ID {db_notificacion.id}")
    return db_notificacion


def obtener_notificaciones_padre(
    db: Session, padre_id: int, limit: int = 50, solo_no_leidas: bool = False
) -> List[dict]:
    """Obtener notificaciones de un padre con información adicional"""
    query = (
        db.query(Notificacion)
        .options(
            joinedload(Notificacion.estudiante),
            joinedload(Notificacion.evaluacion).joinedload(Evaluacion.materia),
        )
        .filter(Notificacion.padre_id == padre_id)
    )

    if solo_no_leidas:
        query = query.filter(Notificacion.leida == False)

    notificaciones = query.order_by(desc(Notificacion.created_at)).limit(limit).all()

    # Formatear respuesta con información adicional
    resultado = []
    for notif in notificaciones:
        item = {
            "id": notif.id,
            "titulo": notif.titulo,
            "mensaje": notif.mensaje,
            "tipo": notif.tipo,
            "leida": notif.leida,
            "padre_id": notif.padre_id,
            "estudiante_id": notif.estudiante_id,
            "evaluacion_id": notif.evaluacion_id,
            "created_at": notif.created_at,
            "updated_at": notif.updated_at,
            "estudiante_nombre": notif.estudiante.nombre if notif.estudiante else None,
            "estudiante_apellido": (
                notif.estudiante.apellido if notif.estudiante else None
            ),
            "materia_nombre": (
                notif.evaluacion.materia.nombre
                if notif.evaluacion and notif.evaluacion.materia
                else None
            ),
            "evaluacion_valor": notif.evaluacion.valor if notif.evaluacion else None,
        }
        resultado.append(item)

    return resultado


def obtener_notificacion_por_id(
    db: Session, notificacion_id: int, padre_id: int = None
) -> Optional[Notificacion]:
    """Obtener una notificación específica"""
    query = db.query(Notificacion).filter(Notificacion.id == notificacion_id)

    if padre_id:
        query = query.filter(Notificacion.padre_id == padre_id)

    return query.first()


def marcar_como_leida(
    db: Session, notificacion_id: int, padre_id: int
) -> Optional[Notificacion]:
    """Marcar una notificación como leída"""
    notificacion = (
        db.query(Notificacion)
        .filter(
            and_(Notificacion.id == notificacion_id, Notificacion.padre_id == padre_id)
        )
        .first()
    )

    if notificacion:
        notificacion.leida = True
        db.commit()
        db.refresh(notificacion)
        logger.info(f"Notificación {notificacion_id} marcada como leída")

    return notificacion


def marcar_todas_como_leidas(db: Session, padre_id: int) -> int:
    """Marcar todas las notificaciones como leídas"""
    count = (
        db.query(Notificacion)
        .filter(and_(Notificacion.padre_id == padre_id, Notificacion.leida == False))
        .update({"leida": True})
    )
    db.commit()
    logger.info(f"Marcadas {count} notificaciones como leídas para padre {padre_id}")
    return count


def obtener_estadisticas_notificaciones(db: Session, padre_id: int) -> dict:
    """Obtener estadísticas de notificaciones de un padre"""
    total = db.query(Notificacion).filter(Notificacion.padre_id == padre_id).count()

    no_leidas = (
        db.query(Notificacion)
        .filter(and_(Notificacion.padre_id == padre_id, Notificacion.leida == False))
        .count()
    )

    leidas = total - no_leidas

    # Estadísticas por tipo
    tipos = (
        db.query(Notificacion.tipo, func.count(Notificacion.id))
        .filter(Notificacion.padre_id == padre_id)
        .group_by(Notificacion.tipo)
        .all()
    )

    por_tipo = {tipo: count for tipo, count in tipos}

    return {
        "total": total,
        "no_leidas": no_leidas,
        "leidas": leidas,
        "por_tipo": por_tipo,
    }


def eliminar_notificacion(db: Session, notificacion_id: int, padre_id: int) -> bool:
    """Eliminar una notificación"""
    notificacion = (
        db.query(Notificacion)
        .filter(
            and_(Notificacion.id == notificacion_id, Notificacion.padre_id == padre_id)
        )
        .first()
    )

    if notificacion:
        db.delete(notificacion)
        db.commit()
        logger.info(f"Notificación {notificacion_id} eliminada")
        return True

    return False


def obtener_notificaciones_admin(
    db: Session,
    limit: int = 100,
    tipo: Optional[str] = None,
    padre_id: Optional[int] = None,
    estudiante_id: Optional[int] = None,
) -> List[Notificacion]:
    """Obtener notificaciones para administradores"""
    query = db.query(Notificacion)

    if tipo:
        query = query.filter(Notificacion.tipo == tipo)
    if padre_id:
        query = query.filter(Notificacion.padre_id == padre_id)
    if estudiante_id:
        query = query.filter(Notificacion.estudiante_id == estudiante_id)

    return query.order_by(desc(Notificacion.created_at)).limit(limit).all()


def contar_notificaciones_no_leidas_padre(db: Session, padre_id: int) -> int:
    """Contar notificaciones no leídas de un padre"""
    return (
        db.query(Notificacion)
        .filter(and_(Notificacion.padre_id == padre_id, Notificacion.leida == False))
        .count()
    )
