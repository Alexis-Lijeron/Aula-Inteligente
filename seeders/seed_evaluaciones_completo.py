from sqlalchemy.orm import Session
from app.models import (
    Estudiante,
    Curso,
    CursoMateria,
    Inscripcion,
    DocenteMateria,
    Periodo,
    TipoEvaluacion,
    Evaluacion,
)
from datetime import timedelta, date
import random


def seed_evaluaciones(db: Session):
    estudiantes = db.query(Estudiante).all()
    cursos = db.query(Curso).all()
    inscripciones = db.query(Inscripcion).all()
    cursomaterias = db.query(CursoMateria).all()
    docentematerias = db.query(DocenteMateria).all()
    periodos = db.query(Periodo).all()
    tipos = db.query(TipoEvaluacion).all()

    tipo_dict = {t.nombre.lower(): t.id for t in tipos}

    for periodo in periodos:
        dias_periodo = (periodo.fecha_fin - periodo.fecha_inicio).days + 1
        fechas = [periodo.fecha_inicio + timedelta(days=i) for i in range(dias_periodo)]

        for insc in inscripciones:
            curso_id = insc.curso_id
            estudiante_id = insc.estudiante_id

            # Buscar materias del curso
            materias_ids = [
                cm.materia_id for cm in cursomaterias if cm.curso_id == curso_id
            ]

            for materia_id in materias_ids:
                for f in fechas:
                    # Asistencia (cada día)
                    asistencia_valor = random.choice([100, 50, 0])
                    db.add(
                        Evaluacion(
                            fecha=f,
                            descripcion="Asistencia",
                            valor=asistencia_valor,
                            estudiante_id=estudiante_id,
                            materia_id=materia_id,
                            tipo_evaluacion_id=tipo_dict["asistencia"],
                            periodo_id=periodo.id,
                        )
                    )

                    # Participación (cada día)
                    participacion_valor = random.uniform(0, 100)
                    db.add(
                        Evaluacion(
                            fecha=f,
                            descripcion="Participación en clase",
                            valor=round(participacion_valor, 2),
                            estudiante_id=estudiante_id,
                            materia_id=materia_id,
                            tipo_evaluacion_id=tipo_dict["participaciones"],
                            periodo_id=periodo.id,  
                        )
                    )

                    # Tarea (cada día)
                    tarea_valor = random.uniform(50, 100)
                    db.add(
                        Evaluacion(
                            fecha=f,
                            descripcion="Tarea del día",
                            valor=round(tarea_valor, 2),
                            estudiante_id=estudiante_id,
                            materia_id=materia_id,
                            tipo_evaluacion_id=tipo_dict["tareas"],
                            periodo_id=periodo.id,
                        )
                    )

                    # Práctica (cada 2 días)
                    if (f - periodo.fecha_inicio).days % 2 == 0:
                        practica_valor = random.uniform(0, 100)
                        db.add(
                            Evaluacion(
                                fecha=f,
                                descripcion="Práctica",
                                valor=round(practica_valor, 2),
                                estudiante_id=estudiante_id,
                                materia_id=materia_id,
                                tipo_evaluacion_id=tipo_dict["prácticas"],
                                periodo_id=periodo.id,
                            )
                        )

                    # Exposición (cada semana)
                    if f.weekday() == 0:
                        expos_valor = random.uniform(60, 100)
                        db.add(
                            Evaluacion(
                                fecha=f,
                                descripcion="Exposición",
                                valor=round(expos_valor, 2),
                                estudiante_id=estudiante_id,
                                materia_id=materia_id,
                                tipo_evaluacion_id=tipo_dict["exposiciones"],
                                periodo_id=periodo.id,
                            )
                        )

                        ensayo_valor = random.uniform(20, 100)
                        db.add(
                            Evaluacion(
                                fecha=f,
                                descripcion="Ensayo",
                                valor=round(ensayo_valor, 2),
                                estudiante_id=estudiante_id,
                                materia_id=materia_id,
                                tipo_evaluacion_id=tipo_dict["ensayos"],
                                periodo_id=periodo.id,
                            )
                        )

                        cuestionario_valor = random.uniform(0, 100)
                        db.add(
                            Evaluacion(
                                fecha=f,
                                descripcion="Cuestionario",
                                valor=round(cuestionario_valor, 2),
                                estudiante_id=estudiante_id,
                                materia_id=materia_id,
                                tipo_evaluacion_id=tipo_dict["cuestionarios"],
                                periodo_id=periodo.id,
                            )
                        )

                        grupal_valor = random.uniform(60, 100)
                        db.add(
                            Evaluacion(
                                fecha=f,
                                descripcion="Trabajo grupal",
                                valor=round(grupal_valor, 2),
                                estudiante_id=estudiante_id,
                                materia_id=materia_id,
                                tipo_evaluacion_id=tipo_dict["trabajo grupal"],
                                periodo_id=periodo.id,
                            )
                        )

                    # Examen (2 veces al mes)
                    if f.day in [15, 30] or (f.day == 28 and f.month == 2):
                        examen_valor = random.uniform(0, 100)
                        db.add(
                            Evaluacion(
                                fecha=f,
                                descripcion="Examen parcial",
                                valor=round(examen_valor, 2),
                                estudiante_id=estudiante_id,
                                materia_id=materia_id,
                                tipo_evaluacion_id=tipo_dict["exámenes"],
                                periodo_id=periodo.id,
                            )
                        )

                    # Proyecto final (últimos 5 días del periodo)
                    if (periodo.fecha_fin - f).days < 5:
                        proyecto_valor = random.uniform(60, 100)
                        db.add(
                            Evaluacion(
                                fecha=f,
                                descripcion="Proyecto final",
                                valor=round(proyecto_valor, 2),
                                estudiante_id=estudiante_id,
                                materia_id=materia_id,
                                tipo_evaluacion_id=tipo_dict["proyecto final"],
                                periodo_id=periodo.id,
                            )
                        )

    db.commit()
