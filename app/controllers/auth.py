"""Autenticación de administradores: iniciar y cerrar sesión."""
from flask import flash, redirect, render_template, request, session, url_for

from ..extensions import db
from ..models import Usuario
from .base import BaseController
from .seguridad import Seguridad


class AuthController(BaseController):
    nombre = "auth"
    prefijo = "/admin"

    def registrar_rutas(self):
        self.ruta("/login", self.login, metodos=("GET", "POST"))
        self.ruta("/logout", self.logout, metodos=("POST",))

    def login(self):
        if Seguridad.hay_sesion():
            return redirect(url_for("admin.dashboard"))
        if request.method == "POST":
            usuario_txt = request.form.get("usuario", "").strip()
            password = request.form.get("password", "")
            usuario = db.session.execute(
                db.select(Usuario).where(Usuario.usuario == usuario_txt)).scalar_one_or_none()
            if usuario and usuario.verificar_password(password):
                visitante = session.get("visitante")  # conserva el contador de visitas
                session.clear()
                if visitante:
                    session["visitante"] = visitante
                session[Seguridad.CLAVE] = usuario.id
                session["usuario_nombre"] = usuario.nombre
                return redirect(self._destino_seguro(request.args.get("next")))
            flash("Usuario o contraseña incorrectos.", "danger")
        return render_template("auth/login.html")

    def logout(self):
        session.pop(Seguridad.CLAVE, None)
        session.pop("usuario_nombre", None)
        flash("Cerraste sesión correctamente.", "success")
        return redirect(url_for("auth.login"))

    @staticmethod
    def _destino_seguro(destino):
        # Solo se permite regresar a rutas internas del panel (evita redirecciones a otros sitios)
        if destino and destino.startswith("/admin") and not destino.startswith("//"):
            return destino
        return url_for("admin.dashboard")
