from configs.flask_config import db, ma


class CandidatoTestPsicologicoDetalle(db.Model):
    __table_args__ = {"schema": "evaluationroom"}
    __tablename__ = 'candidatotestdetalle'

    idcandidato = db.Column(db.Integer, db.ForeignKey('evaluationroom.candidato.idcandidato'), primary_key=True)
    idtestpsicologico = db.Column(db.Integer, db.ForeignKey('evaluationroom.candidatotest.idtestpsicologico'), primary_key=True)
    idparte = db.Column(db.Integer, primary_key=True)
    idpregunta = db.Column(db.Integer, primary_key=True)
    respuesta = db.Column(db.String())
    fecharegistro = db.Column(db.DateTime(), primary_key=True)
    origin = db.Column(db.String())
    host = db.Column(db.String())
    user_agent = db.Column(db.String())

    def __init__(self, idcandidato, idtestpsicologico, idparte, idpregunta, respuesta, fecharegistro, origin=None, host=None, user_agent=None):
        self.idcandidato = idcandidato
        self.idtestpsicologico = idtestpsicologico
        self.idparte = idparte
        self.idpregunta = idpregunta
        self.respuesta = respuesta
        self.fecharegistro = fecharegistro
        self.origin = origin
        self.host = host
        self.user_agent = user_agent


class CandidatoTestPsicologicoDetalleSchema(ma.Schema):
    class Meta:
        fields = ('idcandidato', 'idtestpsicologico', 'idparte', 'idpregunta', 'respuesta', 'fecharegistro')
