import random
from sqlalchemy.orm import Session
from app.models.docente_materia import DocenteMateria
from app.models.tipo_evaluacion import TipoEvaluacion
from app.models.gestion import Gestion
from app.models.peso_tipo_evaluacion import PesoTipoEvaluacion


def seed_peso_tipo_evaluacion(db: Session):
    # Valores fijos para tipoevaluacion_id
    pesos_fijos = {
        1: 30,  # Exámenes
        3: 10,  # Exposiciones
        7: 10,  # Proyecto final
        8: 5,  # Trabajo grupal
    }

    # Valores variables a repartir entre docentes (los ids pueden ser distintos en tu BD real)
    pesos_variables = {
        2: 15,  # Tareas
        4: 10,  # Participaciones
        5: 10,  # Asistencia
        6: 5,  # Prácticas
        9: 3,  # Ensayos
        10: 2,  # Cuestionarios
    }

    gestion = db.query(Gestion).filter_by(anio="2025").first()
    docente_materias = db.query(DocenteMateria).all()
    tipo_evaluaciones = db.query(TipoEvaluacion).all()

    if not gestion or len(tipo_evaluaciones) < 10:
        print("❌ Faltan datos de gestión o tipo de evaluación.")
        return

    for dm in docente_materias:
        # Intercambiar aleatoriamente los valores variables
        items_variables = list(pesos_variables.items())
        random.shuffle(items_variables)

        for tipo_eval in tipo_evaluaciones:
            if tipo_eval.id in pesos_fijos:
                porcentaje = pesos_fijos[tipo_eval.id]
            else:
                # Buscar en la lista ya mezclada
                for idx, (id_original, valor) in enumerate(items_variables):
                    if tipo_eval.id == id_original:
                        porcentaje = valor
                        break
            nuevo_peso = PesoTipoEvaluacion(
                porcentaje=porcentaje,
                docente_id=dm.docente_id,
                materia_id=dm.materia_id,
                gestion_id=gestion.id,
                tipo_evaluacion_id=tipo_eval.id,
            )
            db.add(nuevo_peso)

        print(
            f"✅ Pesos asignados para docente {dm.docente_id} - materia {dm.materia_id}"
        )

    db.commit()
    print("🎯 Seeder finalizado sin valores negativos ni duplicación de pesos fijos.")
