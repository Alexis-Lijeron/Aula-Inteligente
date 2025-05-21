from sqlalchemy.orm import Session
from app.models.tipo_evaluacion import TipoEvaluacion


def seed_tipo_evaluacion(db: Session):
    tipos = [
        "Exámenes",
        "Tareas",
        "Exposiciones",
        "Participaciones",
        "Asistencia",
        "Prácticas",
        "Proyecto final",
        "Trabajo grupal",
        "Ensayos",
        "Cuestionarios",
    ]

    for nombre in tipos:
        existe = (
            db.query(TipoEvaluacion).filter(TipoEvaluacion.nombre == nombre).first()
        )
        if not existe:
            nuevo = TipoEvaluacion(nombre=nombre)
            db.add(nuevo)

    db.commit()
    print("✔️ Tipos de evaluación insertados correctamente.")
