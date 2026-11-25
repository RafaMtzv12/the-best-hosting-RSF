/* Mantenimiento de contratos (hereda de CrudTabla). */
'use strict';

class ContratosCrud extends CrudTabla {
  constructor(api) {
    super({ api, recurso: '/contratos', nombre: 'contrato' });
  }

  valoresNuevo() {
    const hoy = new Date();
    const enUnAnio = new Date(hoy);
    enUnAnio.setFullYear(hoy.getFullYear() + 1);
    const iso = (f) => f.toISOString().slice(0, 10);
    return { fecha_inicio: iso(hoy), fecha_vencimiento: iso(enUnAnio) };
  }

  estado(dias) {
    if (dias < 0) return `<span class="badge text-bg-secondary">Vencido hace ${-dias} d</span>`;
    if (dias < 10) return `<span class="badge text-bg-warning">Vence en ${dias} d</span>`;
    return `<span class="badge text-bg-success">Vigente (${dias} d)</span>`;
  }

  fila(c) {
    const e = Formato.escapar;
    return `<tr>
      <td>${e(c.cliente_nombre)}<br><small class="text-muted">${e(c.correo)}</small></td>
      <td>${e(c.dominio)}</td>
      <td>${e(c.plan)}</td>
      <td class="text-nowrap">${Formato.fecha(c.fecha_inicio)}</td>
      <td class="text-nowrap">${Formato.fecha(c.fecha_vencimiento)}</td>
      <td>${this.estado(c.dias_restantes)}</td>
      ${this.botones(c.id)}
    </tr>`;
  }

  descripcion(c) { return c.dominio; }
}

$(() => new ContratosCrud(new ApiClient()).iniciar());
