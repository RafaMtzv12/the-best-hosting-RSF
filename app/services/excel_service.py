"""Exportación a Excel con openpyxl."""
from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill


class ExcelService:
    COLOR_ENCABEZADO = "8B0000"

    def exportar_sugerencias(self, sugerencias):
        libro = Workbook()
        hoja = libro.active
        hoja.title = "Sugerencias"
        encabezados = ["#", "Fecha", "Nombre", "Correo", "Mensaje", "Correo enviado"]
        hoja.append(encabezados)
        for s in sugerencias:
            hoja.append([s.id, s.fecha, s.nombre, s.correo, s.mensaje, "Sí" if s.correo_enviado else "No"])

        # Formato: encabezado rojo, anchos de columna, fechas legibles y filtros
        for celda in hoja[1]:
            celda.font = Font(bold=True, color="FFFFFF")
            celda.fill = PatternFill("solid", fgColor=self.COLOR_ENCABEZADO)
            celda.alignment = Alignment(horizontal="center")
        for letra, ancho in zip("ABCDEF", [6, 18, 28, 32, 70, 15]):
            hoja.column_dimensions[letra].width = ancho
        for fila in hoja.iter_rows(min_row=2):
            fila[1].number_format = "DD/MM/YYYY HH:MM"
            fila[4].alignment = Alignment(wrap_text=True, vertical="top")
        hoja.freeze_panes = "A2"
        hoja.auto_filter.ref = hoja.dimensions

        buffer = BytesIO()
        libro.save(buffer)
        return buffer.getvalue()
