"""Chatbot de ayuda en línea 24/7 basado en palabras clave.

1. Limpia el mensaje (minúsculas y sin acentos).
2. Si menciona un plan por su nombre, responde con su precio real de la base de datos.
3. Si no, busca en la tabla respuestas_chatbot la respuesta con más palabras clave encontradas.
4. Si nada coincide, ofrece temas sugeridos y el contacto humano.
"""
import re
import unicodedata

from ..extensions import db
from ..models import Plan, RespuestaChatbot

SUGERENCIAS = ["Planes y precios", "Dominios", "Soporte técnico", "Formas de pago", "Correo electrónico"]


class ChatbotService:
    @staticmethod
    def normalizar(texto):
        texto = unicodedata.normalize("NFD", (texto or "").lower())
        texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")  # quita acentos
        return re.sub(r"[^a-z0-9ñ$ ]+", " ", texto).strip()

    def responder(self, mensaje):
        limpio = self.normalizar(mensaje)
        if not limpio:
            return self._respuesta("Escríbeme tu duda y con gusto te ayudo. 🙂", SUGERENCIAS)

        respuesta_plan = self._buscar_plan(limpio)
        if respuesta_plan:
            return respuesta_plan

        mejor, puntos = None, 0
        palabras = f" {limpio} "
        for registro in db.session.execute(db.select(RespuestaChatbot)).scalars():
            coincidencias = sum(1 for p in registro.lista_palabras() if f" {self.normalizar(p)}" in palabras)
            if coincidencias > puntos:
                mejor, puntos = registro, coincidencias
        if mejor:
            return self._respuesta(mejor.respuesta, [], mejor.tema)
        return self._respuesta(
            "No estoy seguro de haber entendido. 🤔 Puedo ayudarte con estos temas, "
            "o si prefieres, llama a ventas al (844) 414 5676.", SUGERENCIAS)

    def _buscar_plan(self, limpio):
        planes = db.session.execute(db.select(Plan).where(Plan.activo.is_(True))).scalars().all()
        for plan in planes:
            if self.normalizar(plan.nombre) in limpio:
                texto = (f"El plan <b>{plan.nombre}</b> cuesta <b>${plan.precio:,.0f} MXN al {plan.periodo}</b>"
                         f" e incluye {plan.espacio} de espacio, {plan.cuentas_correo} cuentas de correo y "
                         f"transferencia {plan.transferencia.lower()}. "
                         f"<a href='/planes/{plan.id}'>Ver detalles</a>")
                return self._respuesta(texto, [], "planes")
        return None

    @staticmethod
    def _respuesta(texto, sugerencias, tema="general"):
        return {"respuesta": texto, "sugerencias": sugerencias, "tema": tema}
