"""Contador de visitas y usuarios conectados (patrón Singleton).

- Visitas: cuántos visitantes distintos (navegadores) han entrado al sitio.
- Conectados: cuántos tuvieron actividad en los últimos minutos (ver MINUTOS_CONECTADO).
El navegador manda una señal cada minuto (/api/v1/presencia) mientras la página está abierta.
"""
import uuid
from datetime import datetime, timedelta

from flask import current_app, request, session
from sqlalchemy import func

from ..extensions import db
from ..models import Visita
from ..patrones.singleton import SingletonMeta


class ContadorVisitas(metaclass=SingletonMeta):
    CLAVE_SESION = "visitante"
    SEGUNDOS_ENTRE_ESCRITURAS = 30  # para no escribir en la BD en cada clic

    def registrar(self):
        """Cuenta al visitante la primera vez y actualiza su última actividad."""
        sesion_id = session.get(self.CLAVE_SESION)
        ahora = datetime.now()
        visita = None
        if sesion_id:
            visita = db.session.execute(
                db.select(Visita).where(Visita.sesion == sesion_id)
            ).scalar_one_or_none()
        if visita is None:
            sesion_id = uuid.uuid4().hex
            session[self.CLAVE_SESION] = sesion_id
            session.permanent = True
            db.session.add(Visita(sesion=sesion_id, ip=request.remote_addr, primera=ahora, ultima=ahora))
            db.session.commit()
        elif (ahora - visita.ultima).total_seconds() > self.SEGUNDOS_ENTRE_ESCRITURAS:
            visita.ultima = ahora
            db.session.commit()

    def total_visitas(self):
        return db.session.execute(db.select(func.count(Visita.id))).scalar_one()

    def conectados(self):
        limite = datetime.now() - timedelta(minutes=current_app.config["MINUTOS_CONECTADO"])
        consulta = db.select(func.count(Visita.id)).where(Visita.ultima >= limite)
        return db.session.execute(consulta).scalar_one()

    def resumen(self):
        total = self.total_visitas()
        return {
            "visitas": total,
            "visitas_digitos": f"{total:05d}",  # 00042 -> como el contador del diseño
            "conectados": max(self.conectados(), 1),  # quien está viendo la página siempre cuenta
        }
