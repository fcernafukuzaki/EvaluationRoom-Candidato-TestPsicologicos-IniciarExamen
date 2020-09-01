from flask import request
from flask_restful import Resource
from configs.flask_config import app
from service.iniciarexamen_service import IniciarExamenService
from service.autorizador_service import AutorizadorService

iniciar_examen_service = IniciarExamenService()
autorizador_service = AutorizadorService()

class IniciarExamenController(Resource):

    def get(self, email_candidato):
        token = request.headers['Authorization']
        valido = autorizador_service.validar_token(token)
        if valido:
            return iniciar_examen_service.iniciar_examen(email_candidato)
        return {'mensaje': 'Operación no valida.'}, 403