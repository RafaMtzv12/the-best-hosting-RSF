"""Panel de administración (parte privada). Todas las páginas piden sesión."""
from datetime import datetime

from flask import Response, render_template, request

from ..services.dashboard_service import DashboardService
from ..services.excel_service import ExcelService
from ..services.pdf_service import PdfService
from ..services.plan_service import PlanService
from ..services.sugerencia_service import SugerenciaService
from .base import BaseController
from .seguridad import Seguridad


class AdminController(BaseController):
    nombre = "admin"
    prefijo = "/admin"

    def __init__(self):
        self.sugerencias_srv = SugerenciaService()
        super().__init__()

    def ruta(self, regla, vista, metodos=("GET",), endpoint=None):
        # Todas las rutas de este controlador se protegen con login
        super().ruta(regla, Seguridad.login_requerido(vista), metodos, endpoint or vista.__name__)

    def registrar_rutas(self):
        self.ruta("/", self.dashboard)
        self.ruta("/planes", self.planes)
        self.ruta("/contratos", self.contratos)
        self.ruta("/sugerencias", self.sugerencias)
        self.ruta("/sugerencias/exportar/excel", self.exportar_excel)
        self.ruta("/sugerencias/exportar/pdf", self.exportar_pdf)

    def dashboard(self):
        return render_template("admin/dashboard.html", tarjetas=DashboardService().tarjetas())

    def planes(self):
        return render_template("admin/planes.html", tipos=PlanService().tipos())

    def contratos(self):
        planes = PlanService().buscar(solo_activos=False, orden="nombre")
        return render_template("admin/contratos.html", planes=planes)

    def sugerencias(self):
        pagina = request.args.get("pagina", 1, type=int)
        q = request.args.get("q", "").strip()
        paginacion = self.sugerencias_srv.paginar(pagina, q)
        return render_template("admin/sugerencias.html", paginacion=paginacion, q=q)

    def exportar_excel(self):
        q = request.args.get("q", "").strip()
        datos = ExcelService().exportar_sugerencias(self.sugerencias_srv.todas(q))
        return self._archivo(datos, "xlsx",
                             "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    def exportar_pdf(self):
        q = request.args.get("q", "").strip()
        datos = PdfService().listado_sugerencias(self.sugerencias_srv.todas(q), q)
        return self._archivo(datos, "pdf", "application/pdf")

    @staticmethod
    def _archivo(datos, extension, tipo):
        nombre = f"sugerencias_{datetime.now():%Y%m%d_%H%M}.{extension}"
        return Response(datos, mimetype=tipo, headers={"Content-Disposition": f"attachment; filename={nombre}"})
