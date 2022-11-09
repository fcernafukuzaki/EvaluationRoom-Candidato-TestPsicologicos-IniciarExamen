from configs.flask_config import db, ma


class CandidatoLog(db.Model):
    __table_args__ = {"schema": "evaluationroom"}
    __tablename__ = 'candidato_log'

    fecharegistro = db.Column(db.DateTime(), primary_key=True)
    idcandidato = db.Column(db.Integer, primary_key=True)
    accion = db.Column(db.String())
    detalle = db.Column(db.String())
    origin = db.Column(db.String())
    host = db.Column(db.String())
    user_agent = db.Column(db.String())

    def __init__(self, fecharegistro, idcandidato, accion, detalle, origin=None, host=None, user_agent=None):
        self.fecharegistro = fecharegistro
        self.idcandidato = idcandidato
        self.accion = accion
        self.detalle = detalle
        self.origin = origin
        self.host = host
        self.user_agent = user_agent


class CandidatoLogSchema(ma.Schema):
    class Meta:
        fields = ('fecharegistro', 'idcandidato', 'accion', 'detalle')
