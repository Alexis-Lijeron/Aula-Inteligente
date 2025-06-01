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
from datetime import timedelta
import random


def seed_evaluaciones(db: Session, periodo_id: int):
    periodo = db.query(Periodo).filter_by(id=periodo_id).first()
    if not periodo:
        print(f"❌ No se encontró el periodo con id {periodo_id}")
        return

    print(f"🟡 Generando evaluaciones para el periodo: {periodo.nombre}")

    estudiantes = db.query(Estudiante).all()
    inscripciones = db.query(Inscripcion).all()
    cursomaterias = db.query(CursoMateria).all()
    tipos = db.query(TipoEvaluacion).all()

    tipo_dict = {t.nombre.lower(): t.id for t in tipos}
    fechas = [
        periodo.fecha_inicio + timedelta(days=i)
        for i in range((periodo.fecha_fin - periodo.fecha_inicio).days + 1)
    ]
    fechas = fechas[::3]
    evaluaciones_batch = []
    contador = 0

    for insc in inscripciones:
        curso_id = insc.curso_id
        estudiante_id = insc.estudiante_id

        materias_ids = [
            cm.materia_id for cm in cursomaterias if cm.curso_id == curso_id
        ]

        for materia_id in materias_ids:
            estudiante = db.query(Estudiante).get(estudiante_id)
            print(
                f"🔷 {estudiante.nombre} {estudiante.apellido} - Materia {materia_id}"
            )

            for f in fechas:
                evaluaciones_batch.extend(
                    [
                        Evaluacion(
                            fecha=f,
                            descripcion="Asistencia",
                            valor=random.choice([100, 50, 0]),
                            estudiante_id=estudiante_id,
                            materia_id=materia_id,
                            tipo_evaluacion_id=tipo_dict["asistencia"],
                            periodo_id=periodo.id,
                        ),
                        Evaluacion(
                            fecha=f,
                            descripcion="Participación en clase",
                            valor=round(random.uniform(0, 100), 2),
                            estudiante_id=estudiante_id,
                            materia_id=materia_id,
                            tipo_evaluacion_id=tipo_dict["participaciones"],
                            periodo_id=periodo.id,
                        ),
                        Evaluacion(
                            fecha=f,
                            descripcion="Tarea del día",
                            valor=round(random.uniform(50, 100), 2),
                            estudiante_id=estudiante_id,
                            materia_id=materia_id,
                            tipo_evaluacion_id=tipo_dict["tareas"],
                            periodo_id=periodo.id,
                        ),
                    ]
                )

                if (f - periodo.fecha_inicio).days % 2 == 0:
                    evaluaciones_batch.append(
                        Evaluacion(
                            fecha=f,
                            descripcion="Práctica",
                            valor=round(random.uniform(0, 100), 2),
                            estudiante_id=estudiante_id,
                            materia_id=materia_id,
                            tipo_evaluacion_id=tipo_dict["prácticas"],
                            periodo_id=periodo.id,
                        )
                    )

                if f.weekday() == 0:
                    evaluaciones_batch.extend(
                        [
                            Evaluacion(
                                fecha=f,
                                descripcion="Exposición",
                                valor=round(random.uniform(60, 100), 2),
                                estudiante_id=estudiante_id,
                                materia_id=materia_id,
                                tipo_evaluacion_id=tipo_dict["exposiciones"],
                                periodo_id=periodo.id,
                            ),
                            Evaluacion(
                                fecha=f,
                                descripcion="Ensayo",
                                valor=round(random.uniform(20, 100), 2),
                                estudiante_id=estudiante_id,
                                materia_id=materia_id,
                                tipo_evaluacion_id=tipo_dict["ensayos"],
                                periodo_id=periodo.id,
                            ),
                            Evaluacion(
                                fecha=f,
                                descripcion="Cuestionario",
                                valor=round(random.uniform(0, 100), 2),
                                estudiante_id=estudiante_id,
                                materia_id=materia_id,
                                tipo_evaluacion_id=tipo_dict["cuestionarios"],
                                periodo_id=periodo.id,
                            ),
                            Evaluacion(
                                fecha=f,
                                descripcion="Trabajo grupal",
                                valor=round(random.uniform(60, 100), 2),
                                estudiante_id=estudiante_id,
                                materia_id=materia_id,
                                tipo_evaluacion_id=tipo_dict["trabajo grupal"],
                                periodo_id=periodo.id,
                            ),
                        ]
                    )

                if f.day in [15, 30] or (f.day == 28 and f.month == 2):
                    evaluaciones_batch.append(
                        Evaluacion(
                            fecha=f,
                            descripcion="Examen parcial",
                            valor=round(random.uniform(0, 100), 2),
                            estudiante_id=estudiante_id,
                            materia_id=materia_id,
                            tipo_evaluacion_id=tipo_dict["exámenes"],
                            periodo_id=periodo.id,
                        )
                    )

                if (periodo.fecha_fin - f).days < 5:
                    evaluaciones_batch.append(
                        Evaluacion(
                            fecha=f,
                            descripcion="Proyecto final",
                            valor=round(random.uniform(60, 100), 2),
                            estudiante_id=estudiante_id,
                            materia_id=materia_id,
                            tipo_evaluacion_id=tipo_dict["proyecto final"],
                            periodo_id=periodo.id,
                        )
                    )

                contador += 1
                if contador % 500 == 0:
                    db.add_all(evaluaciones_batch)
                    db.commit()
                    print(f"💾 Guardadas {contador} evaluaciones...")
                    evaluaciones_batch.clear()

    if evaluaciones_batch:
        db.add_all(evaluaciones_batch)
        db.commit()
        print(f"✅ Guardadas las últimas {len(evaluaciones_batch)} evaluaciones.")

    print(f"🎉 Evaluaciones completadas para el periodo: {periodo.nombre}")
