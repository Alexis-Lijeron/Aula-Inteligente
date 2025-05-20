from sqlalchemy.orm import Session
from app.models.docente import Docente
from app.models.materia import Materia
import random
import unicodedata
from app.seguridad import hash_contrasena

nombres_hombre = [
    "Carlos",
    "Juan",
    "Luis",
    "José",
    "Andrés",
    "Mario",
    "Hugo",
    "Edgar",
    "Jorge",
    "Mauricio",
]

nombres_mujer = [
    "Ana",
    "María",
    "Carla",
    "Paola",
    "Fernanda",
    "Lucía",
    "Gabriela",
    "Valeria",
    "Daniela",
    "Roxana",
]

apellidos_bolivianos = [
    "Condori",
    "Mamani",
    "Quispe",
    "Rojas",
    "Guzmán",
    "Salvatierra",
    "Zeballos",
    "Choque",
    "Rivera",
    "Alarcón",
]


def limpiar_texto(texto):
    """Quita acentos y convierte espacios a minúsculas sin tildes"""
    texto = unicodedata.normalize("NFKD", texto).encode("ASCII", "ignore").decode()
    return texto.lower().replace(" ", "")


def generar_genero_y_nombre():
    if random.choice([True, False]):
        nombre = random.choice(nombres_mujer)
        genero = "Femenino"
    else:
        nombre = random.choice(nombres_hombre)
        genero = "Masculino"
    return nombre, genero


def generar_correo_unico(base, existentes):
    correo = base + "@gmail.com"
    contador = 1
    while correo in existentes:
        correo = f"{base}{contador}@gmail.com"
        contador += 1
    existentes.add(correo)
    return correo


def seed_docentes(db: Session):
    existentes = set(doc.correo for doc in db.query(Docente).all())
    nuevos = []

    # Admin
    admin_correo = "admin@gmail.com"
    if admin_correo not in existentes:
        nuevos.append(
            Docente(
                nombre="Admin",
                apellido="General",
                telefono="70000001",
                correo=admin_correo,
                genero="Masculino",
                contrasena=hash_contrasena("admin"),
                is_doc=False,
            )
        )
        existentes.add(admin_correo)

    # Docentes por materia
    materias = db.query(Materia).all()
    usados = set()
    for materia in materias:
        nombre_doc, genero = generar_genero_y_nombre()
        apellido = random.choice(apellidos_bolivianos)

        # Evitar que se repitan combinaciones
        clave = (nombre_doc, apellido)
        while clave in usados:
            nombre_doc, genero = generar_genero_y_nombre()
            apellido = random.choice(apellidos_bolivianos)
            clave = (nombre_doc, apellido)
        usados.add(clave)

        base_correo = limpiar_texto(nombre_doc + apellido)
        correo = generar_correo_unico(base_correo, existentes)

        nuevos.append(
            Docente(
                nombre=nombre_doc,
                apellido=apellido,
                telefono=str(70000000 + len(nuevos)),
                correo=correo,
                genero=genero,
                contrasena=hash_contrasena(limpiar_texto(nombre_doc)),
                is_doc=True,
            )
        )

    db.bulk_save_objects(nuevos)
    db.commit()
    print(f"✅ Se crearon {len(nuevos)} docentes.")
