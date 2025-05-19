from sqlalchemy.orm import Session
from app.models.curso_materia import CursoMateria
from app.schemas.curso_materia import CursoMateriaCreate, CursoMateriaUpdate


def crear_asignacion(db: Session, datos: CursoMateriaCreate):
    asignacion = CursoMateria(**datos.dict())
    db.add(asignacion)
    db.commit()
    db.refresh(asignacion)
    return asignacion


def listar_asignaciones(db: Session):
    return db.query(CursoMateria).all()


def obtener_por_id(db: Session, asignacion_id: int):
    return db.query(CursoMateria).filter(CursoMateria.id == asignacion_id).first()


def actualizar_asignacion(db: Session, asignacion_id: int, datos: CursoMateriaUpdate):
    asignacion = db.query(CursoMateria).filter(CursoMateria.id == asignacion_id).first()
    if asignacion:
        for key, value in datos.dict().items():
            setattr(asignacion, key, value)
        db.commit()
        db.refresh(asignacion)
    return asignacion


def eliminar_asignacion(db: Session, asignacion_id: int):
    asignacion = db.query(CursoMateria).filter(CursoMateria.id == asignacion_id).first()
    if asignacion:
        db.delete(asignacion)
        db.commit()
    return asignacion


def listar_materias_por_curso(db: Session, curso_id: int):
    return db.query(CursoMateria).filter(CursoMateria.curso_id == curso_id).all()


def listar_cursos_por_materia(db: Session, materia_id: int):
    return db.query(CursoMateria).filter(CursoMateria.materia_id == materia_id).all()
