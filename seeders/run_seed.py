from app.database import SessionLocal
from seeders.seed_cursos import seed_cursos
from seeders.seed_materias import seed_materias

def run():
    db = SessionLocal()
    seed_materias(db)
    #seed_docentes(db)
    #seed_gestion(db)
    seed_cursos(db)
    #seed_curso_materia(db)
    # seed_estudiantes(db)
    db.close()


if __name__ == "__main__":
    run()
