class AutorizadorService:

    def validar_token(self, token):
        if token:
            return True
        return False