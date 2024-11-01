from ext.database import db
from sqlalchemy.inspection import inspect
from flask_login import UserMixin


class Placas(db.Model):
    __tablename__ = 'placas'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    placa = db.Column(db.String(10), nullable=False)
    veiculo = db.Column(db.String(30))
    km_necessario = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

    def __repr__(self):
        return f'<Placa id={self.id} placa={self.placa}>'


class Motoristas(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    motorista = db.Column(db.String(50), nullable=False)
    cidade = db.Column(db.String(30))

    def __repr__(self):
        return f'<Motorista id={self.id} motorista={self.motorista}>'


class Cidades(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    cidade = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return f'<Cidade id={self.id} cidade={self.cidade}>'


class User(db.Model, UserMixin):
    __tablename__ = "posto_users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    username = db.Column(db.String(140))
    password = db.Column(db.String(512))
    is_admin = db.Column(db.Boolean, default=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password


tables_dict = {table.__tablename__: table for table in db.Model.__subclasses__()}


def table_object(table_name):
    return tables_dict.get(table_name)
