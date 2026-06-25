from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model, UserMixin):

    __tablename__ = "user"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(80),
        unique=True,
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.String(20),
        default="user"
    )

    activo = db.Column(
        db.Boolean,
        default=True
    )

    cambiar_password = db.Column(
        db.Boolean,
        default=False
    )

    articulos = db.relationship(
        "Articulo",
        backref="owner",
        lazy=True
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(
            self.password_hash,
            password
        )

class Articulo(db.Model):

    __tablename__ = "articulos"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    numero = db.Column(
        db.Integer,
        nullable=False
    )

    lista_orden = db.Column(db.String(50))

    ubicacion = db.Column(db.String(100))

    marca = db.Column(db.String(100))

    referencia = db.Column(db.String(100))

    set_modelo = db.Column(db.String(100))

    descripcion = db.Column(db.String(300))

    matricula = db.Column(db.String(100))

    matricula_ii = db.Column(db.String(100))

    epoca = db.Column(db.String(50))

    caja = db.Column(db.String(100))

    unidades = db.Column(db.Integer)

    tipo = db.Column(db.String(100))

    ejes = db.Column(db.String(50))

    rodaje = db.Column(db.String(50))

    longitud = db.Column(db.String(50))

    administracion = db.Column(db.String(100))

    librea = db.Column(db.String(100))

    envejecido = db.Column(db.String(50))

    clasificacion = db.Column(db.String(100))

    mercancia = db.Column(db.String(100))

    estado = db.Column(db.String(100))

    necesidades = db.Column(db.String(300))

    rodaje_detalle = db.Column(db.String(100))

    imagen = db.Column(db.String(300)

)

class MaestroArticulo(db.Model):

    __tablename__ = "maestro_articulos"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    referencia = db.Column(
        db.String(100),
        unique=True
    )

    marca = db.Column(db.String(100))
    descripcion = db.Column(db.String(300))
    matricula = db.Column(db.String(100))
    matricula_ii = db.Column(db.String(100))
    epoca = db.Column(db.String(50))
    caja = db.Column(db.String(100))
    unidades = db.Column(db.Integer)
    tipo = db.Column(db.String(100))
    ejes = db.Column(db.String(50))
    rodaje = db.Column(db.String(50))
    longitud = db.Column(db.String(50))
    administracion = db.Column(db.String(100))
    librea = db.Column(db.String(100))
    envejecido = db.Column(db.String(50))
    clasificacion = db.Column(db.String(100))
    mercancia = db.Column(db.String(100))
    estado = db.Column(db.String(100))
    necesidades = db.Column(db.String(300))
    rodaje_detalle = db.Column(db.String(100))
    imagen = db.Column(db.String(300))

    validada = db.Column(
        db.Boolean,
        default=False
    )

    validada_por = db.Column(
        db.String(100)
    )
