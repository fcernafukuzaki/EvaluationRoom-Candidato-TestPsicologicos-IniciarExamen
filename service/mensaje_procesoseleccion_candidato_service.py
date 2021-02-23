from configs.flask_config import db
from object.mensaje_procesoseleccion_candidato import MensajeProcesoseleccionCandidato

class MensajeProcesoseleccionCandidatoService():

    def _consultar_por_identificador(self, id_mensaje):
        return db.session.query(
                    MensajeProcesoseleccionCandidato
                ).filter(MensajeProcesoseleccionCandidato.id_mensaje == id_mensaje
                ).order_by(MensajeProcesoseleccionCandidato.id_mensaje)
    
    def obtener_mensaje_bienvenida(self, nombre):
        try:
            mensaje_procesoseleccion_candidato = self._consultar_por_identificador(1)
        except:
            print('Error al recuperar el mensaje de bienvenida del candidato.')
            return False, 'Error al recuperar el mensaje de bienvenida del candidato.'
        else:
            print('El candidato {} va a iniciar el examen (mensaje de bienvenida)'.format(nombre))
            if mensaje_procesoseleccion_candidato.count() > 0:
                for mensaje in mensaje_procesoseleccion_candidato:
                    return True, mensaje.mensaje.format(nombre)
            return False, None

    def obtener_mensaje_felicitaciones(self, nombre):
        try:
            mensaje_procesoseleccion_candidato = self._consultar_por_identificador(2)
        except:
            print('Error al recuperar el mensaje de felicitaciones del candidato.')
            return False, 'Error al recuperar el mensaje de felicitaciones del candidato.'
        else:
            print('El candidato {} ha finalizado los test psicológicos asignados'.format(nombre))
            if mensaje_procesoseleccion_candidato.count() > 0:
                for mensaje in mensaje_procesoseleccion_candidato:
                    return True, mensaje.mensaje.format(nombre)
            return False, None
