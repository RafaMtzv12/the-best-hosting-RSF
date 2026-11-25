/* Mantenimiento de planes: altas, bajas y cambios (hereda de CrudTabla). */
'use strict';

class PlanesCrud extends CrudTabla {
  constructor(api) {
    super({ api, recurso: '/planes', nombre: 'plan', parametrosLista: { todos: 1, orden: 'nombre' } });
  }

  valoresNuevo() {
    return { periodo: 'año', transferencia: 'Ilimitada', ram: 'Compartida', activo: true, icono: 'planes/starter.webp' };
  }

  fila(p) {
    const e = Formato.escapar;
    const anterior = p.precio_anterior ? `<del class="text-muted small">${Formato.dinero(p.precio_anterior)}</del> ` : '';
    return `<tr>
      <td><img src="/static/img/${e(p.icono)}" alt="" width="28" height="28" class="me-2">${e(p.nombre)}</td>
      <td>${e(p.tipo)}</td>
      <td class="text-end text-nowrap">${anterior}<b>${Formato.dinero(p.precio, 2)}</b>/${e(p.periodo)}</td>
      <td>${e(p.espacio)}</td>
      <td>${p.destacado ? '<span class="badge text-bg-warning">Destacado</span>' : ''}</td>
      <td>${p.activo ? '<span class="badge text-bg-success">Activo</span>' : '<span class="badge text-bg-secondary">Inactivo</span>'}</td>
      ${this.botones(p.id)}
    </tr>`;
  }
}

$(() => new PlanesCrud(new ApiClient()).iniciar());
