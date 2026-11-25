"""Lógica de los contratos (planes contratados por clientes)."""
from sqlalchemy import or_

from ..extensions import db
from ..models import Contrato, Plan
from .errores import ErrorNegocio
from .validador import ContratoValidator


class ContratoService:
    def listar(self, texto=""):
        consulta = db.select(Contrato).join(Plan)
        texto = (texto or "").strip()
        if texto:
            patron = f"%{texto}%"
            consulta = consulta.where(or_(
                Contrato.cliente_nombre.ilike(patron), Contrato.dominio.ilike(patron),
                Contrato.correo.ilike(patron), Plan.nombre.ilike(patron),
            ))
        consulta = consulta.order_by(Contrato.fecha_vencimiento)
        return db.session.execute(consulta).scalars().all()

    def obtener(self, contrato_id):
        contrato = db.session.get(Contrato, contrato_id)
        if contrato is None:
            raise ErrorNegocio("El contrato no existe.", 404)
        return contrato

    def crear(self, datos):
        limpio = ContratoValidator(datos).validar()
        self._validar_plan(limpio["plan_id"])
        contrato = Contrato(**limpio)
        db.session.add(contrato)
        db.session.commit()
        return contrato

    def actualizar(self, contrato_id, datos):
        contrato = self.obtener(contrato_id)
        limpio = ContratoValidator(datos).validar()
        self._validar_plan(limpio["plan_id"])
        for campo, valor in limpio.items():
            setattr(contrato, campo, valor)
        db.session.commit()
        return contrato

    def eliminar(self, contrato_id):
        db.session.delete(self.obtener(contrato_id))
        db.session.commit()

    def _validar_plan(self, plan_id):
        if db.session.get(Plan, plan_id) is None:
            raise ErrorNegocio("El plan no existe.", 422, {"plan_id": "Plan inválido."})
