from configs.flask_config import db, ma

class ReclutadorNotificacion(db.Model):
    __table_args__ = {"schema": "evaluationroom", 'extend_existing': True}
    __tablename__ = 'reclutador_notificacion'
    
    idcandidato = db.Column(db.Integer, db.ForeignKey('evaluationroom.candidato.idcandidato'), primary_key=True)
    testpsicologico = db.Column(db.String())
    fechanotificacion = db.Column(db.DateTime(), primary_key=True)

    def __init__(self, idcandidato, testpsicologico, fechanotificacion):
        self.idcandidato = idcandidato
        self.testpsicologico = testpsicologico
        self.fechanotificacion = fechanotificacion
    
class ReclutadorNotificacionSchema(ma.Schema):
    class Meta:
        fields = ('idcandidato', 'testpsicologico', 'fechanotificacion')