from app.database import SessionLocal
from seeders.seed_cursos import seed_cursos
from seeders.seed_materias import seed_materias
from seeders.seed_curso_materia import seed_curso_materia
from seeders.seed_docentes import seed_docentes
from seeders.seed_docente_materia import seed_docente_materia
from seeders.seed_estudiantes import seed_estudiantes


def run():
    db = SessionLocal()
    # seed_materias(db)
    # seed_docentes(db)
    # seed_gestion(db)
    # seed_cursos(db)
    # seed_curso_materia(db)
    seed_estudiantes(db)
    # seed_docente_materia(db)
    db.close()


if __name__ == "__main__":
    run()
