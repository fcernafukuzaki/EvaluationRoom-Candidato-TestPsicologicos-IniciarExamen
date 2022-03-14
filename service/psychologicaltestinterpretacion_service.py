import os
from common.util import get_response_body, invoke_api

class PsychologicalTestInterpretacionService():

    def getinterpretacion(self, idcandidato=None):
        try:
            api = os.environ['API']
            print("PsychologicalTestInterpretacionController:{}|{}".format(idcandidato,api))
            if idcandidato:
                url = f'{api}/testpsicologico/interpretacion/candidato/{idcandidato}'
                print(url)
                response = invoke_api(url, body=None, method='GET')
                print('Resultado de API: {} {}'.format(response.status, response.data))
                response_body = {'mensaje':"OK"}
                return get_response_body(code=200, message="OK", user_message="OK", body=response_body), 200
        except Exception as e:
            message = f'Hubo un error durante la consulta del usuario {e}'
            return get_response_body(code=503, message=message, user_message=message), 503
