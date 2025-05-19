from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base


class Docente(Base):
    __tablename__ = "docentes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    apellido = Column(String, nullable=False)
    telefono = Column(String, nullable=False)
    correo = Column(String, unique=True, nullable=False)
    genero = Column(String, nullable=False)
    contrasena = Column(String, nullable=False)
    is_doc = Column(Boolean, default=True)  # True = docente, False = admin
