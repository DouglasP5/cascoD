from . import db
from datetime import datetime

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    senha = db.Column(db.String(150), nullable=False)
    tipo = db.Column(db.String(20), nullable=False, default='participante')
    admin = db.Column(db.Boolean, default=False)

class Equipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    lider_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    lider = db.relationship('Usuario', backref='equipes')

class Convite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    equipe_id = db.Column(db.Integer, db.ForeignKey('equipe.id'), nullable=False)
    equipe = db.relationship('Equipe', backref='convites')
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    usuario = db.relationship('Usuario', backref='convites')
    status = db.Column(db.String(20), nullable=False, default='pendente')
    data_envio = db.Column(db.DateTime, default=datetime.utcnow)

class Tartaruga(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sexo = db.Column(db.String(20), nullable=False)
    nome_cientifico = db.Column(db.String(150), nullable=False)
    anilha = db.Column(db.String(100), unique=True, nullable=False)
    especie = db.Column(db.String(150), nullable=False)
    tipo_registro = db.Column(db.String(50), nullable=False)
    registros = db.relationship('RegistroTartaruga', backref='tartaruga', lazy=True)

class RegistroTartaruga(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tartaruga_id = db.Column(db.Integer, db.ForeignKey('tartaruga.id'), nullable=False)
    estado = db.Column(db.String(100), nullable=False)
    data = db.Column(db.Date, nullable=False)
    horario = db.Column(db.Time, nullable=False)
    praia = db.Column(db.String(150), nullable=False)
    municipio = db.Column(db.String(150), nullable=False)
    comprimento_casco = db.Column(db.Float, nullable=False)
    largura_casco = db.Column(db.Float, nullable=False)
    quantidade_ovos = db.Column(db.Integer, nullable=False)
