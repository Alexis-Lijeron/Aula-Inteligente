from sqlalchemy.orm import Session
from app.models.docente import Docente
from app.schemas.docente import DocenteCreate, DocenteUpdate
from passlib.hash import bcrypt # type: ignore


def crear_docente(db: Session, docente: DocenteCreate):
    hashed = bcrypt.hash(docente.contrasena)
    nuevo = Docente(**docente.dict(exclude={"contrasena"}), contrasena=hashed)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


def autenticar_docente(db: Session, correo: str, contrasena: str):
    docente = db.query(Docente).filter(Docente.correo == correo).first()
    if docente and bcrypt.verify(contrasena, docente.contrasena):
        return docente
    return None


def obtener_por_correo(db: Session, correo: str):
    return db.query(Docente).filter(Docente.correo == correo).first()


def actualizar_docente(db: Session, docente_id: int, datos: DocenteUpdate):
    doc = db.query(Docente).filter(Docente.id == docente_id).first()
    if doc:
        for key, value in datos.dict(exclude_unset=True).items():
            setattr(doc, key, value)
        db.commit()
        db.refresh(doc)
    return doc


def eliminar_docente(db: Session, docente_id: int):
    doc = db.query(Docente).filter(Docente.id == docente_id).first()
    if doc:
        db.delete(doc)
        db.commit()
    return doc


def obtener_docentes(db: Session):
    return db.query(Docente).filter(Docente.is_doc == True).all()


def obtener_admins(db: Session):
    return db.query(Docente).filter(Docente.is_doc == False).all()


def obtener_docente_por_id(db: Session, docente_id: int):
    return db.query(Docente).filter(Docente.id == docente_id).first()
