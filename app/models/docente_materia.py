from sqlalchemy import Column, Integer, ForeignKey
from app.database import Base
from sqlalchemy.orm import relationship


class DocenteMateria(Base):
    __tablename__ = "docente_materia"

    id = Column(Integer, primary_key=True, index=True)
    docente_id = Column(
        Integer, ForeignKey("docentes.id", ondelete="CASCADE"), nullable=False
    )
    materia_id = Column(
        Integer, ForeignKey("materias.id", ondelete="CASCADE"), nullable=False
    )
    docente = relationship("Docente", backref="materias_asignadas")
    materia = relationship("Materia", backref="docentes_asignados")
