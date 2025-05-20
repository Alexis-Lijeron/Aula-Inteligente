from sqlalchemy.orm import Session
from app.models.estudiante import Estudiante
from app.models.curso import Curso
from app.models.gestion import Gestion
from app.models.inscripcion import Inscripcion
from datetime import date


def seed_inscripciones(db: Session):
    estudiantes = db.query(Estudiante).order_by(Estudiante.id).all()
    cursos = db.query(Curso).order_by(Curso.id).all()
    gestion = db.query(Gestion).filter_by(anio="2025").first()

    if not gestion:
        raise Exception(
            "❌ Gestión 2025 no encontrada. Asegúrate de ejecutar seed_gestion."
        )

    total_esperado = len(cursos) * 30
    if len(estudiantes) < total_esperado:
        raise Exception(
            f"❌ Se esperaban al menos {total_esperado} estudiantes para 30 por curso."
        )

    inscripciones = []
    fecha_actual = date.today()
    idx = 0

    for curso in cursos:
        for _ in range(30):
            estudiante = estudiantes[idx]
            inscripciones.append(
                Inscripcion(
                    descripcion="Inscripción automática 2025",
                    fecha=fecha_actual,
                    estudiante_id=estudiante.id,
                    curso_id=curso.id,
                    gestion_id=gestion.id,
                )
            )
            idx += 1

    db.bulk_save_objects(inscripciones)
    db.commit()
    print(f"✅ Se generaron {len(inscripciones)} inscripciones para gestión 2025.")
