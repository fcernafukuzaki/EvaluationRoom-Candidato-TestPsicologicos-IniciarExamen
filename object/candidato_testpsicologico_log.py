from configs.flask_config import db, ma


class CandidatoTestPsicologicoLog(db.Model):
    __table_args__ = {"schema": "evaluationroom"}
    __tablename__ = 'candidatotest_log'

    idcandidato = db.Column(db.Integer, db.ForeignKey('evaluationroom.candidato.idcandidato'), primary_key=True)
    idtestpsicologico = db.Column(db.Integer, db.ForeignKey('evaluationroom.candidatotest.idtestpsicologico'), primary_key=True)
    idparte = db.Column(db.Integer, primary_key=True)
    fechainicio = db.Column(db.DateTime(), primary_key=True)
    fechafin = db.Column(db.DateTime())

    def __init__(self, idcandidato, idtestpsicologico, idparte, fechainicio, fechafin=None):
        self.idcandidato = idcandidato
        self.idtestpsicologico = idtestpsicologico
        self.idparte = idparte
        self.fechainicio = fechainicio
        self.fechafin = fechafin


class CandidatoTestPsicologicoLogSchema(ma.Schema):
    class Meta:
        fields = ('idcandidato', 'idtestpsicologico', 'idparte', 'fechainicio', 'fechafin')
