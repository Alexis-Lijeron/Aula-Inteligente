from sqlalchemy.orm import Session
from app.models.curso import Curso
from app.models.materia import Materia
from app.models.curso_materia import CursoMateria


def seed_curso_materia(db: Session):
    # Agrupación de materias por nivel
    materias_inicial = [
        "Desarrollo Personal y Social",
        "Comunicación Oral (en Lengua Castellana)",
        "Lenguaje Artístico y Corporal",
        "Exploración del Entorno",
        "Motricidad Global y Fina",
        "Valores y Espiritualidad",
    ]

    materias_primaria = [
        "Cosmos y Pensamiento",
        "Valores, Espiritualidades y Religiones",
        "Comunidad y Sociedad",
        "Comunicación y Lenguajes",
        "Artes Plásticas y Visuales",
        "Educación Musical",
        "Educación Física y Deportes",
        "Ciencias Sociales",
        "Vida, Tierra, Territorio",
        "Ciencias Naturales",
        "Ciencia, Tecnología y Producción",
        "Matemática",
        "Técnica Tecnológica",
    ]

    materias_secundaria = [
        "Ciencias Naturales: Biología – Geografía",
        "Ciencias Naturales: Física",
        "Ciencias Naturales: Química",
        "Matemática Avanzada",
        "Técnica Tecnológica General",
        "Comunicación y Lenguajes: Lengua Castellana",
        "Comunicación y Lenguajes: Lengua Originaria",
        "Lengua Extranjera",
        "Ciencias Sociales Avanzadas",
        "Artes Plásticas y Visuales Avanzadas",
        "Educación Musical Avanzada",
        "Educación Física y Deportes Avanzada",
        "Cosmovisiones, Filosofía y Sociología",
        "Valores, Espiritualidad y Religiones",
    ]

    # Obtener todas las materias desde la BD una sola vez
    materias_db = {m.nombre: m.id for m in db.query(Materia).all()}

    cursos = db.query(Curso).all()
    for curso in cursos:
        if curso.nivel == "Inicial":
            materias = materias_inicial
        elif curso.nivel == "Primaria":
            materias = materias_primaria
        elif curso.nivel == "Secundaria":
            materias = materias_secundaria
        else:
            continue  # nivel desconocido

        for nombre_materia in materias:
            materia_id = materias_db.get(nombre_materia)
            if not materia_id:
                print(f"[❗] Materia no encontrada: {nombre_materia}")
                continue

            ya_asignado = (
                db.query(CursoMateria)
                .filter_by(curso_id=curso.id, materia_id=materia_id)
                .first()
            )
            if not ya_asignado:
                db.add(CursoMateria(curso_id=curso.id, materia_id=materia_id))

    db.commit()
    print("✅ CursoMateria seed completado.")
