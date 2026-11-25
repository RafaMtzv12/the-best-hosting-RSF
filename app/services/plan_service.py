"""Lógica de los planes de hosting: búsqueda y mantenimiento (altas, bajas y cambios)."""
from sqlalchemy import or_

from ..extensions import db
from ..models import Plan, TipoPlan
from .errores import ErrorNegocio
from .validador import PlanValidator


class PlanService:
    ORDENES = {
        "precio": Plan.precio.asc(),
        "precio_desc": Plan.precio.desc(),
        "nombre": Plan.nombre.asc(),
    }

    def buscar(self, texto="", tipo=None, precio_max=None, orden="precio", solo_activos=True):
        """Estrategia de búsqueda: texto libre en nombre, lema, descripción y características,
        más filtros por tipo de plan y precio máximo."""
        consulta = db.select(Plan).join(TipoPlan)
        if solo_activos:
            consulta = consulta.where(Plan.activo.is_(True))
        texto = (texto or "").strip()
        if texto:
            for palabra in texto.split():  # cada palabra debe aparecer en algún campo
                patron = f"%{palabra}%"
                consulta = consulta.where(or_(
                    Plan.nombre.ilike(patron), Plan.lema.ilike(patron),
                    Plan.descripcion.ilike(patron), Plan.caracteristicas.ilike(patron),
                    Plan.espacio.ilike(patron), TipoPlan.nombre.ilike(patron),
                ))
        if tipo:
            if str(tipo).isdigit():
                consulta = consulta.where(Plan.tipo_id == int(tipo))
            else:
                consulta = consulta.where(TipoPlan.clave == tipo)
        if precio_max:
            try:
                consulta = consulta.where(Plan.precio <= float(precio_max))
            except ValueError:
                pass
        consulta = consulta.order_by(self.ORDENES.get(orden, Plan.precio.asc()))
        return db.session.execute(consulta).scalars().all()

    def destacados(self):
        consulta = db.select(Plan).where(Plan.activo.is_(True), Plan.destacado.is_(True)).order_by(Plan.precio)
        return db.session.execute(consulta.limit(4)).scalars().all()

    def tipos(self):
        return db.session.execute(db.select(TipoPlan).order_by(TipoPlan.id)).scalars().all()

    def obtener(self, plan_id, solo_activos=False):
        plan = db.session.get(Plan, plan_id)
        if plan is None or (solo_activos and not plan.activo):
            raise ErrorNegocio("El plan no existe.", 404)
        return plan

    def crear(self, datos):
        limpio = PlanValidator(datos).validar()
        self._validar_unico(limpio["nombre"])
        self._validar_tipo(limpio["tipo_id"])
        plan = Plan()
        self._asignar(plan, limpio)
        db.session.add(plan)
        db.session.commit()
        return plan

    def actualizar(self, plan_id, datos):
        plan = self.obtener(plan_id)
        limpio = PlanValidator(datos).validar()
        self._validar_unico(limpio["nombre"], excluir_id=plan.id)
        self._validar_tipo(limpio["tipo_id"])
        self._asignar(plan, limpio)
        db.session.commit()
        return plan

    def eliminar(self, plan_id):
        plan = self.obtener(plan_id)
        if plan.contratos:
            raise ErrorNegocio(
                f"No se puede eliminar: {len(plan.contratos)} contrato(s) usan este plan. "
                "Puedes desactivarlo para que ya no se muestre en el sitio.", 409)
        db.session.delete(plan)
        db.session.commit()

    # --- auxiliares privados ---
    def _asignar(self, plan, limpio):
        for campo, valor in limpio.items():
            if campo == "icono" and not valor:
                continue
            setattr(plan, campo, valor)

    def _validar_unico(self, nombre, excluir_id=None):
        consulta = db.select(Plan).where(Plan.nombre == nombre)
        existente = db.session.execute(consulta).scalar_one_or_none()
        if existente and existente.id != excluir_id:
            raise ErrorNegocio("Ya existe un plan con ese nombre.", 409, {"nombre": "Nombre repetido."})

    def _validar_tipo(self, tipo_id):
        if db.session.get(TipoPlan, tipo_id) is None:
            raise ErrorNegocio("El tipo de plan no existe.", 422, {"tipo_id": "Tipo inválido."})
