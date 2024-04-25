from models.database import db, Configuration

def create(parameter, value):
    new_configuration = Configuration(parameter=parameter, value=value)
    db.session.add(new_configuration)
    db.session.commit()
    print(f"Configuración creada exitosamente: {parameter}={value}")


def set(parameter, new_value):
    configuration = Configuration.query.filter_by(parameter=parameter).first()

    if configuration:
        configuration.value = new_value
        db.session.commit()
        print(f"Valor de configuración actualizado exitosamente: {parameter}={new_value}")
    else:
        print(f"Configuración no encontrada: {parameter}")

def get(parameter):
    configuration = Configuration.query.filter_by(parameter=parameter).first()

    if configuration:
        return configuration.value
    else:
        print(f"Configuración no encontrada: {parameter}")
        return None
