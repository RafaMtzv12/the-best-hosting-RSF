"""Protección de la parte privada (solo administradores)."""
from functools import wraps

from flask import jsonify, redirect, request, session, url_for


class Seguridad:
    CLAVE = "usuario_id"

    @classmethod
    def hay_sesion(cls):
        return cls.CLAVE in session

    @classmethod
    def login_requerido(cls, vista):
        """Para páginas: si no hay sesión, manda al login y luego regresa a donde iba."""
        @wraps(vista)
        def envoltura(*args, **kwargs):
            if not cls.hay_sesion():
                return redirect(url_for("auth.login", next=request.path))
            return vista(*args, **kwargs)
        return envoltura

    @classmethod
    def api_admin(cls, vista):
        """Para la API: si no hay sesión, responde 401 (no autorizado) en JSON."""
        @wraps(vista)
        def envoltura(*args, **kwargs):
            if not cls.hay_sesion():
                return jsonify(ok=False, mensaje="Inicia sesión como administrador."), 401
            return vista(*args, **kwargs)
        return envoltura
