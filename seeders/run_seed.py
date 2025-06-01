from app.database import SessionLocal
from seeders.seed_cursos import seed_cursos
from seeders.seed_materias import seed_materias
from seeders.seed_curso_materia import seed_curso_materia
from seeders.seed_docentes import seed_docentes
from seeders.seed_docente_materia import seed_docente_materia
from seeders.seed_estudiantes import seed_estudiantes
from seeders.seed_inscripciones import seed_inscripciones
from seeders.seed_gestion import seed_gestion
from seeders.seed_periodos import seed_periodos
from seeders.seed_tipo_evaluacion import seed_tipo_evaluacion
from seeders.seed_evaluaciones_completo import seed_evaluaciones
from seeders.seed_peso_tipo_evaluacion import seed_peso_tipo_evaluacion


def run():
    db = SessionLocal()
    # seed_gestion(db)
    # seed_materias(db)
    # seed_cursos(db)
    # seed_curso_materia(db)
    # seed_docentes(db)
    # seed_docente_materia(db)
    # seed_estudiantes(db)
    # seed_inscripciones(db)
    # seed_periodos(db)
    # seed_tipo_evaluacion(db)
    # seed_peso_tipo_evaluacion(db)
    periodo_id = 3
    seed_evaluaciones(db, periodo_id)
    print("✅ Todos los datos de prueba se han insertado correctamente.")
    db.close()


if __name__ == "__main__":
    run()
