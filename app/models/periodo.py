from sqlalchemy import Column, DateTime, Integer, String, Date, ForeignKey, func
from app.database import Base
from sqlalchemy.orm import relationship


class Periodo(Base):
    __tablename__ = "periodos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False, unique=True)
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=False)

    gestion_id = Column(
        Integer, ForeignKey("gestiones.id", ondelete="CASCADE"), nullable=False
    )
    gestion = relationship("Gestion", backref="periodos")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
