"""Modelos (la "M" de MVC): cada clase es una tabla de la base de datos.

Gracias al ORM no se escribe SQL a mano: se crean objetos y SQLAlchemy los guarda.
"""
from datetime import date, datetime

from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db


class ModeloBase(db.Model):
    """Clase padre abstracta: no crea tabla, solo comparte el id con sus clases hijas."""

    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)


class Usuario(ModeloBase):
    """Administrador del sitio (parte privada)."""

    __tablename__ = "usuarios"
    usuario = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def asignar_password(self, password):
        # Nunca se guarda la contraseña, solo su "hash" (huella irreversible)
        self.password_hash = generate_password_hash(password)

    def verificar_password(self, password):
        return check_password_hash(self.password_hash, password)


class TipoPlan(ModeloBase):
    """Categoría de plan: Hosting compartido, VPS, Servidor dedicado, Reseller."""

    __tablename__ = "tipos_plan"
    clave = db.Column(db.String(30), unique=True, nullable=False)  # para las URLs
    nombre = db.Column(db.String(60), unique=True, nullable=False)
    descripcion = db.Column(db.String(255))
    planes = db.relationship("Plan", back_populates="tipo")

    def to_dict(self):
        return {"id": self.id, "clave": self.clave, "nombre": self.nombre, "descripcion": self.descripcion}


class Plan(ModeloBase):
    """Plan de hosting que vende la empresa (los "servicios" del sitio)."""

    __tablename__ = "planes"
    nombre = db.Column(db.String(80), unique=True, nullable=False)
    tipo_id = db.Column(db.Integer, db.ForeignKey("tipos_plan.id"), nullable=False)
    precio_anterior = db.Column(db.Numeric(10, 2))
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    periodo = db.Column(db.String(20), nullable=False, default="año")
    lema = db.Column(db.String(120))
    descripcion = db.Column(db.Text)
    espacio = db.Column(db.String(40), nullable=False)
    transferencia = db.Column(db.String(40), nullable=False, default="Ilimitada")
    dominios = db.Column(db.String(40), nullable=False, default="1")
    cuentas_correo = db.Column(db.String(40), nullable=False, default="10")
    bases_datos = db.Column(db.String(40), nullable=False, default="1")
    ram = db.Column(db.String(40), nullable=False, default="Compartida")
    caracteristicas = db.Column(db.Text)  # una característica por renglón
    icono = db.Column(db.String(120), nullable=False, default="planes/starter.webp")
    destacado = db.Column(db.Boolean, nullable=False, default=False)
    activo = db.Column(db.Boolean, nullable=False, default=True)
    creado = db.Column(db.DateTime, nullable=False, default=datetime.now)

    tipo = db.relationship("TipoPlan", back_populates="planes")
    contratos = db.relationship("Contrato", back_populates="plan")

    def lista_caracteristicas(self):
        return [c.strip() for c in (self.caracteristicas or "").splitlines() if c.strip()]

    def ficha_tecnica(self):
        """Datos técnicos en pares (etiqueta, valor) para la página de detalle y el PDF."""
        return [
            ("Tipo de plan", self.tipo.nombre if self.tipo else ""),
            ("Espacio web", self.espacio),
            ("Transferencia", self.transferencia),
            ("Dominios incluidos", self.dominios),
            ("Cuentas de correo", self.cuentas_correo),
            ("Bases de datos MySQL", self.bases_datos),
            ("Memoria RAM", self.ram),
            ("Precio", f"${self.precio:,.2f} MXN / {self.periodo}"),
        ]

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "tipo_id": self.tipo_id,
            "tipo": self.tipo.nombre if self.tipo else None,
            "tipo_clave": self.tipo.clave if self.tipo else None,
            "precio_anterior": float(self.precio_anterior) if self.precio_anterior is not None else None,
            "precio": float(self.precio),
            "periodo": self.periodo,
            "lema": self.lema,
            "descripcion": self.descripcion,
            "espacio": self.espacio,
            "transferencia": self.transferencia,
            "dominios": self.dominios,
            "cuentas_correo": self.cuentas_correo,
            "bases_datos": self.bases_datos,
            "ram": self.ram,
            "caracteristicas": self.lista_caracteristicas(),
            "icono": self.icono,
            "destacado": self.destacado,
            "activo": self.activo,
        }


class Cliente(ModeloBase):
    """Empresas (hipotéticas) que son clientes; se muestran en la sección Clientes."""

    __tablename__ = "clientes"
    nombre = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    logo = db.Column(db.String(120), nullable=False)
    giro = db.Column(db.String(100))


class Contrato(ModeloBase):
    """Un plan contratado por un cliente, con su fecha de vencimiento (para el dashboard)."""

    __tablename__ = "contratos"
    cliente_nombre = db.Column(db.String(120), nullable=False)
    correo = db.Column(db.String(120), nullable=False)
    dominio = db.Column(db.String(120), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey("planes.id"), nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=False, default=date.today)
    fecha_vencimiento = db.Column(db.Date, nullable=False)

    plan = db.relationship("Plan", back_populates="contratos")

    @property
    def dias_restantes(self):
        return (self.fecha_vencimiento - date.today()).days

    def to_dict(self):
        return {
            "id": self.id,
            "cliente_nombre": self.cliente_nombre,
            "correo": self.correo,
            "dominio": self.dominio,
            "plan_id": self.plan_id,
            "plan": self.plan.nombre if self.plan else None,
            "fecha_inicio": self.fecha_inicio.isoformat(),
            "fecha_vencimiento": self.fecha_vencimiento.isoformat(),
            "dias_restantes": self.dias_restantes,
        }


class Sugerencia(ModeloBase):
    """Mensaje enviado desde el formulario de contacto."""

    __tablename__ = "sugerencias"
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(120), nullable=False)
    mensaje = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.now)
    correo_enviado = db.Column(db.Boolean, nullable=False, default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "correo": self.correo,
            "mensaje": self.mensaje,
            "fecha": self.fecha.strftime("%d/%m/%Y %H:%M"),
            "correo_enviado": self.correo_enviado,
        }


class Visita(ModeloBase):
    """Un visitante del sitio (un navegador). Sirve para el contador y los conectados."""

    __tablename__ = "visitas"
    sesion = db.Column(db.String(64), unique=True, nullable=False, index=True)
    ip = db.Column(db.String(45))
    primera = db.Column(db.DateTime, nullable=False, default=datetime.now)
    ultima = db.Column(db.DateTime, nullable=False, default=datetime.now, index=True)


class PreguntaFrecuente(ModeloBase):
    __tablename__ = "preguntas_frecuentes"
    pregunta = db.Column(db.String(200), nullable=False)
    respuesta = db.Column(db.Text, nullable=False)
    orden = db.Column(db.Integer, nullable=False, default=0)


class RespuestaChatbot(ModeloBase):
    """Base de conocimiento del chatbot: si el mensaje trae alguna palabra clave, responde esto."""

    __tablename__ = "respuestas_chatbot"
    tema = db.Column(db.String(60), nullable=False)
    palabras_clave = db.Column(db.String(255), nullable=False)  # separadas por coma
    respuesta = db.Column(db.Text, nullable=False)

    def lista_palabras(self):
        return [p.strip() for p in self.palabras_clave.split(",") if p.strip()]
