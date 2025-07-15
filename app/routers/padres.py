from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.schemas.padre import PadreCreate, PadreOut, PadreUpdate, PadreConHijos
from app.schemas.estudiante import EstudianteOut
from app.crud import padre as crud
from app.auth.roles import admin_required, usuario_autenticado, propietario_o_admin
from typing import List

router = APIRouter(prefix="/padres", tags=["👨‍👩‍👧‍👦 Padres"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ========== ENDPOINTS ADMINISTRATIVOS (Solo admins) ==========


@router.post("/", response_model=PadreOut)
def crear_padre(
    padre: PadreCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(admin_required),
):
    """👤 Crear un nuevo padre (Solo administradores)"""
    return crud.crear_padre(db, padre)


@router.get("/", response_model=List[PadreOut])
def listar_padres(
    db: Session = Depends(get_db),
    payload: dict = Depends(admin_required),
):
    """📋 Listar todos los padres (Solo administradores)"""
    return crud.obtener_padres(db)


@router.put("/{padre_id}", response_model=PadreOut)
def actualizar_padre(
    padre_id: int,
    datos: PadreUpdate,
    db: Session = Depends(get_db),
    payload: dict = Depends(admin_required),
):
    """✏️ Actualizar datos del padre (Solo administradores)"""
    padre = crud.actualizar_padre(db, padre_id, datos)
    if not padre:
        raise HTTPException(status_code=404, detail="Padre no encontrado")
    return padre


@router.delete("/{padre_id}")
def eliminar_padre(
    padre_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(admin_required),
):
    """🗑️ Eliminar padre (Solo administradores)"""
    padre = crud.eliminar_padre(db, padre_id)
    if not padre:
        raise HTTPException(status_code=404, detail="Padre no encontrado")
    return {"mensaje": "Padre eliminado correctamente"}


@router.post("/{padre_id}/hijos/{estudiante_id}")
def asignar_hijo(
    padre_id: int,
    estudiante_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(admin_required),
):
    """👶 Asignar hijo a padre (Solo administradores)"""
    resultado = crud.asignar_hijo_a_padre(db, padre_id, estudiante_id)
    if not resultado:
        raise HTTPException(status_code=400, detail="No se pudo asignar hijo al padre")
    return {"mensaje": "Hijo asignado correctamente"}


@router.delete("/{padre_id}/hijos/{estudiante_id}")
def desasignar_hijo(
    padre_id: int,
    estudiante_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(admin_required),
):
    """❌ Desasignar hijo de padre (Solo administradores)"""
    resultado = crud.desasignar_hijo_de_padre(db, padre_id, estudiante_id)
    if not resultado:
        raise HTTPException(
            status_code=400, detail="No se pudo desasignar hijo del padre"
        )
    return {"mensaje": "Hijo desasignado correctamente"}


# ========== ENDPOINTS PARA PADRES AUTENTICADOS ==========


@router.get("/mi-perfil", response_model=PadreOut)
def obtener_mi_perfil(
    payload: dict = Depends(usuario_autenticado),
    db: Session = Depends(get_db),
):
    """👤 Obtener mi perfil como padre"""
    # Verificar que el usuario es padre
    if payload.get("user_type") != "padre":
        raise HTTPException(status_code=403, detail="Solo padres pueden acceder")

    padre_id = payload.get("user_id")
    padre = crud.obtener_padre_por_id(db, padre_id)
    if not padre:
        raise HTTPException(status_code=404, detail="Padre no encontrado")
    return padre


@router.get("/mis-hijos", response_model=List[EstudianteOut])
def obtener_mis_hijos(
    payload: dict = Depends(usuario_autenticado),
    db: Session = Depends(get_db),
):
    """👶 Obtener mis hijos"""
    # Verificar que el usuario es padre
    if payload.get("user_type") != "padre":
        raise HTTPException(status_code=403, detail="Solo padres pueden acceder")

    padre_id = payload.get("user_id")
    return crud.obtener_hijos_del_padre(db, padre_id)


@router.get("/{padre_id}/hijos")
def obtener_hijos_del_padre(
    padre_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(propietario_o_admin),
):
    """👶 Obtener hijos de un padre específico"""
    # Verificar permisos: debe ser el mismo padre o admin
    user_type = payload.get("user_type")
    user_id = payload.get("user_id")

    if user_type != "admin" and (user_type != "padre" or user_id != padre_id):
        raise HTTPException(status_code=403, detail="No autorizado")

    return crud.obtener_hijos_del_padre(db, padre_id)


@router.get("/{padre_id}", response_model=PadreOut)
def obtener_padre(
    padre_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(propietario_o_admin),
):
    """👤 Obtener datos de un padre"""
    # Verificar permisos: debe ser el mismo padre o admin
    user_type = payload.get("user_type")
    user_id = payload.get("user_id")

    if user_type != "admin" and (user_type != "padre" or user_id != padre_id):
        raise HTTPException(status_code=403, detail="No autorizado")

    padre = crud.obtener_padre_por_id(db, padre_id)
    if not padre:
        raise HTTPException(status_code=404, detail="Padre no encontrado")
    return padre
