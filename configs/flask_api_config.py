from .flask_config import api
from controller.iniciarexamen_controller import *
from controller.registrarrespuesta_controller import *

api.add_resource(IniciarExamenController,
    '/v1/iniciar_examen')

api.add_resource(RegistrarRespuestaController,
    '/v1/registrar_respuesta')
