from configs.flask_config import db
from sqlalchemy import func
from sqlalchemy import desc
from object.candidato_testpsicologico_log import CandidatoTestPsicologicoLog, CandidatoTestPsicologicoLogSchema
from service.validaremailcandidato_service import ValidarEmailCandidatoService

candidato_testpsicologico_detalle_schema = CandidatoTestPsicologicoLogSchema()

validar_email_candidato_service = ValidarEmailCandidatoService()

class LogService():

    def registrar_log(self, email_candidato, idcandidato, idtestpsicologico, idparte, flag):
        email_valido, idcandidato = validar_email_candidato_service.valida_email_candidato(email_candidato)
        
        if email_valido == False:
            return {'mensaje': 'No existe candidato.'}, 404
        
        flag, mensaje = self.registrar_log_candidato(idcandidato, idtestpsicologico, idparte, flag)
        if flag == False:
            return {'mensaje': mensaje}, 500
        return {'mensaje': mensaje}, 200
        
    def registrar_log_candidato(self, idcandidato, idtestpsicologico, idparte, flag):
        ''' Si el valor del argumento flag es 'F', 
                entonces buscar si existe registro previo y actualizar la fecha de fin
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

                    return True, 'Actualización exitosa.'
            
            new_candidato_testpsicologico_log = CandidatoTestPsicologicoLog(idcandidato, idtestpsicologico, 
                                                        idparte, 
                                                        func.now())
            db.session.add(new_candidato_testpsicologico_log)
            db.session.commit()

            return True, 'Registro exitoso.'
        except:
            print('Error al registrar log del candidato {}.'.format(idcandidato))
            return False, 'Error al registrar respuesta.'