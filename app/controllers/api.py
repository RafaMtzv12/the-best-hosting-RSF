"""API REST propia en /api/v1. Responde siempre en JSON.

REST significa que cada URL es un "recurso" y el método HTTP dice qué hacer con él:
  GET = consultar, POST = crear, PUT = modificar, DELETE = eliminar.

| Método y URL                         | Qué hace                                  | Acceso   |
|--------------------------------------|-------------------------------------------|----------|
| GET    /api/v1/planes?q=&tipo=&...   | Buscar planes                             | Público  |
| GET    /api/v1/planes/<id>           | Consultar un plan                         | Público  |
| POST   /api/v1/planes                | Crear plan                                | Admin    |
| PUT    /api/v1/planes/<id>           | Modificar plan                            | Admin    |
| DELETE /api/v1/planes/<id>           | Eliminar plan                             | Admin    |
| GET    /api/v1/tipos                 | Tipos de plan                             | Público  |
| GET/POST /api/v1/contratos           | Listar / crear contratos                  | Admin    |
| PUT/DELETE /api/v1/contratos/<id>    | Modificar / eliminar contrato             | Admin    |
| POST   /api/v1/sugerencias           | Enviar formulario de contacto             | Público  |
| DELETE /api/v1/sugerencias/<id>      | Eliminar sugerencia                       | Admin    |
| POST   /api/v1/chatbot               | Preguntar al chatbot                      | Público  |
| GET/POST /api/v1/presencia           | Contador de visitas y conectados          | Público  |
| GET    /api/v1/dashboard/tipos       | Datos del dashboard 1                     | Admin    |
| GET    /api/v1/dashboard/vencimientos| Datos del dashboard 2                     | Admin    |
"""
from flask import jsonify, request
from flask.views import MethodView

from ..services.chatbot_service import ChatbotService
from ..services.contrato_service import ContratoService
from ..services.dashboard_service import DashboardService
from ..services.errores import ErrorNegocio
from ..services.plan_service import PlanService
from ..services.sugerencia_service import SugerenciaService
from ..services.visitas_service import ContadorVisitas
from .base import BaseController
from .seguridad import Seguridad


class Recurso(MethodView):
    """Clase base de los recursos de la API."""

    @staticmethod
    def datos():
        return request.get_json(silent=True) or request.form.to_dict()

    @staticmethod
    def ok(datos=None, codigo=200, **extra):
        return jsonify(ok=True, datos=datos, **extra), codigo


class PlanListaAPI(Recurso):
    def get(self):
        planes = PlanService().buscar(
            texto=request.args.get("q", ""), tipo=request.args.get("tipo"),
            precio_max=request.args.get("precio_max"), orden=request.args.get("orden", "precio"),
            solo_activos=not (Seguridad.hay_sesion() and request.args.get("todos") == "1"),
        )
        return self.ok([p.to_dict() for p in planes], total=len(planes))

    @Seguridad.api_admin
    def post(self):
        plan = PlanService().crear(self.datos())
        return self.ok(plan.to_dict(), 201, mensaje="Plan creado.")


class PlanAPI(Recurso):
    def get(self, plan_id):
        plan = PlanService().obtener(plan_id, solo_activos=not Seguridad.hay_sesion())
        return self.ok(plan.to_dict())

    @Seguridad.api_admin
    def put(self, plan_id):
        plan = PlanService().actualizar(plan_id, self.datos())
        return self.ok(plan.to_dict(), mensaje="Plan actualizado.")

    @Seguridad.api_admin
    def delete(self, plan_id):
        PlanService().eliminar(plan_id)
        return self.ok(mensaje="Plan eliminado.")


class TipoListaAPI(Recurso):
    def get(self):
        return self.ok([t.to_dict() for t in PlanService().tipos()])


class ContratoListaAPI(Recurso):
    decorators = [Seguridad.api_admin]  # todos los métodos son solo para administradores

    def get(self):
        contratos = ContratoService().listar(request.args.get("q", ""))
        return self.ok([c.to_dict() for c in contratos], total=len(contratos))

    def post(self):
        contrato = ContratoService().crear(self.datos())
        return self.ok(contrato.to_dict(), 201, mensaje="Contrato registrado.")


class ContratoAPI(Recurso):
    decorators = [Seguridad.api_admin]

    def put(self, contrato_id):
        contrato = ContratoService().actualizar(contrato_id, self.datos())
        return self.ok(contrato.to_dict(), mensaje="Contrato actualizado.")

    def delete(self, contrato_id):
        ContratoService().eliminar(contrato_id)
        return self.ok(mensaje="Contrato eliminado.")


class SugerenciaListaAPI(Recurso):
    def post(self):
        sugerencia = SugerenciaService().registrar(self.datos())
        mensaje = "¡Gracias! Recibimos tu mensaje."
        if sugerencia.correo_enviado:
            mensaje += " También se envió por correo a nuestro equipo."
        return self.ok({"id": sugerencia.id}, 201, mensaje=mensaje)


class SugerenciaAPI(Recurso):
    decorators = [Seguridad.api_admin]

    def delete(self, sugerencia_id):
        SugerenciaService().eliminar(sugerencia_id)
        return self.ok(mensaje="Sugerencia eliminada.")


class ChatbotAPI(Recurso):
    def post(self):
        mensaje = str(self.datos().get("mensaje", ""))[:500]
        return self.ok(ChatbotService().responder(mensaje))


class PresenciaAPI(Recurso):
    def get(self):
        return self.ok(ContadorVisitas().resumen())

    def post(self):
        """El navegador avisa "sigo aquí" cada minuto."""
        contador = ContadorVisitas()
        contador.registrar()
        return self.ok(contador.resumen())


class DashboardTiposAPI(Recurso):
    decorators = [Seguridad.api_admin]

    def get(self):
        return self.ok(DashboardService().tipos_planes())


class DashboardVencimientosAPI(Recurso):
    decorators = [Seguridad.api_admin]

    def get(self):
        return self.ok(DashboardService().vencimientos(request.args.get("modo", "proximos")))


class ApiController(BaseController):
    nombre = "api"
    prefijo = "/api/v1"

    RECURSOS = [
        ("/planes", PlanListaAPI, "planes"),
        ("/planes/<int:plan_id>", PlanAPI, "plan"),
        ("/tipos", TipoListaAPI, "tipos"),
        ("/contratos", ContratoListaAPI, "contratos"),
        ("/contratos/<int:contrato_id>", ContratoAPI, "contrato"),
        ("/sugerencias", SugerenciaListaAPI, "sugerencias"),
        ("/sugerencias/<int:sugerencia_id>", SugerenciaAPI, "sugerencia"),
        ("/chatbot", ChatbotAPI, "chatbot"),
        ("/presencia", PresenciaAPI, "presencia"),
        ("/dashboard/tipos", DashboardTiposAPI, "dashboard_tipos"),
        ("/dashboard/vencimientos", DashboardVencimientosAPI, "dashboard_vencimientos"),
    ]

    def registrar_rutas(self):
        for regla, clase, nombre in self.RECURSOS:
            self.bp.add_url_rule(regla, view_func=clase.as_view(nombre))
        self.bp.register_error_handler(ErrorNegocio, self.error_negocio)

    @staticmethod
    def error_negocio(error):
        return jsonify(error.to_dict()), error.codigo
