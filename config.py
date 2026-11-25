"""Configuración del proyecto.

Los valores secretos (clave de sesión y datos del correo) se leen del archivo .env
para no escribirlos dentro del código. Ver .env.example.
"""
import os
from datetime import timedelta

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # si python-dotenv no está instalado, se usan los valores por defecto
    pass

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Seguridad y base de datos
    SECRET_KEY = os.environ.get("SECRET_KEY", "clave-de-desarrollo-cambiar-en-produccion")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///" + os.path.join(BASE_DIR, "the_best_hosting.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)

    # Correo del formulario de contacto (Gmail con "contraseña de aplicación")
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", "587"))
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
    MAIL_DESTINO = os.environ.get("MAIL_DESTINO", "")  # quién recibe las sugerencias

    # Ajustes del sitio
    SUGERENCIAS_POR_PAGINA = 10
    MINUTOS_CONECTADO = 5  # un visitante cuenta como "conectado" si estuvo activo en estos minutos
    DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"
