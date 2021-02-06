from configs.flask_config import db, ma

class TestPsicologicoPreguntas(db.Model):
    __table_args__ = {"schema": "evaluationroom"}
    __tablename__ = 'testpsicologicopregunta'
    
    idtestpsicologico = db.Column(db.Integer, primary_key=True)
    idparte = db.Column(db.Integer, primary_key=True)
    idpregunta = db.Column(db.Integer, primary_key=True)
    enunciado = db.Column(db.String())
    alternativa = db.Column(db.String())

    def __init__(self, idtestpsicologico, idparte, idpregunta, enunciado, alternativa):
        self.idtestpsicologico = idtestpsicologico
        self.idparte = idparte
        self.idpregunta = idpregunta
        self.enunciado = enunciado
        self.alternativa = alternativa
    
class TestPsicologicoPreguntasSchema(ma.Schema):
    class Meta:
        fields = ('idtestpsicologico', 'idparte', 'idpregunta', 'enunciado', 'alternativa')