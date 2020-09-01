from flask import jsonify
from configs.flask_config import db
from configs.dynamodb_config import dynamodb
from object.candidato import Candidato, CandidatoSchema
from object.candidato_testpsicologico import CandidatoTestPsicologico
from common.DecimalEncoder import *
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr
import json
import ast

candidato_schema = CandidatoSchema()

class IniciarExamenService():

    def iniciar_examen(self, email):
        email_valido, idcandidato = self.valida_email_candidato(email)
        
        if email_valido == False:
            return {'mensaje': 'No existe candidato.'}, 404

        candidato = self.obtener_candidato(idcandidato, email)

        flag_autoregistro = self.valida_autoregistro(email, candidato.selfregistration)
        if flag_autoregistro == False:
            return candidato_schema.jsonify(candidato)

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
            resultado_preguntas_pendientes = ast.literal_eval(json.dumps(preguntas_pendientes, cls=DecimalEncoder))
            resultado_testpsicologicos_instrucciones = ast.literal_eval(json.dumps(testpsicologicos_instrucciones, cls=DecimalEncoder))
            return {'mensaje_bienvenida': mensaje_bienvenida, 'testpsicologicos_instrucciones': resultado_testpsicologicos_instrucciones, 'preguntas_pendientes': resultado_preguntas_pendientes }, 200
        return {'mensaje': 'Error al recuperar las instrucciones de los test psicológicos.'}, 500

    def valida_email_candidato(self, email):
        idcandidato = db.session.query(Candidato.idcandidato).filter(Candidato.correoelectronico==email)
        if idcandidato.count() > 0:
            print('Se encontró candidato con el correo electronico {}'.format(email))
            return True, idcandidato
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
        if candidato:
            print('Se encontró candidato con el identificador {}'.format(email))
            return candidato
        print('No existe candidato con el identificador {}'.format(email))
        return None

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
        tabla_testpsicologico_instrucciones = dynamodb.Table('TestPsicologico_Instrucciones')

        try:
            if idtestpsicologicos_idparte_lista:
                testpsicologico_instrucciones = tabla_testpsicologico_instrucciones.query(
                    KeyConditionExpression=Key('id_testpsicologico').eq(0),
                    FilterExpression=Attr('idtestpsicologico').is_in(idtestpsicologicos_lista) & ~Attr('idtestpsicologico_idparte').is_in(idtestpsicologicos_idparte_lista)
                )
            else:
                testpsicologico_instrucciones = tabla_testpsicologico_instrucciones.query(
                    KeyConditionExpression=Key('id_testpsicologico').eq(0),
                    FilterExpression=Attr('idtestpsicologico').is_in(idtestpsicologicos_lista),
                )
        except ClientError as e:
            print(e.response['Error']['Message'])
            return False, e.response['Error']['Message']
        else:
            print('Se recupera instrucciones de los test {} (Partes: {})'.format(idtestpsicologicos_lista, idtestpsicologicos_idparte_lista))
            return True, testpsicologico_instrucciones['Items']

    def obtener_mensaje_bienvenida(self, nombre):
        tabla_mensaje_procesoseleccion_candidato = dynamodb.Table('Mensaje_ProcesoSeleccion_Candidato')

        try:
            mensaje_procesoseleccion_candidato = tabla_mensaje_procesoseleccion_candidato.query(
                KeyConditionExpression=Key('id').eq(0) & Key('id_mensaje').eq(1)
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
            return False, e.response['Error']['Message']
        else:
            print('El candidato {} va a iniciar el examen (mensaje de bienvenida)'.format(nombre))
            if len(mensaje_procesoseleccion_candidato['Items']) > 0:
                for mensaje in mensaje_procesoseleccion_candidato['Items']:
                    return True, mensaje['mensaje'].format(nombre)
            return False, None

    def obtener_mensaje_felicitaciones(self, nombre):
        tabla_mensaje_procesoseleccion_candidato = dynamodb.Table('Mensaje_ProcesoSeleccion_Candidato')

        try:
            mensaje_procesoseleccion_candidato = tabla_mensaje_procesoseleccion_candidato.query(
                KeyConditionExpression=Key('id').eq(0) & Key('id_mensaje').eq(2)
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
            return False, e.response['Error']['Message']
        else:
            print('El candidato {} ha finalizado los test psicológicos asignados'.format(nombre))
            if len(mensaje_procesoseleccion_candidato['Items']) > 0:
                for mensaje in mensaje_procesoseleccion_candidato['Items']:
                    return True, mensaje['mensaje'].format(nombre)
            return False, None

    def obtener_preguntas_pendientes(self, idcandidato, id_testpsicologicos):
        tabla_testpsicologico_pregunta = dynamodb.Table('TestPsicologico_Pregunta')
        tabla_candidato_respuesta = dynamodb.Table('Candidato_Respuesta')

        try:
            candidato_respuestas = tabla_candidato_respuesta.query(
                KeyConditionExpression = Key('idcandidato').eq(idcandidato)
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
            return False, e.response['Error']['Message'], None

        if len(candidato_respuestas['Items']) > 0:
            print('El candidato {} posee preguntas pendientes para los test {}'.format(idcandidato, id_testpsicologicos))
            candidato_respuestas_idtestpsicologico_idparte_lista = []
            for candidato_respuesta in candidato_respuestas['Items']:
                idtestpsicologico = int(candidato_respuesta['idtestpsicologico'])
                idparte = int(candidato_respuesta['idparte'])
                candidato_respuestas_idtestpsicologico_idparte_lista.append('{}.{}'.format(idtestpsicologico, idparte))

            print('Lista de respuestas del candidato {}: {}'.format(idcandidato, candidato_respuestas_idtestpsicologico_idparte_lista))
            flag, testpsicologico_instrucciones = self.obtener_instrucciones(id_testpsicologicos, candidato_respuestas_idtestpsicologico_idparte_lista)
            if flag == False:
                return False, 'No hay instrucciones para el test psicológico.', None

            try:
                response = tabla_testpsicologico_pregunta.query(
                    KeyConditionExpression=Key('id_testpsicologico').eq(0),
                    FilterExpression=~Attr('id_testpsicologico_idparte').is_in(candidato_respuestas_idtestpsicologico_idparte_lista)
                )
            except ClientError as e:
                print(e.response['Error']['Message'])
                return False, e.response['Error']['Message'], None
            else:
                return True, response['Items'], testpsicologico_instrucciones
        else:
            flag, testpsicologico_instrucciones = self.obtener_instrucciones(id_testpsicologicos)
            if flag == False:
                return False, 'No hay instrucciones para el test psicológico.', None

            try:
                response = tabla_testpsicologico_pregunta.query(
                    KeyConditionExpression='id_testpsicologico = :id_testpsicologico',
                    FilterExpression=Attr('idtestpsicologico').is_in(id_testpsicologicos),
                    ExpressionAttributeValues={
                        ':id_testpsicologico': 0
                    }
                )
            except ClientError as e:
                print(e.response['Error']['Message'])
                return False, e.response['Error']['Message'], None
            else:
                return True, response['Items'], testpsicologico_instrucciones