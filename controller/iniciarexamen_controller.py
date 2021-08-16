from flask import request
from flask_restful import Resource
from configs.flask_config import app
from service.iniciarexamen_service import IniciarExamenService
from service.autorizador_service import AutorizadorService

iniciar_examen_service = IniciarExamenService()
autorizador_service = AutorizadorService()

class IniciarExamenController(Resource):

    def post(self):
        email_candidato = request.headers['Authorization']
        valido = autorizador_service.validar_token(email_candidato)
        if valido:
            lista_test_psicologicos = []
            json_dict = request.json
            if json_dict is not None:
                if 'lista_test_psicologicos' in json_dict:
                    lista_test_psicologicos = request.json['lista_test_psicologicos']
            return iniciar_examen_service.iniciar_examen(email_candidato, lista_test_psicologicos)
        return {'mensaje': 'Operación no valida.'}, 403