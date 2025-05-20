from sqlalchemy.orm import Session
from app.models.docente import Docente
from app.models.materia import Materia
from app.models.docente_materia import DocenteMateria


def seed_docente_materia(db: Session):
    materias = db.query(Materia).all()
    docentes = db.query(Docente).filter_by(is_doc=True).all()

    if len(docentes) < len(materias):
        print("❌ No hay suficientes docentes para asignar una materia a cada uno.")
        return

    asignaciones = []
    usados = set()

    for i, materia in enumerate(materias):
        docente = docentes[i]

        ya_existe = (
            db.query(DocenteMateria)
            .filter_by(docente_id=docente.id, materia_id=materia.id)
            .first()
        )

        if not ya_existe:
            asignaciones.append(
                DocenteMateria(docente_id=docente.id, materia_id=materia.id)
            )
            usados.add(docente.id)

    db.bulk_save_objects(asignaciones)
    db.commit()
    print(f"✅ Se asignaron {len(asignaciones)} materias a docentes.")
