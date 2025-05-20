from sqlalchemy.orm import Session
from app.models.gestion import Gestion


def seed_gestion(db: Session):
    anio = "2025"
    descripcion = "Gestión académica del año 2025"

    gestion_existente = db.query(Gestion).filter_by(anio=anio).first()

    if not gestion_existente:
        nueva = Gestion(anio=anio, descripcion=descripcion)
        db.add(nueva)
        db.commit()
        print("✅ Gestión 2025 creada.")
    else:
        print("ℹ️ Gestión 2025 ya existe.")
