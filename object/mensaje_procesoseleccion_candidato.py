from configs.flask_config import db, ma

class MensajeProcesoseleccionCandidato(db.Model):
    __table_args__ = {"schema": "evaluationroom"}
    __tablename__ = 'mensaje_procesoseleccion_candidato'
    
    id_mensaje = db.Column(db.Integer, primary_key=True)
    tipo_mensaje = db.Column(db.String())
    mensaje = db.Column(db.String())

    def __init__(self, id_mensaje, tipo_mensaje, mensaje):
        self.id_mensaje = id_mensaje
        self.tipo_mensaje = tipo_mensaje
        self.mensaje = mensaje
    
class MensajeProcesoseleccionCandidatoSchema(ma.Schema):
    class Meta:
        fields = ('id_mensaje', 'tipo_mensaje', 'mensaje')