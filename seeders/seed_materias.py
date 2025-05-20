from sqlalchemy.orm import Session
from app.models.materia import Materia


def seed_materias(db: Session):
    materias = [
        # Inicial
        {
            "nombre": "Desarrollo Personal y Social",
            "descripcion": "Fortalece la identidad y el desarrollo emocional en la infancia",
        },
        {
            "nombre": "Comunicación Oral (en Lengua Castellana)",
            "descripcion": "Estimula la comprensión y expresión verbal del niño",
        },
        {
            "nombre": "Lenguaje Artístico y Corporal",
            "descripcion": "Favorece la expresión a través del arte, el cuerpo y el juego",
        },
        {
            "nombre": "Exploración del Entorno",
            "descripcion": "Permite la observación, exploración y comprensión del entorno natural y social",
        },
        {
            "nombre": "Motricidad Global y Fina",
            "descripcion": "Desarrolla coordinación de movimientos amplios y precisos",
        },
        {
            "nombre": "Valores y Espiritualidad",
            "descripcion": "Fomenta el respeto, la empatía y la diversidad espiritual desde pequeños",
        },
        # Primaria
        {
            "nombre": "Cosmos y Pensamiento",
            "descripcion": "Promueve la reflexión filosófica sobre el universo y la vida",
        },
        {
            "nombre": "Valores, Espiritualidades y Religiones",
            "descripcion": "Aborda la diversidad de creencias y valores éticos",
        },
        {
            "nombre": "Comunidad y Sociedad",
            "descripcion": "Explora la vida en comunidad, cultura y participación social",
        },
        {
            "nombre": "Comunicación y Lenguajes",
            "descripcion": "Desarrolla comprensión lectora, oralidad y redacción",
        },
        {
            "nombre": "Artes Plásticas y Visuales",
            "descripcion": "Fomenta la creatividad a través del arte visual y plástico",
        },
        {
            "nombre": "Educación Musical",
            "descripcion": "Desarrolla el ritmo, el canto y la apreciación musical",
        },
        {
            "nombre": "Educación Física y Deportes",
            "descripcion": "Fortalece la salud, la coordinación y el trabajo en equipo",
        },
        {
            "nombre": "Ciencias Sociales",
            "descripcion": "Comprende la historia, geografía y realidad social",
        },
        {
            "nombre": "Vida, Tierra, Territorio",
            "descripcion": "Fortalece la conciencia medioambiental y territorial",
        },
        {
            "nombre": "Ciencias Naturales",
            "descripcion": "Estudia fenómenos naturales, el cuerpo humano y los seres vivos",
        },
        {
            "nombre": "Ciencia, Tecnología y Producción",
            "descripcion": "Vincula el conocimiento con la producción contextualizada",
        },
        {
            "nombre": "Matemática",
            "descripcion": "Aplica conceptos de lógica, aritmética, geometría y resolución de problemas",
        },
        {
            "nombre": "Técnica Tecnológica",
            "descripcion": "Introduce procesos técnicos útiles en la vida cotidiana",
        },
        # Secundaria
        {
            "nombre": "Ciencias Naturales: Biología – Geografía",
            "descripcion": "Explora el cuerpo humano, seres vivos y el entorno geográfico",
        },
        {
            "nombre": "Ciencias Naturales: Física",
            "descripcion": "Estudia el movimiento, la energía y las leyes físicas",
        },
        {
            "nombre": "Ciencias Naturales: Química",
            "descripcion": "Analiza la materia, sus propiedades y transformaciones",
        },
        {
            "nombre": "Matemática Avanzada",
            "descripcion": "Refuerza lógica, álgebra, geometría, estadística y resolución de problemas",
        },
        {
            "nombre": "Técnica Tecnológica General",
            "descripcion": "Aplica procesos técnicos y tecnológicos en contextos productivos",
        },
        {
            "nombre": "Comunicación y Lenguajes: Lengua Castellana",
            "descripcion": "Perfecciona expresión oral y escrita en lengua oficial",
        },
        {
            "nombre": "Comunicación y Lenguajes: Lengua Originaria",
            "descripcion": "Preserva y promueve el uso de idiomas ancestrales",
        },
        {
            "nombre": "Lengua Extranjera",
            "descripcion": "Desarrolla habilidades comunicativas en inglés u otro idioma",
        },
        {
            "nombre": "Ciencias Sociales Avanzadas",
            "descripcion": "Analiza procesos históricos, económicos, políticos y culturales",
        },
        {
            "nombre": "Artes Plásticas y Visuales Avanzadas",
            "descripcion": "Profundiza en técnicas y apreciación de arte visual",
        },
        {
            "nombre": "Educación Musical Avanzada",
            "descripcion": "Desarrolla expresión musical y uso de instrumentos",
        },
        {
            "nombre": "Educación Física y Deportes Avanzada",
            "descripcion": "Consolida salud, trabajo en equipo y competencia deportiva",
        },
        {
            "nombre": "Cosmovisiones, Filosofía y Sociología",
            "descripcion": "Promueve el pensamiento crítico, ético y social",
        },
        {
            "nombre": "Valores, Espiritualidad y Religiones",
            "descripcion": "Profundiza en valores universales y espiritualidad intercultural",
        },
    ]

    for mat in materias:
        existe = db.query(Materia).filter_by(nombre=mat["nombre"]).first()
        if not existe:
            db.add(Materia(**mat))
    db.commit()
    print("✅ Materia seed completado.")