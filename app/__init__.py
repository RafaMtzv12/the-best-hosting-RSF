"""Construcción de la aplicación (patrón Application Factory dentro de la clase Aplicacion)."""
from flask import Flask, jsonify, render_template, request

from config import Config

from .controllers.admin import AdminController
from .controllers.api import ApiController
from .controllers.auth import AuthController
from .controllers.public import PublicController
from .controllers.seguridad import Seguridad
from .extensions import db
from .services.seed import Seeder
from .services.visitas_service import ContadorVisitas


class Aplicacion:
    CONTROLADORES = [PublicController, AuthController, AdminController, ApiController]

    def __init__(self, configuracion=Config):
        self.configuracion = configuracion

    def construir(self):
        app = Flask(__name__)
        app.config.from_object(self.configuracion)
        db.init_app(app)
        self._registrar_controladores(app)
        self._registrar_contador(app)
        self._registrar_contexto(app)
        self._registrar_errores(app)
        with app.app_context():
            db.create_all()  # crea las tablas que falten
            Seeder().ejecutar()  # datos de ejemplo la primera vez
        return app

    def _registrar_controladores(self, app):
        for controlador in self.CONTROLADORES:
            app.register_blueprint(controlador().bp)

    @staticmethod
    def _registrar_contador(app):
        @app.before_request
        def contar_visita():
            # Solo cuentan las páginas públicas (no imágenes, ni API, ni panel de administración)
            if request.method == "GET" and (request.endpoint or "").startswith("public."):
                ContadorVisitas().registrar()

    @staticmethod
    def _registrar_contexto(app):
        @app.context_processor
        def variables_globales():
            # Disponibles en todas las plantillas
            return {
                "contador": ContadorVisitas().resumen,  # se llama solo si la plantilla lo usa
                "es_admin": Seguridad.hay_sesion(),
            }

    @staticmethod
    def _registrar_errores(app):
        def responder(codigo, titulo, mensaje):
            if request.path.startswith("/api/"):
                return jsonify(ok=False, mensaje=mensaje), codigo
            return render_template("error.html", codigo=codigo, titulo=titulo, mensaje=mensaje), codigo

        @app.errorhandler(404)
        def no_encontrado(_error):
            return responder(404, "Página no encontrada", "La página que buscas no existe o fue movida.")

        @app.errorhandler(405)
        def metodo_no_permitido(_error):
            return responder(405, "Método no permitido", "Esta dirección no acepta ese tipo de petición.")

        @app.errorhandler(500)
        def error_interno(_error):
            db.session.rollback()
            return responder(500, "Error del servidor", "Ocurrió un error inesperado. Intenta de nuevo.")
