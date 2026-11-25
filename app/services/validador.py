"""Validación de datos en el servidor (además de la validación en el navegador).

ValidadorBase tiene la lógica común; cada formulario tiene su clase hija.
"""
import re
from datetime import date
from decimal import Decimal, InvalidOperation

from .errores import ErrorNegocio

PATRON_CORREO = re.compile(r"^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$")
PATRON_DOMINIO = re.compile(r"^(?!-)[a-z0-9-]+(\.[a-z0-9-]+)+$")


class ValidadorBase:
    def __init__(self, datos):
        self.datos = datos or {}
        self.errores = {}
        self.limpio = {}

    def texto(self, campo, etiqueta, maximo, requerido=True):
        valor = str(self.datos.get(campo) or "").strip()
        if requerido and not valor:
            self.errores[campo] = f"{etiqueta} es obligatorio."
        elif len(valor) > maximo:
            self.errores[campo] = f"{etiqueta} admite máximo {maximo} caracteres."
        self.limpio[campo] = valor
        return valor

    def correo(self, campo="correo"):
        valor = self.texto(campo, "El correo", 120)
        if valor and not PATRON_CORREO.match(valor):
            self.errores[campo] = "Escribe un correo válido (ejemplo: nombre@dominio.com)."
        return valor

    def dinero(self, campo, etiqueta, requerido=True):
        bruto = str(self.datos.get(campo) or "").replace(",", "").replace("$", "").strip()
        if not bruto:
            if requerido:
                self.errores[campo] = f"{etiqueta} es obligatorio."
            self.limpio[campo] = None
            return None
        try:
            valor = Decimal(bruto)
            if valor < 0 or valor > Decimal("9999999"):
                raise InvalidOperation
        except InvalidOperation:
            self.errores[campo] = f"{etiqueta} debe ser un número positivo."
            valor = None
        self.limpio[campo] = valor
        return valor

    def fecha(self, campo, etiqueta):
        bruto = str(self.datos.get(campo) or "").strip()
        try:
            valor = date.fromisoformat(bruto)
        except ValueError:
            self.errores[campo] = f"{etiqueta} no es una fecha válida."
            valor = None
        self.limpio[campo] = valor
        return valor

    def entero(self, campo, etiqueta):
        try:
            valor = int(self.datos.get(campo))
        except (TypeError, ValueError):
            self.errores[campo] = f"Selecciona {etiqueta}."
            valor = None
        self.limpio[campo] = valor
        return valor

    def booleano(self, campo):
        valor = self.datos.get(campo)
        self.limpio[campo] = valor in (True, "true", "1", 1, "on")
        return self.limpio[campo]

    def reglas(self):
        raise NotImplementedError

    def validar(self):
        self.reglas()
        if self.errores:
            raise ErrorNegocio("Revisa los campos marcados.", 422, self.errores)
        return self.limpio


class PlanValidator(ValidadorBase):
    def reglas(self):
        self.texto("nombre", "El nombre", 80)
        self.entero("tipo_id", "un tipo de plan")
        precio = self.dinero("precio", "El precio")
        anterior = self.dinero("precio_anterior", "El precio anterior", requerido=False)
        if precio is not None and anterior is not None and anterior <= precio:
            self.errores["precio_anterior"] = "El precio anterior debe ser mayor al precio actual."
        periodo = self.texto("periodo", "El periodo", 20)
        if periodo and periodo not in ("mes", "año"):
            self.errores["periodo"] = "El periodo debe ser mes o año."
        self.texto("lema", "El lema", 120, requerido=False)
        self.texto("descripcion", "La descripción", 2000, requerido=False)
        for campo, etiqueta in [("espacio", "El espacio"), ("transferencia", "La transferencia"),
                                ("dominios", "Los dominios"), ("cuentas_correo", "Las cuentas de correo"),
                                ("bases_datos", "Las bases de datos"), ("ram", "La memoria RAM")]:
            self.texto(campo, etiqueta, 40)
        self.texto("caracteristicas", "Las características", 2000, requerido=False)
        self.texto("icono", "El icono", 120, requerido=False)
        self.booleano("destacado")
        self.booleano("activo")


class ContratoValidator(ValidadorBase):
    def reglas(self):
        self.texto("cliente_nombre", "El nombre del cliente", 120)
        self.correo()
        dominio = self.texto("dominio", "El dominio", 120).lower()
        self.limpio["dominio"] = dominio
        if dominio and not PATRON_DOMINIO.match(dominio):
            self.errores["dominio"] = "Escribe un dominio válido (ejemplo: miempresa.com)."
        self.entero("plan_id", "un plan")
        inicio = self.fecha("fecha_inicio", "La fecha de inicio")
        fin = self.fecha("fecha_vencimiento", "La fecha de vencimiento")
        if inicio and fin and fin <= inicio:
            self.errores["fecha_vencimiento"] = "El vencimiento debe ser posterior al inicio."


class SugerenciaValidator(ValidadorBase):
    def reglas(self):
        self.texto("nombre", "El nombre", 100)
        self.correo()
        mensaje = self.texto("mensaje", "El mensaje", 2000)
        if mensaje and len(mensaje) < 10:
            self.errores["mensaje"] = "El mensaje debe tener al menos 10 caracteres."
