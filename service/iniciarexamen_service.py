from flask import jsonify
from configs.flask_config import db
from sqlalchemy import func
from sqlalchemy import desc
from object.candidato import Candidato, CandidatoInfo, CandidatoSchema
from object.candidato_testpsicologico import CandidatoTestPsicologico, CandidatoTestPsicologicoSchema
from object.testpsicologico_instrucciones import TestPsicologicoInstrucciones, TestPsicologicoInstruccionesSchema
from object.mensaje_procesoseleccion_candidato import MensajeProcesoseleccionCandidato
from object.testpsicologico_preguntas import TestPsicologicoPreguntas, TestPsicologicoPreguntasSchema
from object.candidato_testpsicologicodetalle import CandidatoTestPsicologicoDetalle
from object.reclutador_notificacion import ReclutadorNotificacion
import json
import ast
import urllib3

candidato_schema = CandidatoSchema()
candidato_testpsicologico_schema = CandidatoTestPsicologicoSchema(many=True)
testpsicologico_instrucciones_schema = TestPsicologicoInstruccionesSchema(many=True)
testpsicologico_preguntas_schema = TestPsicologicoPreguntasSchema(many=True)

class IniciarExamenService():

    def iniciar_examen(self, email, lista_test_psicologicos):
        email_valido, idcandidato = self.valida_email_candidato(email)
        
        if email_valido == False:
            return {'mensaje': 'No existe candidato.'}, 404

        candidato, candidato_info = self.obtener_candidato(idcandidato, email)
        
        flag_autoregistro = self.valida_autoregistro(email, candidato.selfregistration)
        #if flag_autoregistro == False:
        #    return candidato_schema.jsonify(candidato)

        flag, testpsicologicos_pendientes = self.obtener_testpsicologicos_pendientes(idcandidato, email)
        if flag == False:
            flag, mensaje = self.obtener_mensaje_felicitaciones(candidato.nombre)
            reclutador_notificado = False
            if len(lista_test_psicologicos) > 0:
                reclutador_notificado = self.valida_lista_test_psicologicos(idcandidato, lista_test_psicologicos)
            return {'mensaje': mensaje,
                    'reclutador_notificado': reclutador_notificado}, 202

        testpsicologicos_lista = []
        for test in candidato.testpsicologicos:
            testpsicologicos_lista.append(test.idtestpsicologico)

        flag, mensaje_bienvenida = self.obtener_mensaje_bienvenida(candidato.nombre)
        flag, preguntas_pendientes, testpsicologicos_instrucciones, testpsicologicos_asignados = self.obtener_preguntas_pendientes(candidato.idcandidato, testpsicologicos_lista)
        if flag:
            resultado_preguntas_pendientes = preguntas_pendientes
            resultado_testpsicologicos_instrucciones = testpsicologicos_instrucciones
            return {'mensaje_bienvenida': mensaje_bienvenida, 
                    'candidato': candidato_schema.dump(candidato_info), 
                    'testpsicologicos_asignados': candidato_testpsicologico_schema.dump(testpsicologicos_asignados),
                    'testpsicologicos_instrucciones': testpsicologico_instrucciones_schema.dump(resultado_testpsicologicos_instrucciones), 
                    'preguntas_pendientes': testpsicologico_preguntas_schema.dump(resultado_preguntas_pendientes) }, 200
        return {'mensaje': 'Error al recuperar las instrucciones de los test psicológicos.'}, 500

    def valida_email_candidato(self, email):
        http = urllib3.PoolManager()
        url = 'https://api.evaluationroom.com/candidato_email_validar/'
        response = http.request('GET',
                                url,
                                headers={'Content-Type': 'application/json', 'Authorization': email},
                                retries=False)
        print('Resultado de API: {} {}'.format(response.status, response.data))
        if response.status == 200:
            print('Se encontró candidato con el correo electronico {}'.format(email))
            return True, json.loads(response.data.decode('utf-8'))['idcandidato']
        print('No existe candidato con el correo electronico {}'.format(email))
        return False, None

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
                                        db.func.extract('year', CandidatoTestPsicologico.fechaexamen) == 1900,
                                        db.func.extract('month', CandidatoTestPsicologico.fechaexamen) == 1,
                                        db.func.extract('day', CandidatoTestPsicologico.fechaexamen) == 1
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
            print('Error al recuperar las instrucciones del test psicológico.')
            return False, 'Error al recuperar las instrucciones del test psicológico.'
        else:
            print('Se recupera instrucciones de los test {} (Partes: {})'.format(idtestpsicologicos_lista, idtestpsicologicos_idparte_lista))
            return True, testpsicologico_instrucciones

    def obtener_mensaje_bienvenida(self, nombre):
        try:
            mensaje_procesoseleccion_candidato = db.session.query(
                                                    MensajeProcesoseleccionCandidato
                                                ).filter(MensajeProcesoseleccionCandidato.id_mensaje == 1
                                                ).order_by(MensajeProcesoseleccionCandidato.id_mensaje)
        except:
            print('Error al recuperar el mensaje de bienvenida del candidato.')
            return False, 'Error al recuperar el mensaje de bienvenida del candidato.'
        else:
            print('El candidato {} va a iniciar el examen (mensaje de bienvenida)'.format(nombre))
            if mensaje_procesoseleccion_candidato.count() > 0:
                for mensaje in mensaje_procesoseleccion_candidato:
                    return True, mensaje.mensaje.format(nombre)
            return False, None

    def obtener_mensaje_felicitaciones(self, nombre):
        try:
            mensaje_procesoseleccion_candidato = db.session.query(
                                                    MensajeProcesoseleccionCandidato
                                                ).filter(MensajeProcesoseleccionCandidato.id_mensaje == 2
                                                ).order_by(MensajeProcesoseleccionCandidato.id_mensaje)
        except:
            print('Error al recuperar el mensaje de felicitaciones del candidato.')
            return False, 'Error al recuperar el mensaje de felicitaciones del candidato.'
        else:
            print('El candidato {} ha finalizado los test psicológicos asignados'.format(nombre))
            if mensaje_procesoseleccion_candidato.count() > 0:
                for mensaje in mensaje_procesoseleccion_candidato:
                    return True, mensaje.mensaje.format(nombre)
            return False, None

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
                                                CandidatoTestPsicologico
                                            ).filter(CandidatoTestPsicologico.idcandidato==idcandidato
                                            ).order_by(CandidatoTestPsicologico.idtestpsicologico)
        except AssertionError as e:
            print(e)
            print('Error al recuperar las respuestas del candidato {}'.format(idcandidato))
            return False, '', None, None

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
            flag, testpsicologico_instrucciones = self.obtener_instrucciones(id_testpsicologicos, candidato_respuestas_idtestpsicologico_idparte_lista)
            if flag == False:
                return False, 'No hay instrucciones para el test psicológico.', None, None

            try:
                response = candidato_respuestas
            except:
                print('Error al recuperar las preguntas del test psicológico.')
                return False, 'Error al recuperar las preguntas del test psicológico.', None, None
            
            else:
                return True, response, testpsicologico_instrucciones, testpsicologicos_asignados
        else:
            flag, testpsicologico_instrucciones = self.obtener_instrucciones(id_testpsicologicos)
            if flag == False:
                return False, 'No hay instrucciones para el test psicológico.', None, None

            try:
                response = db.session.query(
                                TestPsicologicoPreguntas
                            ).filter(
                                TestPsicologicoPreguntas.idtestpsicologico.in_(id_testpsicologicos)
                            ).order_by(TestPsicologicoPreguntas.idtestpsicologico, TestPsicologicoPreguntas.idparte, TestPsicologicoPreguntas.idpregunta)
            except:
                print('Error al recuperar las preguntas del test psicológico.')
                return False, 'Error al recuperar las preguntas del test psicológico.', None, None
            else:
                return True, response, testpsicologico_instrucciones, testpsicologicos_asignados
    
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