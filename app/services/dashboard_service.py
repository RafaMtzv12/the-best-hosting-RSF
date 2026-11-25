"""Datos de los 2 dashboards del administrador.

1. Análisis de los tipos de planes registrados (planes y contratos por tipo).
2. Planes (contratos) que vencen en un periodo de 10 días.
"""
from datetime import date, timedelta

from sqlalchemy import distinct, func

from ..extensions import db
from ..models import Contrato, Plan, Sugerencia, TipoPlan

DIAS_SEMANA = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]


class DashboardService:
    DIAS = 10

    def tipos_planes(self):
        consulta = (
            db.select(TipoPlan.nombre, func.count(distinct(Plan.id)), func.count(distinct(Contrato.id)))
            .select_from(TipoPlan)
            .outerjoin(Plan, Plan.tipo_id == TipoPlan.id)
            .outerjoin(Contrato, Contrato.plan_id == Plan.id)
            .group_by(TipoPlan.id, TipoPlan.nombre)
            .order_by(TipoPlan.id)
        )
        filas = db.session.execute(consulta).all()
        return {
            "etiquetas": [f[0] for f in filas],
            "planes": [f[1] for f in filas],
            "contratos": [f[2] for f in filas],
        }

    def vencimientos(self, modo="proximos"):
        """modo='proximos': de hoy a 9 días adelante. modo='ultimos': los 10 días anteriores hasta hoy."""
        hoy = date.today()
        if modo == "ultimos":
            inicio, fin = hoy - timedelta(days=self.DIAS - 1), hoy
        else:
            modo, inicio, fin = "proximos", hoy, hoy + timedelta(days=self.DIAS - 1)
        consulta = (db.select(Contrato)
                    .where(Contrato.fecha_vencimiento.between(inicio, fin))
                    .order_by(Contrato.fecha_vencimiento))
        contratos = db.session.execute(consulta).scalars().all()

        dias = [inicio + timedelta(days=i) for i in range(self.DIAS)]
        conteo = {d: 0 for d in dias}
        for c in contratos:
            conteo[c.fecha_vencimiento] += 1
        return {
            "modo": modo,
            "desde": inicio.strftime("%d/%m/%Y"),
            "hasta": fin.strftime("%d/%m/%Y"),
            "etiquetas": [f"{DIAS_SEMANA[d.weekday()]} {d:%d/%m}" for d in dias],
            "totales": [conteo[d] for d in dias],
            "contratos": [c.to_dict() for c in contratos],
        }

    def tarjetas(self):
        hoy = date.today()
        contar = lambda consulta: db.session.execute(consulta).scalar_one()  # noqa: E731
        return {
            "planes_activos": contar(db.select(func.count(Plan.id)).where(Plan.activo.is_(True))),
            "contratos_vigentes": contar(db.select(func.count(Contrato.id)).where(Contrato.fecha_vencimiento >= hoy)),
            "por_vencer": contar(db.select(func.count(Contrato.id)).where(
                Contrato.fecha_vencimiento.between(hoy, hoy + timedelta(days=self.DIAS - 1)))),
            "sugerencias": contar(db.select(func.count(Sugerencia.id))),
        }
