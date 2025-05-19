from pydantic import BaseModel
from datetime import date
from typing import Optional


class EstudianteBase(BaseModel):
    nombre: str
    apellido: str
    fecha_nacimiento: date
    genero: str
    url_imagen: Optional[str] = None
    nombre_tutor: Optional[str] = None
    telefono_tutor: Optional[str] = None
    direccion_casa: Optional[str] = None


class EstudianteCreate(EstudianteBase):
    pass


class EstudianteUpdate(EstudianteBase):
    pass


class EstudianteOut(EstudianteBase):
    id: int

    class Config:
        from_attributes = True
