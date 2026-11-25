"""Controlador base (la "C" de MVC). Los demás controladores heredan de esta clase."""
from flask import Blueprint


class BaseController:
    nombre = None  # nombre del blueprint, se usa en url_for("nombre.metodo")
    prefijo = None  # prefijo de URL, por ejemplo "/admin"

    def __init__(self):
        self.bp = Blueprint(self.nombre, __name__, url_prefix=self.prefijo)
        self.registrar_rutas()

    def ruta(self, regla, vista, metodos=("GET",), endpoint=None):
        """Conecta una URL con un método de la clase."""
        self.bp.add_url_rule(regla, endpoint or vista.__name__, vista, methods=list(metodos))

    def registrar_rutas(self):
        raise NotImplementedError("Cada controlador define sus rutas")
