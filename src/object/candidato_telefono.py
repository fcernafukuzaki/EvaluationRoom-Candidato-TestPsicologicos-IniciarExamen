from configs.flask_config import db, ma
from object.telefono import Telefono, TelefonoSchema


class CandidatoTelefono(db.Model):
    __table_args__ = {"schema": "evaluationroom"}
    __tablename__ = 'candidatotelefono'

    idcandidato = db.Column(db.Integer, db.ForeignKey('evaluationroom.candidato.idcandidato'), primary_key=True)
    idtelefono = db.Column(db.Integer, db.ForeignKey('evaluationroom.telefono.idtelefono'), primary_key=True)
    numero = db.Column(db.String())

    telefono = db.relationship('Telefono',
                                primaryjoin='and_(Candidato.idcandidato==CandidatoTelefono.idcandidato, '
                                            'CandidatoTelefono.idtelefono==Telefono.idtelefono)')

    def __init__(self, id_candidato, id_telephone, number=None):
        self.idcandidato = id_candidato
        self.idtelefono = id_telephone
        self.numero = number


class CandidatoTelefonoSchema(ma.Schema):
    class Meta:
        fields = ('idcandidato', 'idtelefono', 'numero', 'telefono')

    telefono = ma.Nested(TelefonoSchema)