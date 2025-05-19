from sqlalchemy import Column, DateTime, Integer, String, Date, func
from app.database import Base


class Estudiante(Base):
    __tablename__ = "estudiantes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    apellido = Column(String, nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)
    genero = Column(String, nullable=False)
    url_imagen = Column(String)
    nombre_tutor = Column(String, nullable=True)
    telefono_tutor = Column(String, nullable=True)
    direccion_casa = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())