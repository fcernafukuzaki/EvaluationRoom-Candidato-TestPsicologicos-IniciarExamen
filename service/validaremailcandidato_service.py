import json
import ast
import urllib3

class ValidarEmailCandidatoService():

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