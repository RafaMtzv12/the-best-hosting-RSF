"""Excepción propia para errores de negocio (datos inválidos, registro inexistente, etc.)."""


class ErrorNegocio(Exception):
    def __init__(self, mensaje, codigo=400, errores=None):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.codigo = codigo  # código HTTP que devolverá la API
        self.errores = errores or {}  # errores por campo, para marcar el formulario en rojo

    def to_dict(self):
        return {"ok": False, "mensaje": self.mensaje, "errores": self.errores}
