"""Parte pública del sitio (no requiere iniciar sesión)."""
from flask import Response, abort, redirect, render_template, request, url_for

from ..extensions import db
from ..models import Cliente, PreguntaFrecuente
from ..services.contenido_service import ContenidoService
from ..services.errores import ErrorNegocio
from ..services.pdf_service import PdfService
from ..services.plan_service import PlanService
from .base import BaseController


class PublicController(BaseController):
    nombre = "public"

    def __init__(self):
        self.planes = PlanService()
        self.contenido = ContenidoService()
        super().__init__()

    def registrar_rutas(self):
        self.ruta("/", self.inicio)
        self.ruta("/compania", self.compania)
        self.ruta("/servicios", self.servicios)
        self.ruta("/soluciones", self.soluciones)
        self.ruta("/clientes", self.clientes)
        self.ruta("/contacto", self.contacto)
        self.ruta("/preguntas-frecuentes", self.preguntas_frecuentes)
        self.ruta("/planes/<int:plan_id>", self.plan)
        self.ruta("/planes/<int:plan_id>/ficha.pdf", self.ficha_pdf)
        self.ruta("/seccion/<clave>", self.seccion)

    def inicio(self):
        return render_template("public/inicio.html", planes=self.planes.destacados())

    def compania(self):
        return render_template("public/compania.html")

    def servicios(self):
        return render_template("public/servicios.html", tipos=self.planes.tipos(),
                               q=request.args.get("q", ""), tipo=request.args.get("tipo", ""))

    def soluciones(self):
        return render_template("public/soluciones.html", tipos=self.planes.tipos())

    def clientes(self):
        clientes = db.session.execute(db.select(Cliente).order_by(Cliente.nombre)).scalars().all()
        return render_template("public/clientes.html", clientes=clientes)

    def contacto(self):
        return render_template("public/contacto.html")

    def preguntas_frecuentes(self):
        preguntas = db.session.execute(
            db.select(PreguntaFrecuente).order_by(PreguntaFrecuente.orden)).scalars().all()
        return render_template("public/preguntas.html", preguntas=preguntas)

    def plan(self, plan_id):
        plan = self._plan_o_404(plan_id)
        return render_template("public/plan.html", plan=plan)

    def ficha_pdf(self, plan_id):
        plan = self._plan_o_404(plan_id)
        url = url_for("public.plan", plan_id=plan.id, _external=True)
        pdf = PdfService().ficha_plan(plan, url)
        nombre = f"ficha-plan-{plan.id}.pdf"
        # inline: se abre en el navegador; desde ahí se puede descargar o imprimir
        return Response(pdf, mimetype="application/pdf",
                        headers={"Content-Disposition": f"inline; filename={nombre}"})

    def seccion(self, clave):
        # Algunas opciones del menú lateral son filtros del buscador de planes
        filtros = {"web-hosting": "compartido", "servidor-dedicado": "dedicado", "resellers": "reseller"}
        if clave in filtros:
            return redirect(url_for("public.servicios", tipo=filtros[clave]))
        try:
            seccion = self.contenido.obtener(clave)
        except ErrorNegocio:
            abort(404)
        return render_template("public/seccion.html", seccion=seccion)

    def _plan_o_404(self, plan_id):
        try:
            return self.planes.obtener(plan_id, solo_activos=True)
        except ErrorNegocio:
            abort(404)
