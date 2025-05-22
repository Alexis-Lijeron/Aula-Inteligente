from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.schemas.estudiante import EstudianteOut, EstudianteUpdate
from app.database import SessionLocal
from app.crud import estudiante as crud
from app.auth.roles import admin_required, docente_o_admin_required
from app.cloudinary import subir_imagen_a_cloudinary
from datetime import datetime

router = APIRouter(prefix="/estudiantes", tags=["Estudiantes"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def validar_campo(nombre: str, valor: str):
    if not valor or valor.strip() == "":
        raise HTTPException(
            status_code=400, detail=f"El campo '{nombre}' no puede estar vacío"
        )
    return valor.strip()


@router.post("/", response_model=EstudianteOut)
def crear(
    nombre: str = Form(...),
    apellido: str = Form(...),
    fecha_nacimiento: str = Form(...),
    genero: str = Form(...),
    nombre_tutor: str = Form(...),
    telefono_tutor: str = Form(...),
    direccion_casa: str = Form(...),
    imagen: UploadFile = File(...),
    db: Session = Depends(get_db),
    payload: dict = Depends(admin_required),
):
    # Validar campos vacíos
    nombre = validar_campo("nombre", nombre)
    apellido = validar_campo("apellido", apellido)
    genero = validar_campo("genero", genero)
    nombre_tutor = validar_campo("nombre_tutor", nombre_tutor)
    telefono_tutor = validar_campo("telefono_tutor", telefono_tutor)
    direccion_casa = validar_campo("direccion_casa", direccion_casa)

    url_imagen = subir_imagen_a_cloudinary(imagen, f"{nombre}_{apellido}")

    nuevo = crud.crear_estudiante(
        db,
        EstudianteUpdate(
            nombre=nombre,
            apellido=apellido,
            fecha_nacimiento=datetime.fromisoformat(fecha_nacimiento),
            genero=genero,
            url_imagen=url_imagen,
            nombre_tutor=nombre_tutor,
            telefono_tutor=telefono_tutor,
            direccion_casa=direccion_casa,
        ),
    )
    return nuevo


@router.get("/", response_model=list[EstudianteOut])
def listar(db: Session = Depends(get_db), payload: dict = Depends(admin_required)):
    return crud.obtener_estudiantes(db)


@router.get("/{estudiante_id}", response_model=EstudianteOut)
def obtener(
    estudiante_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(docente_o_admin_required),
):
    est = crud.obtener_estudiante(db, estudiante_id)
    if not est:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return est


@router.put("/{estudiante_id}", response_model=EstudianteOut)
def actualizar(
    estudiante_id: int,
    nombre: str = Form(...),
    apellido: str = Form(...),
    fecha_nacimiento: str = Form(...),
    genero: str = Form(...),
    nombre_tutor: str = Form(...),
    telefono_tutor: str = Form(...),
    direccion_casa: str = Form(...),
    imagen: UploadFile = File(None),
    db: Session = Depends(get_db),
    payload: dict = Depends(admin_required),
):
    # Validar campos vacíos
    nombre = validar_campo("nombre", nombre)
    apellido = validar_campo("apellido", apellido)
    genero = validar_campo("genero", genero)
    nombre_tutor = validar_campo("nombre_tutor", nombre_tutor)
    telefono_tutor = validar_campo("telefono_tutor", telefono_tutor)
    direccion_casa = validar_campo("direccion_casa", direccion_casa)

    url_imagen = None
    if imagen:
        url_imagen = subir_imagen_a_cloudinary(imagen, f"{nombre}_{apellido}")

    datos = EstudianteUpdate(
        nombre=nombre,
        apellido=apellido,
        fecha_nacimiento=datetime.fromisoformat(fecha_nacimiento),
        genero=genero,
        url_imagen=url_imagen,
        nombre_tutor=nombre_tutor,
        telefono_tutor=telefono_tutor,
        direccion_casa=direccion_casa,
    )
    return crud.actualizar_estudiante(db, estudiante_id, datos)


@router.delete("/{estudiante_id}")
def eliminar(
    estudiante_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(admin_required),
):
    est = crud.eliminar_estudiante(db, estudiante_id)
    if not est:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return {"mensaje": "Estudiante eliminado"}
