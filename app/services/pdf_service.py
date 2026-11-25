"""Generación de PDF con ReportLab (patrón Singleton).

- ficha_plan: ficha técnica de un plan de hosting, con QR que abre el plan en el sitio.
- listado_sugerencias: reporte de las sugerencias recibidas.
Los PDF se arman en memoria (BytesIO) y se mandan al navegador sin guardar archivos.
"""
import os
from datetime import datetime
from io import BytesIO
from xml.sax.saxutils import escape

from flask import current_app
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from ..patrones.singleton import SingletonMeta

ROJO = colors.HexColor("#8b0000")
ROSA = colors.HexColor("#fde8e8")


class PdfService(metaclass=SingletonMeta):
    def __init__(self):
        estilos = getSampleStyleSheet()
        self.titulo = ParagraphStyle("titulo", parent=estilos["Title"], textColor=ROJO, fontSize=20)
        self.subtitulo = ParagraphStyle("sub", parent=estilos["Heading2"], textColor=ROJO)
        self.normal = estilos["BodyText"]
        self.pequeno = ParagraphStyle("peq", parent=estilos["BodyText"], fontSize=8, leading=10)

    # --- piezas comunes ---
    def _logo(self):
        ruta = os.path.join(current_app.static_folder, "img", "sitio", "logo.webp")
        try:
            return Image(ruta, width=4.5 * cm, height=2.37 * cm)
        except Exception:  # si la imagen no se puede leer, el PDF sigue sin logo
            return Paragraph("<b>THE BEST HOSTING</b>", self.subtitulo)

    def _pie(self, lienzo, documento):
        lienzo.saveState()
        lienzo.setFont("Helvetica", 8)
        lienzo.setFillColor(colors.grey)
        lienzo.drawString(documento.leftMargin, 1.2 * cm,
                          f"The Best Hosting · (844) 414 5676 · help@thebesthost.com · "
                          f"Generado el {datetime.now():%d/%m/%Y %H:%M}")
        lienzo.drawRightString(documento.pagesize[0] - documento.rightMargin, 1.2 * cm,
                               f"Página {documento.page}")
        lienzo.restoreState()

    def _qr(self, texto, tam=3.2 * cm):
        widget = QrCodeWidget(texto)
        x1, y1, x2, y2 = widget.getBounds()
        dibujo = Drawing(tam, tam, transform=[tam / (x2 - x1), 0, 0, tam / (y2 - y1), 0, 0])
        dibujo.add(widget)
        return dibujo

    def _construir(self, elementos, horizontal=False):
        buffer = BytesIO()
        tam = landscape(letter) if horizontal else letter
        doc = SimpleDocTemplate(buffer, pagesize=tam, leftMargin=1.8 * cm, rightMargin=1.8 * cm,
                                topMargin=1.5 * cm, bottomMargin=2 * cm, title="The Best Hosting")
        doc.build(elementos, onFirstPage=self._pie, onLaterPages=self._pie)
        return buffer.getvalue()

    # --- documentos ---
    def ficha_plan(self, plan, url_plan):
        encabezado = Table([[self._logo(), self._qr(url_plan)]], colWidths=[13 * cm, 4 * cm])
        encabezado.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                        ("ALIGN", (1, 0), (1, 0), "RIGHT")]))
        elementos = [
            encabezado,
            Paragraph(f"Ficha técnica: Plan {escape(plan.nombre)}", self.titulo),
        ]
        if plan.lema:
            elementos.append(Paragraph(f"<i>{escape(plan.lema)}</i>", self.normal))
        elementos.append(Spacer(1, 0.4 * cm))

        filas = [["Concepto", "Detalle"]] + [[k, v] for k, v in plan.ficha_tecnica()]
        if plan.precio_anterior:
            filas.append(["Precio anterior", f"${plan.precio_anterior:,.2f} MXN"])
        tabla = Table(filas, colWidths=[6 * cm, 11 * cm])
        tabla.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), ROJO), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ROSA]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d9a5a5")),
            ("PADDING", (0, 0), (-1, -1), 7),
        ]))
        elementos += [tabla, Spacer(1, 0.6 * cm)]

        if plan.descripcion:
            elementos += [Paragraph("Descripción", self.subtitulo), Paragraph(escape(plan.descripcion), self.normal)]
        caracteristicas = plan.lista_caracteristicas()
        if caracteristicas:
            elementos.append(Paragraph("Incluye", self.subtitulo))
            for c in caracteristicas:
                elementos.append(Paragraph(f"• {escape(c)}", self.normal))
        elementos += [Spacer(1, 0.6 * cm),
                      Paragraph("Escanea el código QR para ver o contratar este plan en línea.", self.pequeno)]
        return self._construir(elementos)

    def listado_sugerencias(self, sugerencias, filtro=""):
        elementos = [self._logo(), Paragraph("Listado de sugerencias", self.titulo)]
        detalle = f"Total: {len(sugerencias)}" + (f" · Filtro: «{escape(filtro)}»" if filtro else "")
        elementos += [Paragraph(detalle, self.normal), Spacer(1, 0.3 * cm)]
        filas = [["#", "Fecha", "Nombre", "Correo", "Mensaje"]]
        for s in sugerencias:
            filas.append([str(s.id), s.fecha.strftime("%d/%m/%Y %H:%M"), Paragraph(escape(s.nombre), self.pequeno),
                          Paragraph(escape(s.correo), self.pequeno), Paragraph(escape(s.mensaje), self.pequeno)])
        tabla = Table(filas, colWidths=[1.2 * cm, 3 * cm, 4.5 * cm, 5.5 * cm, 10 * cm], repeatRows=1)
        tabla.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), ROJO), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ROSA]),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d9a5a5")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        elementos.append(tabla)
        return self._construir(elementos, horizontal=True)
