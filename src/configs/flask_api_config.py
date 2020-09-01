from .flask_config import api
from controller.iniciarexamen_controller import *

api.add_resource(IniciarExamenController,
    '/v1/iniciar_examen/<string:email_candidato>')
