from flask import jsonify
from configs.flask_config import db
from sqlalchemy import func
from object.candidato import Candidato, CandidatoInfo, CandidatoSchema
from object.candidato_testpsicologico import CandidatoTestPsicologico
from object.testpsicologico_instrucciones import TestPsicologicoInstrucciones, TestPsicologicoInstruccionesSchema
from object.mensaje_procesoseleccion_candidato import MensajeProcesoseleccionCandidato
from object.testpsicologico_preguntas import TestPsicologicoPreguntas, TestPsicologicoPreguntasSchema
from object.candidato_testpsicologicodetalle import CandidatoTestPsicologicoDetalle
import json
import ast
import urllib3

candidato_schema = CandidatoSchema()
testpsicologico_instrucciones_schema = TestPsicologicoInstruccionesSchema(many=True)
testpsicologico_preguntas_schema = TestPsicologicoPreguntasSchema(many=True)

class IniciarExamenService():

    def iniciar_examen(self, email):
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
            return {'mensaje': mensaje}, 202

        testpsicologicos_lista = []
        for test in candidato.testpsicologicos:
            testpsicologicos_lista.append(test.idtestpsicologico)

        flag, mensaje_bienvenida = self.obtener_mensaje_bienvenida(candidato.nombre)
        flag, preguntas_pendientes, testpsicologicos_instrucciones = self.obtener_preguntas_pendientes(candidato.idcandidato, testpsicologicos_lista)
        if flag:
            resultado_preguntas_pendientes = preguntas_pendientes
            resultado_testpsicologicos_instrucciones = testpsicologicos_instrucciones
            return {'mensaje_bienvenida': mensaje_bienvenida, 'candidato': candidato_schema.dump(candidato_info), 'testpsicologicos_instrucciones': testpsicologico_instrucciones_schema.dump(resultado_testpsicologicos_instrucciones), 'preguntas_pendientes': testpsicologico_preguntas_schema.dump(resultado_preguntas_pendientes) }, 200
            #return candidato_schema.jsonify(candidato_info)
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
                                                ).filter(TestPsicologicoInstrucciones.idtestpsicologico.in_((idtestpsicologicos_lista)),
                                                    func.concat(TestPsicologicoInstrucciones.idtestpsicologico, '.', TestPsicologicoInstrucciones.idparte).notin_((idtestpsicologicos_idparte_lista))
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
            candidato_respuestas = db.session.query(
                                        CandidatoTestPsicologicoDetalle
                                    ).filter(
                                        CandidatoTestPsicologicoDetalle.idcandidato == idcandidato
                                    ).order_by(CandidatoTestPsicologicoDetalle.idtestpsicologico, CandidatoTestPsicologicoDetalle.idparte, CandidatoTestPsicologicoDetalle.idpregunta)
        except:
            print('Error al recuperar las respuestas del candidato {}'.format(idcandidato))
            return False, '', None

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

            print('Lista de respuestas del candidato {}: {}'.format(idcandidato, candidato_respuestas_idtestpsicologico_idparte_lista))
            flag, testpsicologico_instrucciones = self.obtener_instrucciones(id_testpsicologicos, candidato_respuestas_idtestpsicologico_idparte_lista)
            if flag == False:
                return False, 'No hay instrucciones para el test psicológico.', None

            try:
                response = db.session.query(
                                TestPsicologicoPreguntas
                            ).filter(
                                func.concat(TestPsicologicoPreguntas.idtestpsicologico, '.', TestPsicologicoPreguntas.idparte).notin_(candidato_respuestas_idtestpsicologico_idparte_lista)
                            ).order_by(TestPsicologicoPreguntas.idtestpsicologico, TestPsicologicoPreguntas.idparte, TestPsicologicoPreguntas.idpregunta)
            except:
                print('Error al recuperar las preguntas del test psicológico.')
                return False, 'Error al recuperar las preguntas del test psicológico.', None
            
            else:
                return True, response, testpsicologico_instrucciones
        else:
            flag, testpsicologico_instrucciones = self.obtener_instrucciones(id_testpsicologicos)
            if flag == False:
                return False, 'No hay instrucciones para el test psicológico.', None

            try:
                response = db.session.query(
                                TestPsicologicoPreguntas
                            ).filter(
                                TestPsicologicoPreguntas.idtestpsicologico.in_(id_testpsicologicos)
                            ).order_by(TestPsicologicoPreguntas.idtestpsicologico, TestPsicologicoPreguntas.idparte, TestPsicologicoPreguntas.idpregunta)
            except:
                print('Error al recuperar las preguntas del test psicológico.')
                return False, 'Error al recuperar las preguntas del test psicológico.', None
            else:
                return True, response, testpsicologico_instrucciones