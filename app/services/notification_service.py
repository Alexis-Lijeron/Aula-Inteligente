# app/services/notification_service.py
from sqlalchemy.orm import Session
from app.crud import notificacion as crud_notificacion
from app.models.padre_estudiante import PadreEstudiante
from app.models.evaluacion import Evaluacion
from app.models.estudiante import Estudiante
from app.models.materia import Materia
from app.models.tipo_evaluacion import TipoEvaluacion
from app.schemas.notificacion import NotificacionCreate
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class NotificationService:

    @staticmethod
    def verificar_y_notificar_calificacion_baja(
        db: Session, evaluacion_id: int, umbral: float = 50.0
    ) -> List[int]:
        """
        Verificar si una evaluación tiene calificación baja (< umbral)
        y notificar a los padres correspondientes

        Args:
            db: Sesión de base de datos
            evaluacion_id: ID de la evaluación a verificar
            umbral: Valor mínimo para considerar calificación baja (default: 50.0)

        Returns:
            Lista de IDs de notificaciones creadas
        """
        try:
            # Obtener la evaluación con toda la información necesaria
            evaluacion = (
                db.query(Evaluacion)
                .join(Estudiante, Evaluacion.estudiante_id == Estudiante.id)
                .join(Materia, Evaluacion.materia_id == Materia.id)
                .join(
                    TipoEvaluacion, Evaluacion.tipo_evaluacion_id == TipoEvaluacion.id
                )
                .filter(Evaluacion.id == evaluacion_id)
                .first()
            )

            if not evaluacion:
                logger.warning(f"Evaluación {evaluacion_id} no encontrada")
                return []

            # Verificar si la calificación es menor al umbral
            if evaluacion.valor >= umbral:
                logger.info(
                    f"Evaluación {evaluacion_id} tiene valor {evaluacion.valor} >= {umbral}, no se envía notificación"
                )
                return []

            # Encontrar todos los padres del estudiante
            padres = (
                db.query(PadreEstudiante.padre_id)
                .filter(PadreEstudiante.estudiante_id == evaluacion.estudiante_id)
                .all()
            )

            if not padres:
                logger.warning(
                    f"No se encontraron padres para el estudiante {evaluacion.estudiante_id}"
                )
                return []

            notificaciones_creadas = []

            for padre_relacion in padres:
                padre_id = padre_relacion.padre_id

                # Verificar si ya existe una notificación para esta evaluación y padre
                notificacion_existente = (
                    db.query(crud_notificacion.Notificacion)
                    .filter(
                        crud_notificacion.Notificacion.padre_id == padre_id,
                        crud_notificacion.Notificacion.evaluacion_id == evaluacion_id,
                        crud_notificacion.Notificacion.tipo == "calificacion_baja",
                    )
                    .first()
                )

                if notificacion_existente:
                    logger.info(
                        f"Ya existe notificación para padre {padre_id} y evaluación {evaluacion_id}"
                    )
                    continue

                # Crear notificación personalizada
                titulo = f"⚠️ Calificación Baja - {evaluacion.estudiante.nombre}"
                mensaje = (
                    f"Su hijo(a) {evaluacion.estudiante.nombre} {evaluacion.estudiante.apellido} "
                    f"obtuvo {evaluacion.valor} puntos en {evaluacion.descripcion} "
                    f"de la materia {evaluacion.materia.nombre}. "
                    f"Le recomendamos estar atento al rendimiento académico."
                )

                notificacion_data = NotificacionCreate(
                    titulo=titulo,
                    mensaje=mensaje,
                    tipo="calificacion_baja",
                    padre_id=padre_id,
                    estudiante_id=evaluacion.estudiante_id,
                    evaluacion_id=evaluacion.id,
                )

                try:
                    notificacion = crud_notificacion.crear_notificacion(
                        db, notificacion_data
                    )
                    notificaciones_creadas.append(notificacion.id)
                    logger.info(
                        f"Notificación creada para padre {padre_id} sobre evaluación {evaluacion_id}"
                    )
                except Exception as e:
                    logger.error(
                        f"Error creando notificación para padre {padre_id}: {str(e)}"
                    )

            return notificaciones_creadas

        except Exception as e:
            logger.error(f"Error en verificar_y_notificar_calificacion_baja: {str(e)}")
            return []

    @staticmethod
    def notificar_evaluacion_registrada(
        db: Session,
        evaluacion_id: int,
        solo_calificaciones_bajas: bool = True,
        umbral: float = 50.0,
    ) -> List[int]:
        """
        Notificar sobre una evaluación registrada.

        Args:
            db: Sesión de base de datos
            evaluacion_id: ID de la evaluación
            solo_calificaciones_bajas: Si True, solo notifica si el valor < umbral
            umbral: Valor mínimo para considerar calificación baja

        Returns:
            Lista de IDs de notificaciones creadas
        """
        if solo_calificaciones_bajas:
            return NotificationService.verificar_y_notificar_calificacion_baja(
                db, evaluacion_id, umbral
            )

        # Lógica para notificar todas las evaluaciones (si se necesita en el futuro)
        try:
            evaluacion = (
                db.query(Evaluacion).filter(Evaluacion.id == evaluacion_id).first()
            )
            if not evaluacion:
                return []

            padres = (
                db.query(PadreEstudiante.padre_id)
                .filter(PadreEstudiante.estudiante_id == evaluacion.estudiante_id)
                .all()
            )

            notificaciones_creadas = []

            for padre_relacion in padres:
                padre_id = padre_relacion.padre_id

                titulo = f"📝 Nueva Evaluación - {evaluacion.estudiante.nombre}"
                mensaje = (
                    f"Su hijo(a) {evaluacion.estudiante.nombre} {evaluacion.estudiante.apellido} "
                    f"recibió una calificación de {evaluacion.valor} puntos en {evaluacion.descripcion}."
                )

                notificacion_data = NotificacionCreate(
                    titulo=titulo,
                    mensaje=mensaje,
                    tipo="evaluacion",
                    padre_id=padre_id,
                    estudiante_id=evaluacion.estudiante_id,
                    evaluacion_id=evaluacion.id,
                )

                try:
                    notificacion = crud_notificacion.crear_notificacion(
                        db, notificacion_data
                    )
                    notificaciones_creadas.append(notificacion.id)
                except Exception as e:
                    logger.error(
                        f"Error creando notificación para padre {padre_id}: {str(e)}"
                    )

            return notificaciones_creadas

        except Exception as e:
            logger.error(f"Error en notificar_evaluacion_registrada: {str(e)}")
            return []

    @staticmethod
    def crear_notificacion_personalizada(
        db: Session,
        padre_id: int,
        estudiante_id: int,
        titulo: str,
        mensaje: str,
        tipo: str = "general",
        evaluacion_id: Optional[int] = None,
    ) -> Optional[int]:
        """
        Crear una notificación personalizada

        Args:
            db: Sesión de base de datos
            padre_id: ID del padre
            estudiante_id: ID del estudiante
            titulo: Título de la notificación
            mensaje: Mensaje de la notificación
            tipo: Tipo de notificación
            evaluacion_id: ID de evaluación (opcional)

        Returns:
            ID de la notificación creada o None si hay error
        """
        try:
            notificacion_data = NotificacionCreate(
                titulo=titulo,
                mensaje=mensaje,
                tipo=tipo,
                padre_id=padre_id,
                estudiante_id=estudiante_id,
                evaluacion_id=evaluacion_id,
            )

            notificacion = crud_notificacion.crear_notificacion(db, notificacion_data)
            logger.info(f"Notificación personalizada creada: {notificacion.id}")
            return notificacion.id

        except Exception as e:
            logger.error(f"Error creando notificación personalizada: {str(e)}")
            return None

    @staticmethod
    def notificar_a_todos_los_padres_del_estudiante(
        db: Session,
        estudiante_id: int,
        titulo: str,
        mensaje: str,
        tipo: str = "general",
        evaluacion_id: Optional[int] = None,
    ) -> List[int]:
        """
        Enviar notificación a todos los padres de un estudiante

        Args:
            db: Sesión de base de datos
            estudiante_id: ID del estudiante
            titulo: Título de la notificación
            mensaje: Mensaje de la notificación
            tipo: Tipo de notificación
            evaluacion_id: ID de evaluación (opcional)

        Returns:
            Lista de IDs de notificaciones creadas
        """
        try:
            padres = (
                db.query(PadreEstudiante.padre_id)
                .filter(PadreEstudiante.estudiante_id == estudiante_id)
                .all()
            )

            notificaciones_creadas = []

            for padre_relacion in padres:
                padre_id = padre_relacion.padre_id

                notificacion_id = NotificationService.crear_notificacion_personalizada(
                    db, padre_id, estudiante_id, titulo, mensaje, tipo, evaluacion_id
                )

                if notificacion_id:
                    notificaciones_creadas.append(notificacion_id)

            return notificaciones_creadas

        except Exception as e:
            logger.error(
                f"Error notificando a padres del estudiante {estudiante_id}: {str(e)}"
            )
            return []

    @staticmethod
    def limpiar_notificaciones_antiguas(db: Session, dias_antiguedad: int = 90) -> int:
        """
        Eliminar notificaciones antiguas (opcional, para mantenimiento)

        Args:
            db: Sesión de base de datos
            dias_antiguedad: Días de antigüedad para considerar eliminar

        Returns:
            Número de notificaciones eliminadas
        """
        try:
            from datetime import datetime, timedelta

            fecha_limite = datetime.now() - timedelta(days=dias_antiguedad)

            # Solo eliminar notificaciones leídas y antiguas
            eliminadas = (
                db.query(crud_notificacion.Notificacion)
                .filter(
                    crud_notificacion.Notificacion.leida == True,
                    crud_notificacion.Notificacion.created_at < fecha_limite,
                )
                .delete()
            )

            db.commit()
            logger.info(f"Eliminadas {eliminadas} notificaciones antiguas")
            return eliminadas

        except Exception as e:
            logger.error(f"Error limpiando notificaciones antiguas: {str(e)}")
            return 0
