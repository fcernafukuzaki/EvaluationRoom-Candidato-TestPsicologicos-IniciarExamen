from flask import jsonify
from configs.flask_config import db
from sqlalchemy import func
from sqlalchemy import desc
from object.candidato import Candidato, CandidatoInfo, CandidatoSchema
from object.candidato_testpsicologico import CandidatoTestPsicologico, CandidatoTestPsicologicoSchema
from object.testpsicologico_instrucciones import TestPsicologicoInstrucciones, TestPsicologicoInstruccionesSchema
from object.testpsicologico_preguntas import TestPsicologicoPreguntas, TestPsicologicoPreguntasSchema
from object.candidato_testpsicologicodetalle import CandidatoTestPsicologicoDetalle
from object.reclutador_notificacion import ReclutadorNotificacion
from service.validaremailcandidato_service import ValidarEmailCandidatoService
from service.mensaje_procesoseleccion_candidato_service import MensajeProcesoseleccionCandidatoService
from service.log_service import LogService
import json
import ast
import urllib3

candidato_schema = CandidatoSchema()
candidato_testpsicologico_schema = CandidatoTestPsicologicoSchema(many=True)
testpsicologico_instrucciones_schema = TestPsicologicoInstruccionesSchema(many=True)
testpsicologico_preguntas_schema = TestPsicologicoPreguntasSchema(many=True)

log_service = LogService()
validar_email_candidato_service = ValidarEmailCandidatoService()
mensaje_procesoseleccion_candidato_service = MensajeProcesoseleccionCandidatoService()

class IniciarExamenService():

    def iniciar_examen(self, email, lista_test_psicologicos, origin, host, user_agent):
        email_valido, idcandidato = validar_email_candidato_service.valida_email_candidato(email)
        
        if email_valido == False:
            return {'mensaje': 'No existe candidato.'}, 404

        candidato, candidato_info = self.obtener_candidato(idcandidato, email)
        
        flag_autoregistro = self.valida_autoregistro(email, candidato.selfregistration)
        #if flag_autoregistro == False:
        #    return candidato_schema.jsonify(candidato)

        flag, testpsicologicos_pendientes = self.obtener_testpsicologicos_pendientes(idcandidato, email)
        if flag == False:
            flag, mensaje_felicitaciones = mensaje_procesoseleccion_candidato_service.obtener_mensaje_felicitaciones(candidato.nombre)
            reclutador_notificado = False
            if len(lista_test_psicologicos) > 0:
                reclutador_notificado = self.valida_lista_test_psicologicos(idcandidato, lista_test_psicologicos)
            
            accion = f'Candidato {idcandidato} ({email}) no tiene pruebas pendientes. Mostrar mensaje de felicitaciones'
            detalle = f'Candidato: {idcandidato} {email}. Listado de pruebas: {lista_test_psicologicos}'
            _ = log_service.registrar_candidato_log_accion(idcandidato, accion, detalle, origin, host, user_agent)
            
            return {'mensaje': mensaje_felicitaciones,
                    'reclutador_notificado': reclutador_notificado}, 202

        testpsicologicos_lista = []
        for test in candidato.testpsicologicos:
            testpsicologicos_lista.append(test.idtestpsicologico)

        flag, mensaje_bienvenida = mensaje_procesoseleccion_candidato_service.obtener_mensaje_bienvenida(candidato.nombre)
        try:
            flag, preguntas_pendientes, testpsicologicos_instrucciones, testpsicologicos_asignados, response_lista_obtener_preguntas_pendientes = self.obtener_preguntas_pendientes(candidato.idcandidato, testpsicologicos_lista)
            if flag:
                resultado_preguntas_pendientes = preguntas_pendientes
                resultado_testpsicologicos_instrucciones = testpsicologicos_instrucciones
                
                accion = f'Candidato {idcandidato} ({email}) inicia pruebas'
                detalle = f'Candidato: {idcandidato} {email}. Listado de pruebas: {response_lista_obtener_preguntas_pendientes}'
                _ = log_service.registrar_candidato_log_accion(idcandidato, accion, detalle, origin, host, user_agent)

                return {'mensaje_bienvenida': mensaje_bienvenida, 
                        'candidato': candidato_schema.dump(candidato_info), 
                        'testpsicologicos_asignados': candidato_testpsicologico_schema.dump(testpsicologicos_asignados),
                        'testpsicologicos_instrucciones': testpsicologico_instrucciones_schema.dump(resultado_testpsicologicos_instrucciones), 
                        'preguntas_pendientes': testpsicologico_preguntas_schema.dump(resultado_preguntas_pendientes) }, 200
            mensaje = preguntas_pendientes
            if flag is None:
                accion = f'Error al iniciar examen del candidato {idcandidato} ({email})'
                detalle = f'Mensaje: {mensaje}'
                _ = log_service.registrar_candidato_log_accion(idcandidato, accion, detalle, origin, host, user_agent)
                
                return {'mensaje': mensaje}, 500
            _, mensaje_felicitaciones = mensaje_procesoseleccion_candidato_service.obtener_mensaje_felicitaciones(candidato.nombre)
            
            accion = f'Candidato {idcandidato} ({email}) acabó las pruebas. Mostrar mensaje de felicitaciones'
            detalle = f'Candidato: {idcandidato} {email}. Listado de pruebas: {lista_test_psicologicos}'
            _ = log_service.registrar_candidato_log_accion(idcandidato, accion, detalle, origin, host, user_agent)
            
            return {'mensaje': mensaje_felicitaciones,
                    'reclutador_notificado': False}, 202
        except:
            accion = f'Error al recuperar las instrucciones de los test psicológicos del candidato {idcandidato} ({email})'
            detalle = f'Candidato: {idcandidato} {email}. Listado de pruebas: {lista_test_psicologicos}'
            _ = log_service.registrar_candidato_log_accion(idcandidato, accion, detalle, origin, host, user_agent)
            
            return {'mensaje': 'Error al recuperar las instrucciones de los test psicológicos.'}, 500
        
    def valida_autoregistro(self, email, autoregistro):
        if autoregistro:
            print('El candidato {} se ha registrado. Debe de completar sus datos en formulario'.format(email))
            return True
        print('El candidato {} ha sido registrado por un reclutador'.format(email))
        return False

    def obtener_candidato(self, idcandidato, email):
        candidato = Candidato.query.get(idcandidato)
        candidato_info = CandidatoInfo.candidato_info(idcandidato)
        if candidato:
            print('Se encontró candidato con el identificador {}'.format(email))
            return candidato, candidato_info
        print('No existe candidato con el identificador {}'.format(email))
        return None, None

    def obtener_testpsicologicos_pendientes(self, idcandidato, email):
        testpsicologicos_pendientes = db.session.query(
                                        CandidatoTestPsicologico
                                    ).filter(CandidatoTestPsicologico.idcandidato==idcandidato,
                                        db.or_(
                                            (db.and_(
                                                db.func.extract('year', CandidatoTestPsicologico.fechaexamen) == 1900,
                                                db.func.extract('month', CandidatoTestPsicologico.fechaexamen) == 1,
                                                db.func.extract('day', CandidatoTestPsicologico.fechaexamen) == 1)), 
                                            (CandidatoTestPsicologico.fechaexamen==None)
                                        )
                                    )

        if testpsicologicos_pendientes.count() > 0:
            print('Se encontró test psicologicos pendientes para el candidato con identificador {}'.format(email))
            return True, testpsicologicos_pendientes
        print('No se encontró test psicologicos pendientes para el candidato con identificador {}'.format(email))
        return False, None

    def obtener_instrucciones(self, idtestpsicologicos_lista, idtestpsicologicos_idparte_lista=None):
        try:
            if idtestpsicologicos_idparte_lista:
                print(' Se consulta la parte de los test psicológicos.')
                testpsicologico_instrucciones = db.session.query(
                                                    TestPsicologicoInstrucciones
                                                ).filter(
                                                    func.concat(TestPsicologicoInstrucciones.idtestpsicologico, '.', TestPsicologicoInstrucciones.idparte).in_(
                                                        (idtestpsicologicos_idparte_lista))
                                                ).order_by(TestPsicologicoInstrucciones.idtestpsicologico, TestPsicologicoInstrucciones.idparte)
            else:
                print(' Se consulta los test psicológicos. No posee partes.')
                testpsicologico_instrucciones = db.session.query(
                                                    TestPsicologicoInstrucciones
                                                ).filter(TestPsicologicoInstrucciones.idtestpsicologico.in_(idtestpsicologicos_lista)
                                                ).order_by(TestPsicologicoInstrucciones.idtestpsicologico, TestPsicologicoInstrucciones.idparte)
        except:
            mensaje = 'Error al recuperar las instrucciones del test psicológico.'
            print(mensaje)
            return False, mensaje, mensaje
        else:
            mensaje = 'Se recupera instrucciones de los test {} (Partes: {})'.format(idtestpsicologicos_lista, idtestpsicologicos_idparte_lista)
            print(mensaje)
            return True, testpsicologico_instrucciones, mensaje

    def obtener_preguntas_pendientes(self, idcandidato, id_testpsicologicos):
        try:
            '''
            SELECT idtestpsicologico, idparte, idpregunta, enunciado, alternativa
            FROM evaluationroom.testpsicologicopregunta
            WHERE idtestpsicologico IN (SELECT idtestpsicologico 
                                        FROM evaluationroom.candidatotest 
                                        WHERE idcandidato = 1)
            AND CONCAT(idtestpsicologico, '.', idparte, '.', idpregunta) NOT IN (
                                        SELECT CONCAT(idtestpsicologico, '.', idparte, '.', idpregunta) 
                                        FROM evaluationroom.candidatotestdetalle 
                                        WHERE idcandidato = 1
                                        UNION 
                                        SELECT CONCAT(ctd.idtestpsicologico, '.', ctd.idparte, '.', ctd.idpregunta) 
                                        FROM evaluationroom.testpsicologicopregunta ctd
                                        INNER JOIN evaluationroom.testpsicologicoparte_test tp 
                                            ON ctd.idtestpsicologico = tp.idtestpsicologico AND ctd.idparte = tp.idparte
                                        WHERE CONCAT(ctd.idtestpsicologico, '.', ctd.idparte) IN (
                                            SELECT DISTINCT(CONCAT(tp.idtestpsicologico, '.', tp.idparte))
                                            FROM evaluationroom.candidatotestdetalle ct
                                            INNER JOIN evaluationroom.testpsicologicoparte_test tp
                                                ON ct.idtestpsicologico = tp.idtestpsicologico AND ct.idparte = tp.idparte
                                            WHERE ct.idcandidato = 1
                                            )
                                        AND tp.duracion > 0
                                        AND tp.tipoprueba <> 'Preg.Abierta'
                                        AND CONCAT(ctd.idtestpsicologico, '.', ctd.idparte, '.', ctd.idpregunta) NOT IN (
                                            SELECT CONCAT(idtestpsicologico, '.', idparte, '.', idpregunta) 
                                            FROM evaluationroom.candidatotestdetalle 
                                            WHERE idcandidato = 1)
            )
            ORDER BY idtestpsicologico, idparte, idpregunta;
            '''
            _subquery_testpsicologicos_asignados = db.session.query(
                                CandidatoTestPsicologico.idtestpsicologico
                            ).filter(
                                CandidatoTestPsicologico.idcandidato==idcandidato
                            )
            
            _subquery_preguntas_respondidas = db.session.query(
                                func.concat(CandidatoTestPsicologicoDetalle.idtestpsicologico, '.', CandidatoTestPsicologicoDetalle.idparte, '.', CandidatoTestPsicologicoDetalle.idpregunta)
                            ).filter(
                                CandidatoTestPsicologicoDetalle.idcandidato==idcandidato
                            )
            
            _subquery_preguntas_no_respondidas_por_falta_tiempo = db.session.query(
                                func.concat(TestPsicologicoPreguntas.idtestpsicologico, '.', TestPsicologicoPreguntas.idparte, '.', TestPsicologicoPreguntas.idpregunta)
                            ).outerjoin(TestPsicologicoInstrucciones, 
                                TestPsicologicoInstrucciones.idtestpsicologico==TestPsicologicoPreguntas.idtestpsicologico
                            ).filter(
                                TestPsicologicoInstrucciones.idparte==TestPsicologicoPreguntas.idparte, # JOIN
                                func.concat(TestPsicologicoPreguntas.idtestpsicologico, '.', TestPsicologicoPreguntas.idparte).in_(
                                    db.session.query(
                                        func.concat(TestPsicologicoInstrucciones.idtestpsicologico, '.', TestPsicologicoInstrucciones.idparte)
                                    ).outerjoin(CandidatoTestPsicologicoDetalle, 
                                        TestPsicologicoInstrucciones.idtestpsicologico==CandidatoTestPsicologicoDetalle.idtestpsicologico
                                    ).filter(
                                            CandidatoTestPsicologicoDetalle.idcandidato==idcandidato,
                                            TestPsicologicoInstrucciones.idparte==CandidatoTestPsicologicoDetalle.idparte # JOIN
                                    ).distinct()
                                ),
                                TestPsicologicoInstrucciones.duracion > 0,
                                TestPsicologicoInstrucciones.tipoprueba != 'Preg.Abierta',
                                func.concat(TestPsicologicoPreguntas.idtestpsicologico, '.', TestPsicologicoPreguntas.idparte, '.', TestPsicologicoPreguntas.idpregunta).notin_(
                                    db.session.query(
                                        func.concat(CandidatoTestPsicologicoDetalle.idtestpsicologico, '.', CandidatoTestPsicologicoDetalle.idparte, '.', CandidatoTestPsicologicoDetalle.idpregunta)
                                    ).filter(CandidatoTestPsicologicoDetalle.idcandidato==idcandidato)
                                )
                            )
            _subquery_preguntas_respondidas = _subquery_preguntas_respondidas.union(_subquery_preguntas_no_respondidas_por_falta_tiempo)

            candidato_respuestas = db.session.query(
                                TestPsicologicoPreguntas.idtestpsicologico,
                                TestPsicologicoPreguntas.idparte,
                                TestPsicologicoPreguntas.idpregunta,
                                TestPsicologicoPreguntas.enunciado,
                                TestPsicologicoPreguntas.alternativa
                            ).filter(
                                TestPsicologicoPreguntas.idtestpsicologico.in_(_subquery_testpsicologicos_asignados),
                                func.concat(TestPsicologicoPreguntas.idtestpsicologico, '.', TestPsicologicoPreguntas.idparte, '.', TestPsicologicoPreguntas.idpregunta
                                    ).notin_(_subquery_preguntas_respondidas)
                            ).order_by(TestPsicologicoPreguntas.idtestpsicologico, 
                                TestPsicologicoPreguntas.idparte, 
                                TestPsicologicoPreguntas.idpregunta)
            
            testpsicologicos_asignados = db.session.query(
                                                CandidatoTestPsicologico.idcandidato,
                                                CandidatoTestPsicologico.idtestpsicologico,
                                                CandidatoTestPsicologico.fechaexamen,
                                                TestPsicologicoInstrucciones.idparte
                                            ).outerjoin(TestPsicologicoInstrucciones, 
                                                TestPsicologicoInstrucciones.idtestpsicologico==CandidatoTestPsicologico.idtestpsicologico
                                            ).filter(CandidatoTestPsicologico.idcandidato==idcandidato
                                            ).order_by(CandidatoTestPsicologico.idtestpsicologico, TestPsicologicoInstrucciones.idparte)
        except AssertionError as e:
            print(e)
            print('Error al recuperar las respuestas del candidato {}'.format(idcandidato))
            return None, '', None, None, None

        if candidato_respuestas.count() > 0:
            print('El candidato {} posee preguntas pendientes para los test {}'.format(idcandidato, id_testpsicologicos))
            candidato_respuestas_idtestpsicologico_idparte_lista = set()
            for candidato_respuesta in candidato_respuestas:
                #print('Respuestas de un candidato: {}'.format(candidato_respuesta))
                idtestpsicologico = int(candidato_respuesta.idtestpsicologico)
                idparte = int(candidato_respuesta.idparte)
                candidato_respuestas_idtestpsicologico_idparte_lista.add('{}.{}'.format(idtestpsicologico, idparte))
            candidato_respuestas_idtestpsicologico_idparte_lista = list(candidato_respuestas_idtestpsicologico_idparte_lista)
            candidato_respuestas_idtestpsicologico_idparte_lista.sort()

            print('Lista de partes de las preguntas pendientes del candidato {}: {}'.format(idcandidato, candidato_respuestas_idtestpsicologico_idparte_lista))
            print('Lista de respuestas del candidato {}: {}'.format(idcandidato, candidato_respuestas_idtestpsicologico_idparte_lista))
            flag, testpsicologico_instrucciones, mensaje_obtener_instrucciones = self.obtener_instrucciones(id_testpsicologicos, candidato_respuestas_idtestpsicologico_idparte_lista)
            if flag == False:
                return None, 'No hay instrucciones para el test psicológico.', None, None, None

            try:
                response = candidato_respuestas
            except:
                print('Error al recuperar las preguntas del test psicológico.')
                return None, 'Error al recuperar las preguntas del test psicológico.', None, None, None
            
            else:
                return True, response, testpsicologico_instrucciones, testpsicologicos_asignados, mensaje_obtener_instrucciones
        else:
            print('El candidato {} no tiene preguntas pendientes.'.format(idcandidato))
            return False, 'El candidato {} no tiene preguntas pendientes.'.format(idcandidato), None, None, None
    
    def valida_lista_test_psicologicos(self, idcandidato, lista_test_psicologicos):
        try:
            reclutador_notificacion = db.session.query(
                                        ReclutadorNotificacion
                                    ).filter(ReclutadorNotificacion.idcandidato==idcandidato
                                    ).order_by(desc(ReclutadorNotificacion.fechanotificacion))
            if reclutador_notificacion.count() > 0:
                print('Se encontró notificaciones para el candidato {}'.format(idcandidato))
                reclutador_notificacion_ultimo = reclutador_notificacion.first()
                print('La lista de test recibida del candidato {} es {}'.format(idcandidato, lista_test_psicologicos))
                print('La lista de test obtenida del candidato {} es {}'.format(idcandidato, reclutador_notificacion_ultimo.testpsicologico))
                if lista_test_psicologicos == reclutador_notificacion_ultimo.testpsicologico:
                    print('Las listas de test psicológicos son iguales.')
                    return False
            print('Las listas de test psicológicos son diferentes')
            
            new_reclutador_notificacion = ReclutadorNotificacion(idcandidato, json.dumps(lista_test_psicologicos), func.now())
            db.session.add(new_reclutador_notificacion)
            db.session.commit()

            return True
        except AssertionError as error:
            print(error)
            print('Error al validar lista de test psicologicos.')
            return False