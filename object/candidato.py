from configs.flask_config import db, ma
from sqlalchemy import func
from object.candidato_testpsicologico import CandidatoTestPsicologico, CandidatoTestPsicologicoSchema
from object.candidato_telefono import CandidatoTelefono, CandidatoTelefonoSchema
from object.candidato_direccion import CandidatoDireccion, CandidatoDireccionSchema

class Candidato(db.Model):
    __table_args__ = {"schema": "evaluationroom"}
    __tablename__ = 'candidato'

    idcandidato = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String())
    apellidopaterno = db.Column(db.String())
    apellidomaterno = db.Column(db.String())
    fechanacimiento = db.Column(db.DateTime)
    correoelectronico = db.Column(db.String())
    selfregistration = db.Column(db.Boolean())

    telefonos = db.relationship('CandidatoTelefono', lazy="dynamic",
                                 primaryjoin='and_(Candidato.idcandidato==CandidatoTelefono.idcandidato)')

    direcciones = db.relationship('CandidatoDireccion', lazy="dynamic",
                                 primaryjoin='and_(Candidato.idcandidato==CandidatoDireccion.idcandidato)')

    testpsicologicos = db.relationship('CandidatoTestPsicologico', lazy="dynamic",
                                         primaryjoin='and_(Candidato.idcandidato==CandidatoTestPsicologico.idcandidato)')

    def __init__(self, nombre, apellidopaterno, apellidomaterno, fechanacimiento, correoelectronico, selfregistration):
        self.nombre = nombre
        self.apellidopaterno = apellidopaterno
        self.apellidomaterno = apellidomaterno
        self.fechanacimiento = fechanacimiento
        self.correoelectronico = correoelectronico
        self.selfregistration = selfregistration

class CandidatoInfo():

    def candidato_info(idcandidato):
        return db.session.query(
            Candidato.idcandidato,
            Candidato.nombre,
            Candidato.apellidopaterno,
            Candidato.apellidomaterno,
            Candidato.correoelectronico,
            Candidato.selfregistration,
            Candidato.fechanacimiento,
            func.concat(Candidato.nombre, ' ', Candidato.apellidopaterno, ' ', Candidato.apellidomaterno).label('nombre_completo'),
            func.count(CandidatoTestPsicologico.idcandidato).label('cantidad_pruebas_asignadas')
        ).filter(Candidato.idcandidato == idcandidato
        ).outerjoin(CandidatoTestPsicologico, Candidato.idcandidato == CandidatoTestPsicologico.idcandidato
        ).group_by(Candidato.idcandidato,
            Candidato.nombre,
            Candidato.apellidopaterno,
            Candidato.apellidomaterno,
            Candidato.correoelectronico,
            Candidato.selfregistration,
            Candidato.fechanacimiento
        ).first()

class CandidatoSchema(ma.Schema):
    class Meta:
        fields = ('idcandidato', 'nombre', 'apellidopaterno', 'apellidomaterno', 'fechanacimiento', 'correoelectronico',
                  'selfregistration',
                  'nombre_completo', 'cantidad_pruebas_asignadas',
                  #'telefonos', 'direcciones', 
                  'testpsicologicos')

    #telefonos = ma.Nested(CandidatoTelefonoSchema, many=True)
    #direcciones = ma.Nested(CandidatoDireccionSchema, many=True)
    testpsicologicos = ma.Nested(CandidatoTestPsicologicoSchema, many=True)
