from pydantic import BaseModel, EmailStr
from typing import Optional


class DocenteBase(BaseModel):
    nombre: str
    apellido: str
    telefono: str
    correo: EmailStr
    genero: str
    is_doc: bool = True


class DocenteCreate(DocenteBase):
    contrasena: str


class DocenteOut(DocenteBase):
    id: int

    class Config:
        from_attributes = True


class DocenteLogin(BaseModel):
    correo: EmailStr
    contrasena: str


class DocenteUpdate(BaseModel):
    nombre: Optional[str]
    apellido: Optional[str]
    telefono: Optional[str]
    genero: Optional[str]
    is_doc: Optional[bool]
