from configs.flask_config import db, ma
from object.candidato_testpsicologicodetalle import CandidatoTestPsicologicoDetalle, CandidatoTestPsicologicoDetalleSchema


class CandidatoTestPsicologico(db.Model):
    __table_args__ = {"schema": "evaluationroom"}
    __tablename__ = 'candidatotest'

    idcandidato = db.Column(db.Integer, db.ForeignKey('evaluationroom.candidato.idcandidato'), primary_key=True)
    idtestpsicologico = db.Column(db.Integer, primary_key=True)
    fechaexamen = db.Column(db.DateTime)

    testpsicologicosdetalle = db.relationship('CandidatoTestPsicologicoDetalle', lazy="dynamic",
                                         primaryjoin='and_(CandidatoTestPsicologico.idtestpsicologico==CandidatoTestPsicologicoDetalle.idtestpsicologico)')

    def __init__(self, idcandidato, idtestpsicologico, fechaexamen=None):
        self.idcandidato = idcandidato
        self.idtestpsicologico = idtestpsicologico
        self.fechaexamen = fechaexamen


class CandidatoTestPsicologicoSchema(ma.Schema):
    class Meta:
        fields = ('idcandidato', 'idtestpsicologico', 'fechaexamen', 'idparte')
    
    testpsicologicosdetalle = ma.Nested(CandidatoTestPsicologicoDetalleSchema, many=True)
