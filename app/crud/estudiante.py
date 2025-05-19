from sqlalchemy.orm import Session
from app.models.estudiante import Estudiante
from app.schemas.estudiante import EstudianteCreate, EstudianteUpdate


def crear_estudiante(db: Session, estudiante: EstudianteCreate):
    nuevo = Estudiante(**estudiante.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


def obtener_estudiantes(db: Session):
    return db.query(Estudiante).all()


def obtener_estudiante(db: Session, estudiante_id: int):
    return db.query(Estudiante).filter(Estudiante.id == estudiante_id).first()


def actualizar_estudiante(db: Session, estudiante_id: int, datos: EstudianteUpdate):
    est = db.query(Estudiante).filter(Estudiante.id == estudiante_id).first()
    if est:
        for key, value in datos.dict(exclude_unset=True).items():
            setattr(est, key, value)
        db.commit()
        db.refresh(est)
    return est


def eliminar_estudiante(db: Session, estudiante_id: int):
    est = db.query(Estudiante).filter(Estudiante.id == estudiante_id).first()
    if est:
        db.delete(est)
        db.commit()
    return est
