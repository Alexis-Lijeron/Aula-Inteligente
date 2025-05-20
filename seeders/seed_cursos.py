from sqlalchemy.orm import Session
from app.models.curso import Curso


def seed_cursos(db: Session):
    niveles_y_grados = {
        "Inicial": ["Prekinder", "Kinder"],
        "Primaria": [f"{i}° Primaria" for i in range(1, 7)],
        "Secundaria": [f"{i}° Secundaria" for i in range(1, 7)],
    }

    turnos = ["Mañana", "Tarde", "Noche"]
    paralelos = ["A", "B"]

    for nivel, grados in niveles_y_grados.items():
        for grado in grados:
            for turno in turnos:
                for paralelo in paralelos:
                    nombre = f"{grado} {paralelo} - {turno}"
                    existe = db.query(Curso).filter_by(nombre=nombre).first()
                    if not existe:
                        db.add(
                            Curso(
                                nombre=nombre,
                                nivel=nivel,
                                paralelo=paralelo,
                                turno=turno,
                            )
                        )
    db.commit()
    print("✅ Curso seed completado.")