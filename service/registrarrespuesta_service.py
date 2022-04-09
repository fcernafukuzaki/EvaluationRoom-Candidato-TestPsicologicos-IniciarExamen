from flask import jsonify
from configs.flask_config import db
from sqlalchemy import func
from object.candidato_testpsicologicodetalle import CandidatoTestPsicologicoDetalle, CandidatoTestPsicologicoDetalleSchema
from service.validaremailcandidato_service import ValidarEmailCandidatoService
from service.log_service import LogService
import json
import ast
import urllib3

candidato_testpsicologico_detalle_schema = CandidatoTestPsicologicoDetalleSchema()

log_service = LogService()
validar_email_candidato_service = ValidarEmailCandidatoService()

class RegistrarRespuestaService():

    def registrar_respuesta(self, email, idcandidato, idtestpsicologico, idparte, idpregunta, respuesta, origin, host, user_agent):
        email_valido, idcandidato = validar_email_candidato_service.valida_email_candidato(email)
        
        if email_valido == False:
            return {'mensaje': 'No existe candidato.'}, 404
        
        flag, mensaje = self.registrar_respuesta_candidato(idcandidato, idtestpsicologico, idparte, idpregunta, respuesta, origin, host, user_agent)
        if flag == False:
            return {'mensaje': mensaje}, 500
        return {'mensaje': mensaje}, 200
        
    def registrar_respuesta_candidato(self, idcandidato, idtestpsicologico, idparte, idpregunta, respuesta, origin, host, user_agent):
        try:
            new_candidato_testpsicologico_detalle = CandidatoTestPsicologicoDetalle(idcandidato, idtestpsicologico, 
                                                        idparte, idpregunta, 
                                                        json.dumps(respuesta), func.now(),
                                                        origin=origin, host=host, user_agent=user_agent)
            db.session.add(new_candidato_testpsicologico_detalle)
            db.session.commit()

            return True, 'Registro exitoso.'
        except:
            accion = f'Error al registrar respuesta del candidato {idcandidato}'
            detalle = f'Candidato: {idcandidato}. Datos de la pregunta: {idtestpsicologico}.{idparte}.{idpregunta}. Respuesta: {json.dumps(respuesta)}'
            _ = log_service.registrar_candidato_log_accion(idcandidato, accion, detalle, origin, host, user_agent)
            
            print('Error al registrar respuesta del candidato {}.'.format(idcandidato))
            return False, 'Error al registrar respuesta.'
