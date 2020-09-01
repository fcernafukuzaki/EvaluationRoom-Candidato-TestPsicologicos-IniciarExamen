from configs.flask_config import db, ma


class CandidatoTestPsicologico(db.Model):
    __table_args__ = {"schema": "evaluationroom"}
    __tablename__ = 'candidatotest'

    idcandidato = db.Column(db.Integer, db.ForeignKey('evaluationroom.candidato.idcandidato'), primary_key=True)
    idtestpsicologico = db.Column(db.Integer, 
                                  primary_key=True)
    fechaexamen = db.Column(db.DateTime)

    def __init__(self, idcandidato, idtestpsicologico, fechaexamen=None):
        self.idcandidato = idcandidato
        self.idtestpsicologico = idtestpsicologico
        self.fechaexamen = fechaexamen


class CandidatoTestPsicologicoSchema(ma.Schema):
    class Meta:
        fields = ('idcandidato', 'idtestpsicologico', 'fechaexamen')
