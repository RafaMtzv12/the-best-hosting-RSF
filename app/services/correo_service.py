"""Envío de correos con SMTP (Gmail). Es un Singleton: hay un solo "cartero" en toda la app."""
import smtplib
from email.message import EmailMessage

from flask import current_app

from ..patrones.singleton import SingletonMeta


class CorreoService(metaclass=SingletonMeta):
    def esta_configurado(self):
        cfg = current_app.config
        return bool(cfg.get("MAIL_USERNAME") and cfg.get("MAIL_PASSWORD"))

    def enviar_sugerencia(self, sugerencia):
        """Manda la sugerencia al correo de la empresa. Regresa True si se envió."""
        if not self.esta_configurado():
            current_app.logger.info("Correo no configurado: la sugerencia solo se guardó en la base de datos.")
            return False
        cfg = current_app.config
        mensaje = EmailMessage()
        mensaje["Subject"] = f"Nueva sugerencia de {sugerencia.nombre} - The Best Hosting"
        mensaje["From"] = cfg["MAIL_USERNAME"]
        mensaje["To"] = cfg.get("MAIL_DESTINO") or cfg["MAIL_USERNAME"]
        mensaje["Reply-To"] = sugerencia.correo  # al dar "Responder" se le contesta al visitante
        mensaje.set_content(
            f"Nombre: {sugerencia.nombre}\n"
            f"Correo: {sugerencia.correo}\n"
            f"Fecha: {sugerencia.fecha:%d/%m/%Y %H:%M}\n\n"
            f"Mensaje:\n{sugerencia.mensaje}\n"
        )
        try:
            with smtplib.SMTP(cfg["MAIL_SERVER"], cfg["MAIL_PORT"], timeout=15) as smtp:
                smtp.starttls()
                smtp.login(cfg["MAIL_USERNAME"], cfg["MAIL_PASSWORD"])
                smtp.send_message(mensaje)
            return True
        except (smtplib.SMTPException, OSError) as error:
            current_app.logger.warning("No se pudo enviar el correo: %s", error)
            return False
