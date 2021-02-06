from configs.flask_config import db, ma

class TestPsicologicoInstrucciones(db.Model):
    __table_args__ = {"schema": "evaluationroom"}
    __tablename__ = 'testpsicologicoparte'
    
    idtestpsicologico = db.Column(db.Integer, primary_key=True)
    idparte = db.Column(db.Integer, primary_key=True)
    instrucciones = db.Column(db.String())
    alternativamaxseleccion = db.Column(db.Integer())
    duracion = db.Column(db.Integer)

    def __init__(self, idtestpsicologico, idparte=1, instrucciones=None, alternativa_maxima_seleccion=1, duracion_segundos=0):
        self.idtestpsicologico = idtestpsicologico
        self.idparte = idparte
        self.instrucciones = instrucciones
        self.alternativamaxseleccion = alternativa_maxima_seleccion
        self.duracion = duracion_segundos
    
class TestPsicologicoInstruccionesSchema(ma.Schema):
    class Meta:
        fields = ('idtestpsicologico', 'idparte', 'instrucciones', 'alternativa_maxima_seleccion', 'duracion_segundos')