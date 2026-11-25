"""Sugerencias del formulario de contacto: guardar, enviar por correo, listar con paginación."""
from flask import current_app
from sqlalchemy import or_

from ..extensions import db
from ..models import Sugerencia
from .correo_service import CorreoService
from .errores import ErrorNegocio
from .validador import SugerenciaValidator


class SugerenciaService:
    def registrar(self, datos):
        limpio = SugerenciaValidator(datos).validar()
        sugerencia = Sugerencia(**limpio)
        db.session.add(sugerencia)
        db.session.commit()  # primero se guarda: aunque falle el correo, el mensaje no se pierde
        sugerencia.correo_enviado = CorreoService().enviar_sugerencia(sugerencia)
        db.session.commit()
        return sugerencia

    def _consulta(self, texto=""):
        consulta = db.select(Sugerencia)
        texto = (texto or "").strip()
        if texto:
            patron = f"%{texto}%"
            consulta = consulta.where(or_(
                Sugerencia.nombre.ilike(patron), Sugerencia.correo.ilike(patron),
                Sugerencia.mensaje.ilike(patron),
            ))
        return consulta.order_by(Sugerencia.fecha.desc(), Sugerencia.id.desc())

    def paginar(self, pagina=1, texto=""):
        """Devuelve una página de resultados (objeto Pagination de Flask-SQLAlchemy)."""
        return db.paginate(
            self._consulta(texto), page=pagina,
            per_page=current_app.config["SUGERENCIAS_POR_PAGINA"], error_out=False,
        )

    def todas(self, texto=""):
        return db.session.execute(self._consulta(texto)).scalars().all()

    def eliminar(self, sugerencia_id):
        sugerencia = db.session.get(Sugerencia, sugerencia_id)
        if sugerencia is None:
            raise ErrorNegocio("La sugerencia no existe.", 404)
        db.session.delete(sugerencia)
        db.session.commit()
