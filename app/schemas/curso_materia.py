from pydantic import BaseModel
from app.schemas.curso import CursoOut
from app.schemas.materia import MateriaOut


class CursoMateriaBase(BaseModel):
    curso_id: int
    materia_id: int


class CursoMateriaCreate(CursoMateriaBase):
    pass


class CursoMateriaUpdate(CursoMateriaBase):
    pass


class CursoMateriaOut(CursoMateriaBase):
    id: int

    class Config:
        from_attributes = True


# Para respuestas enriquecidas
class CursoMateriaDetalle(BaseModel):
    id: int
    curso: CursoOut
    materia: MateriaOut

    class Config:
        from_attributes = True
