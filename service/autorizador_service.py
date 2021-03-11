class AutorizadorService:

    def validar_token(self, token):
        if token:
            return True
        return False

    def obtener_header(self, request_headers):
        origin = None
        if 'Origin' in request_headers:
            origin = request_headers['Origin']
        
        host = None
        if 'Host' in request_headers:
            host = request_headers['Host']
        
        user_agent = None
        if 'User-Agent' in request_headers:
            user_agent = request_headers['User-Agent']
        
        return origin, host, user_agent