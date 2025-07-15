from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.schemas.estudiante import EstudianteOut, EstudianteUpdate
from app.database import SessionLocal
from app.crud import estudiante as crud
from app.auth.roles import (
    admin_required,
    docente_o_admin_required,
    propietario_o_admin,
    usuario_autenticado,
)
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
    correo: str = Form(None),  # 🆕 Opcional para login
    contrasena: str = Form(None),  # 🆕 Opcional para login
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
            correo=correo if correo else None,
            contrasena=contrasena if contrasena else None,
        ),
    )
    return nuevo


@router.get("/", response_model=list[EstudianteOut])
def listar(
    db: Session = Depends(get_db), payload: dict = Depends(docente_o_admin_required)
):
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
    correo: str = Form(None),  # 🆕 Opcional
    contrasena: str = Form(None),  # 🆕 Opcional
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
        correo=correo if correo else None,
        contrasena=contrasena if contrasena else None,
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


# ========== ENDPOINTS PARA ESTUDIANTES AUTENTICADOS ==========


@router.get("/mi-perfil", response_model=EstudianteOut)
def obtener_mi_perfil_estudiante(
    payload: dict = Depends(usuario_autenticado),
    db: Session = Depends(get_db),
):
    """👤 Obtener mi perfil como estudiante"""
    # Verificar que el usuario es estudiante
    if payload.get("user_type") != "estudiante":
        raise HTTPException(status_code=403, detail="Solo estudiantes pueden acceder")

    estudiante_id = payload.get("user_id")
    estudiante = crud.obtener_estudiante(db, estudiante_id)
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return estudiante


@router.get("/{estudiante_id}", response_model=EstudianteOut)
def obtener_estudiante(
    estudiante_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(propietario_o_admin),
):
    """👤 Obtener datos de un estudiante"""
    # Verificar permisos: debe ser el mismo estudiante, padre del estudiante, o admin
    user_type = payload.get("user_type")
    user_id = payload.get("user_id")

    if user_type == "admin":
        # Admin puede ver cualquier estudiante
        pass
    elif user_type == "docente":
        # Docente puede ver estudiantes (verificar asignación si es necesario)
        pass
    elif user_type == "estudiante" and user_id == estudiante_id:
        # El mismo estudiante puede ver su perfil
        pass
    elif user_type == "padre":
        # Verificar que es padre del estudiante
        from app.crud.padre import es_padre_del_estudiante

        if not es_padre_del_estudiante(db, user_id, estudiante_id):
            raise HTTPException(status_code=403, detail="No autorizado")
    else:
        raise HTTPException(status_code=403, detail="No autorizado")

    estudiante = crud.obtener_estudiante(db, estudiante_id)
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return estudiante
