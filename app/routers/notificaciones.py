from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.auth.roles import (
    usuario_autenticado,
    admin_required,
    docente_o_admin_required,
)
from app.schemas.notificacion import (
    NotificacionOut,
    NotificacionStats,
    NotificacionResponse,
    NotificacionListResponse,
)
from app.crud import notificacion as crud_notificacion
from app.services.notification_service import NotificationService
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notificaciones", tags=["📢 Notificaciones para Padres"])
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ========== ENDPOINTS PARA PADRES AUTENTICADOS ==========


@router.get("/mis-notificaciones", response_model=List[NotificacionOut])
def obtener_mis_notificaciones(
    limit: int = Query(50, ge=1, le=100, description="Número máximo de notificaciones"),
    solo_no_leidas: bool = Query(False, description="Solo mostrar no leídas"),
    payload: dict = Depends(usuario_autenticado),
    db: Session = Depends(get_db),
):
    """📱 Obtener mis notificaciones como padre"""
    # Verificar que el usuario es padre
    if payload.get("user_type") != "padre":
        raise HTTPException(
            status_code=403, detail="Solo padres pueden acceder a este endpoint"
        )

    padre_id = payload.get("user_id")

    try:
        notificaciones = crud_notificacion.obtener_notificaciones_padre(
            db, padre_id, limit, solo_no_leidas
        )

        logger.info(f"Padre {padre_id} consultó {len(notificaciones)} notificaciones")
        return notificaciones

    except Exception as e:
        logger.error(f"Error obteniendo notificaciones para padre {padre_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/count-no-leidas")
def contar_notificaciones_no_leidas(
    payload: dict = Depends(usuario_autenticado),
    db: Session = Depends(get_db),
):
    """🔢 Obtener cantidad de notificaciones no leídas (para badges)"""
    if payload.get("user_type") != "padre":
        raise HTTPException(status_code=403, detail="Solo padres pueden acceder")

    padre_id = payload.get("user_id")

    try:
        count = crud_notificacion.contar_notificaciones_no_leidas_padre(db, padre_id)
        return {"count": count}

    except Exception as e:
        logger.error(f"Error contando notificaciones no leídas: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.put("/{notificacion_id}/marcar-leida")
def marcar_notificacion_como_leida(
    notificacion_id: int,
    payload: dict = Depends(usuario_autenticado),
    db: Session = Depends(get_db),
):
    """✅ Marcar notificación como leída"""
    if payload.get("user_type") != "padre":
        raise HTTPException(status_code=403, detail="Solo padres pueden acceder")

    padre_id = payload.get("user_id")

    try:
        notificacion = crud_notificacion.marcar_como_leida(
            db, notificacion_id, padre_id
        )

        if not notificacion:
            raise HTTPException(status_code=404, detail="Notificación no encontrada")

        return {"success": True, "mensaje": "Notificación marcada como leída"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error marcando notificación {notificacion_id} como leída: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.put("/marcar-todas-leidas")
def marcar_todas_las_notificaciones_como_leidas(
    payload: dict = Depends(usuario_autenticado),
    db: Session = Depends(get_db),
):
    """✅ Marcar todas mis notificaciones como leídas"""
    if payload.get("user_type") != "padre":
        raise HTTPException(status_code=403, detail="Solo padres pueden acceder")

    padre_id = payload.get("user_id")

    try:
        count = crud_notificacion.marcar_todas_como_leidas(db, padre_id)

        return {
            "success": True,
            "mensaje": f"{count} notificaciones marcadas como leídas",
            "count": count,
        }

    except Exception as e:
        logger.error(f"Error marcando todas las notificaciones como leídas: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/estadisticas", response_model=NotificacionStats)
def obtener_estadisticas_notificaciones(
    payload: dict = Depends(usuario_autenticado),
    db: Session = Depends(get_db),
):
    """📊 Obtener estadísticas de mis notificaciones"""
    if payload.get("user_type") != "padre":
        raise HTTPException(status_code=403, detail="Solo padres pueden acceder")

    padre_id = payload.get("user_id")

    try:
        stats = crud_notificacion.obtener_estadisticas_notificaciones(db, padre_id)
        return stats

    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/{notificacion_id}", response_model=NotificacionOut)
def obtener_notificacion_detalle(
    notificacion_id: int,
    payload: dict = Depends(usuario_autenticado),
    db: Session = Depends(get_db),
):
    """👁️ Obtener detalle de una notificación específica"""
    if payload.get("user_type") != "padre":
        raise HTTPException(status_code=403, detail="Solo padres pueden acceder")

    padre_id = payload.get("user_id")

    try:
        notificacion = crud_notificacion.obtener_notificacion_por_id(
            db, notificacion_id, padre_id
        )

        if not notificacion:
            raise HTTPException(status_code=404, detail="Notificación no encontrada")

        # Marcar como leída automáticamente al ver el detalle
        if not notificacion.leida:
            crud_notificacion.marcar_como_leida(db, notificacion_id, padre_id)

        return notificacion

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error obteniendo detalle de notificación {notificacion_id}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.delete("/{notificacion_id}")
def eliminar_notificacion(
    notificacion_id: int,
    payload: dict = Depends(usuario_autenticado),
    db: Session = Depends(get_db),
):
    """🗑️ Eliminar una notificación"""
    if payload.get("user_type") != "padre":
        raise HTTPException(status_code=403, detail="Solo padres pueden acceder")

    padre_id = payload.get("user_id")

    try:
        eliminada = crud_notificacion.eliminar_notificacion(
            db, notificacion_id, padre_id
        )

        if not eliminada:
            raise HTTPException(status_code=404, detail="Notificación no encontrada")

        return {"success": True, "mensaje": "Notificación eliminada correctamente"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error eliminando notificación {notificacion_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


# ========== ENDPOINTS ADMINISTRATIVOS ==========


@router.post("/admin/crear-notificacion")
def crear_notificacion_admin(
    padre_id: int,
    estudiante_id: int,
    titulo: str,
    mensaje: str,
    tipo: str = "general",
    evaluacion_id: Optional[int] = None,
    payload: dict = Depends(admin_required),
    db: Session = Depends(get_db),
):
    """👑 Crear notificación personalizada (Solo Administradores)"""
    try:
        notificacion_id = NotificationService.crear_notificacion_personalizada(
            db, padre_id, estudiante_id, titulo, mensaje, tipo, evaluacion_id
        )

        if not notificacion_id:
            raise HTTPException(status_code=400, detail="Error creando la notificación")

        return {
            "success": True,
            "mensaje": "Notificación creada correctamente",
            "notificacion_id": notificacion_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en crear_notificacion_admin: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.post("/admin/notificar-estudiante")
def notificar_a_padres_de_estudiante(
    estudiante_id: int,
    titulo: str,
    mensaje: str,
    tipo: str = "general",
    evaluacion_id: Optional[int] = None,
    payload: dict = Depends(admin_required),
    db: Session = Depends(get_db),
):
    """👑 Enviar notificación a todos los padres de un estudiante (Solo Administradores)"""
    try:
        notificaciones_ids = (
            NotificationService.notificar_a_todos_los_padres_del_estudiante(
                db, estudiante_id, titulo, mensaje, tipo, evaluacion_id
            )
        )

        return {
            "success": True,
            "mensaje": f"{len(notificaciones_ids)} notificaciones enviadas",
            "notificaciones_ids": notificaciones_ids,
        }

    except Exception as e:
        logger.error(
            f"Error notificando a padres del estudiante {estudiante_id}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.post("/admin/verificar-evaluacion/{evaluacion_id}")
def verificar_evaluacion_y_notificar(
    evaluacion_id: int,
    umbral: float = Query(
        50.0, ge=0, le=100, description="Umbral mínimo para notificar"
    ),
    payload: dict = Depends(admin_required),
    db: Session = Depends(get_db),
):
    """🔍 Verificar evaluación y notificar si es necesario (Solo Administradores)"""
    try:
        notificaciones = NotificationService.verificar_y_notificar_calificacion_baja(
            db, evaluacion_id, umbral
        )

        return {
            "success": True,
            "mensaje": f"{len(notificaciones)} notificaciones enviadas",
            "notificaciones_ids": notificaciones,
            "umbral_usado": umbral,
        }

    except Exception as e:
        logger.error(f"Error verificando evaluación {evaluacion_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/admin/todas-notificaciones")
def listar_todas_las_notificaciones(
    limit: int = Query(100, ge=1, le=500),
    tipo: Optional[str] = Query(None, description="Filtrar por tipo"),
    padre_id: Optional[int] = Query(None, description="Filtrar por padre"),
    estudiante_id: Optional[int] = Query(None, description="Filtrar por estudiante"),
    payload: dict = Depends(admin_required),
    db: Session = Depends(get_db),
):
    """👑 Ver todas las notificaciones del sistema (Solo Administradores)"""
    try:
        notificaciones = crud_notificacion.obtener_notificaciones_admin(
            db, limit, tipo, padre_id, estudiante_id
        )

        return {"success": True, "data": notificaciones, "total": len(notificaciones)}

    except Exception as e:
        logger.error(f"Error obteniendo todas las notificaciones: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.delete("/admin/limpiar-antiguas")
def limpiar_notificaciones_antiguas(
    dias: int = Query(90, ge=30, le=365, description="Días de antigüedad"),
    payload: dict = Depends(admin_required),
    db: Session = Depends(get_db),
):
    """🧹 Limpiar notificaciones antiguas (Solo Administradores)"""
    try:
        eliminadas = NotificationService.limpiar_notificaciones_antiguas(db, dias)

        return {
            "success": True,
            "mensaje": f"{eliminadas} notificaciones antiguas eliminadas",
            "dias_antiguedad": dias,
        }

    except Exception as e:
        logger.error(f"Error limpiando notificaciones antiguas: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


# ========== ENDPOINTS PARA DOCENTES ==========


@router.post("/docente/notificar-evaluacion/{evaluacion_id}")
def notificar_evaluacion_como_docente(
    evaluacion_id: int,
    forzar_notificacion: bool = Query(
        False, description="Forzar notificación independiente de la nota"
    ),
    payload: dict = Depends(docente_o_admin_required),
    db: Session = Depends(get_db),
):
    """👨‍🏫 Enviar notificación sobre evaluación (Docentes)"""
    try:
        notificaciones = NotificationService.notificar_evaluacion_registrada(
            db, evaluacion_id, not forzar_notificacion
        )

        return {
            "success": True,
            "mensaje": f"{len(notificaciones)} notificaciones enviadas",
            "notificaciones_ids": notificaciones,
        }

    except Exception as e:
        logger.error(f"Error notificando evaluación {evaluacion_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")
