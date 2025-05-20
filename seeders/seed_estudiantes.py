from sqlalchemy.orm import Session
from app.models.estudiante import Estudiante
from app.models.curso import Curso
import random
from datetime import date, timedelta

nombres_masculinos = [
    "Carlos",
    "Juan",
    "Luis",
    "Marco",
    "Pedro",
    "José",
    "Hugo",
    "Edgar",
    "Jorge",
    "Mauricio",
    "Diego",
    "Sebastián",
    "Ramiro",
    "Raúl",
    "Nicolás",
    "Alberto",
    "Fernando",
    "Iván",
    "Gonzalo",
    "Ricardo",
]

nombres_femeninos = [
    "Ana",
    "María",
    "Paola",
    "Lucía",
    "Gabriela",
    "Daniela",
    "Valeria",
    "Roxana",
    "Sandra",
    "Camila",
    "Verónica",
    "Patricia",
    "Karen",
    "Mariela",
    "Julieta",
    "Estefanía",
    "Lorena",
    "Carla",
    "Bianca",
    "Mónica",
]

apellidos = [
    "Quispe",
    "Mamani",
    "Condori",
    "Choque",
    "Rojas",
    "Guzmán",
    "Salvatierra",
    "Rivera",
    "Alarcón",
    "Vargas",
    "Sánchez",
    "Flores",
    "Paredes",
    "Céspedes",
    "Ortíz",
    "Castro",
    "Navarro",
    "Cabrera",
    "Medina",
    "Aguilera",
]


def generar_fecha_nacimiento(nivel):
    edad_base = {
        "Inicial": (4, 5),
        "Primaria": (6, 12),
        "Secundaria": (13, 17),
    }
    min_edad, max_edad = edad_base.get(nivel, (6, 12))
    edad = random.randint(min_edad, max_edad)
    nacimiento = date.today() - timedelta(days=edad * 365 + random.randint(0, 300))
    return nacimiento


def generar_nombre_tutor(tutores_usados: dict):
    intentos = 0
    while True:
        nombre = random.choice(nombres_masculinos + nombres_femeninos)
        apellido = random.choice(apellidos)
        base = f"{nombre} {apellido}"
        cantidad_usos = tutores_usados.get(base, 0)

        if cantidad_usos < 3:
            tutor = base if cantidad_usos == 0 else f"{base} {cantidad_usos + 1}"
            tutores_usados[base] = cantidad_usos + 1
            return tutor
        else:
            # 💡 crear tutor artificialmente único si ya se repitió 3 veces
            tutor = f"{base} Extra{random.randint(100, 999)}"
            if tutor not in tutores_usados:
                tutores_usados[tutor] = 1
                return tutor

        intentos += 1
        if intentos > 5000:
            raise Exception("❌ No se pudo generar tutor único ni con sufijos")


def generar_telefono(ya_usados):
    while True:
        telefono = f"7{random.randint(1000000, 9999999)}"
        if telefono not in ya_usados:
            ya_usados.add(telefono)
            return telefono


def generar_direccion(ya_usados):
    while True:
        direccion = f"Calle {random.randint(1, 200)}, Zona {random.choice(apellidos)}"
        if direccion not in ya_usados:
            ya_usados.add(direccion)
            return direccion


def seed_estudiantes(db: Session):
    cursos = db.query(Curso).all()
    total_insertados = 0

    tutores_usados = {}
    telefonos_usados = set()
    direcciones_usadas = set()

    for curso in cursos:
        for _ in range(30):  # 30 estudiantes por curso
            genero = random.choice(["Masculino", "Femenino"])
            nombre = random.choice(
                nombres_masculinos if genero == "Masculino" else nombres_femeninos
            )
            apellido = random.choice(apellidos)
            fecha_nacimiento = generar_fecha_nacimiento(curso.nivel)
            tutor = generar_nombre_tutor(tutores_usados)
            telefono_tutor = generar_telefono(telefonos_usados)
            direccion = generar_direccion(direcciones_usadas)

            estudiante = Estudiante(
                nombre=nombre,
                apellido=apellido,
                fecha_nacimiento=fecha_nacimiento,
                genero=genero,
                url_imagen="",
                nombre_tutor=tutor,
                telefono_tutor=telefono_tutor,
                direccion_casa=direccion,
            )

            db.add(estudiante)
            total_insertados += 1

    db.commit()
    print(
        f"✅ Se insertaron {total_insertados} estudiantes (30 por curso sin repetir tutor, teléfono ni dirección)."
    )
