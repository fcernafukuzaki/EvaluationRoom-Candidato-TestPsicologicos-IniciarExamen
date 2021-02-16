from flask import request
from flask_restful import Resource
from configs.flask_config import app
from service.registrarrespuesta_service import RegistrarRespuestaService
from service.autorizador_service import AutorizadorService

registrar_respuesta_service = RegistrarRespuestaService()
autorizador_service = AutorizadorService()

class RegistrarRespuestaController(Resource):

    def post(self):
        email_candidato = request.headers['Authorization']
        valido = autorizador_service.validar_token(email_candidato)
        if valido:
            json_dict = request.json
            if json_dict is not None:
                if 'idcandidato' in json_dict:
                    idcandidato = request.json['idcandidato']
                    idtestpsicologico = request.json['idtestpsicologico']
                    idparte = request.json['idparte']
                    idpregunta = request.json['idpregunta']
                    respuesta = request.json['respuesta']
                    return registrar_respuesta_service.registrar_respuesta(email_candidato, idcandidato, idtestpsicologico, idparte, idpregunta, respuesta)
        return {'mensaje': 'Operación no valida.'}, 403