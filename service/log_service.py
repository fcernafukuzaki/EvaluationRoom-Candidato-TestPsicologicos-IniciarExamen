from configs.flask_config import db
from sqlalchemy import func
from sqlalchemy import desc
from object.candidato_testpsicologico_log import CandidatoTestPsicologicoLog, CandidatoTestPsicologicoLogSchema
from object.candidato_log import CandidatoLog, CandidatoLogSchema
from object.candidato_testpsicologico import CandidatoTestPsicologico
from service.validaremailcandidato_service import ValidarEmailCandidatoService
from service.psychologicaltestinterpretacion_service import PsychologicalTestInterpretacionService

candidato_testpsicologico_detalle_schema = CandidatoTestPsicologicoLogSchema()
candidato_log_schema = CandidatoLogSchema()

validar_email_candidato_service = ValidarEmailCandidatoService()
psychologicaltestinterpretacion_service = PsychologicalTestInterpretacionService()

class LogService():

    def registrar_log(self, email_candidato, idcandidato, idtestpsicologico, idparte, flag, origin, host, user_agent):
        email_valido, idcandidato = validar_email_candidato_service.valida_email_candidato(email_candidato)
        
        if email_valido == False:
            return {'mensaje': 'No existe candidato.'}, 404
        
        flag_registro, mensaje = self.registrar_log_candidato(idcandidato, idtestpsicologico, idparte, flag, origin, host, user_agent)
        if flag_registro == False:
            accion_aux = 'Fin de Prueba' if flag == 'F' else 'Inicio de Prueba'
            accion = f'Error al registrar {accion_aux} del candidato {idcandidato} ({email_candidato})'
            detalle = f'Candidato: {idcandidato} ({email_candidato}). Datos de prueba: {idtestpsicologico}.{idparte}'
            _ = self.registrar_candidato_log_accion(idcandidato, accion, detalle, origin, host, user_agent)
            return {'mensaje': mensaje}, 500
        return {'mensaje': mensaje}, 200
        
    def registrar_log_candidato(self, idcandidato, idtestpsicologico, idparte, flag, origin, host, user_agent):
        ''' Si el valor del argumento flag es 'F', 
                entonces buscar si existe registro previo y actualizar la fecha de fin
                e invocar API de interpretación de resultados
            Si el valor del argumento flag es diferente a 'F',
                entonces insertar nuevo registro con fecha de inicio
        '''
        try:
            if flag == 'F':
                candidato_log_examen = db.session.query(
                    CandidatoTestPsicologicoLog
                ).filter(CandidatoTestPsicologicoLog.idcandidato==idcandidato,
                    CandidatoTestPsicologicoLog.idtestpsicologico==idtestpsicologico,
                    CandidatoTestPsicologicoLog.idparte==idparte
                ).order_by(desc(CandidatoTestPsicologicoLog.fechainicio))
                
                if candidato_log_examen.count() > 0:
                    objeto_candidato_log_examen = candidato_log_examen.first()
                    objeto_candidato_log_examen.fechafin = func.now()

                    db.session.commit()

                    try:
                        psychologicaltestinterpretacion_service.getinterpretacion(idcandidato)
                    except:
                        print('Error al interpretar los resultados del candidato {}.'.format(idcandidato))

                    return True, 'Actualización exitosa.'
            
            new_candidato_testpsicologico_log = CandidatoTestPsicologicoLog(idcandidato, idtestpsicologico, 
                                                        idparte, 
                                                        func.now(), 
                                                        origin=origin, host=host, user_agent=user_agent)
            db.session.add(new_candidato_testpsicologico_log)
            db.session.commit()

            return True, 'Registro exitoso.'
        except:
            accion = f'Error al registrar log del candidato {idcandidato}'
            detalle_aux = 'Fin de Prueba' if flag == 'F' else 'Inicio de Prueba'
            detalle = f'Candidato: {idcandidato}. Datos de prueba: {idtestpsicologico}.{idparte} {detalle_aux}'
            _ = self.registrar_candidato_log_accion(idcandidato, accion, detalle, origin, host, user_agent)
            print('Error al registrar log del candidato {}.'.format(idcandidato))
            return False, 'Error al registrar respuesta.'

    def registrar_candidato_log_accion(self, idcandidato, accion, detalle, origin, host, user_agent):
        try:
            new_candidato_log = CandidatoLog(func.now(), idcandidato, accion, detalle, origin, host, user_agent)
            db.session.add(new_candidato_log)
            db.session.commit()

            mensaje = 'Registro exitoso.'
            return {'mensaje': mensaje}, 200
        except:
            print('Error al registrar acción del candidato {}.'.format(idcandidato))
            mensaje = 'Error al registrar acción del candidato.'
            return {'mensaje': mensaje}, 500
