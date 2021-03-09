from flask import request
from flask_restful import Resource
from configs.flask_config import app
from service.log_service import LogService
from service.autorizador_service import AutorizadorService

log_service = LogService()
autorizador_service = AutorizadorService()

class RegistrarLogController(Resource):

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
                    flag = request.json['flag']

                    origin = None
                    if 'Origin' in request.headers:
                        origin = request.headers['Origin']
                    host = request.headers['Host']
                    user_agent = request.headers['User-Agent']
                    return log_service.registrar_log(email_candidato, idcandidato, idtestpsicologico, idparte, flag, origin, host, user_agent)
        return {'mensaje': 'Operación no valida.'}, 403