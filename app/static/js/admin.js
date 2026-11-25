/* Clases del panel de administración. */
'use strict';

/** Ventana de confirmación (modal de Bootstrap) que devuelve una promesa true/false. */
class Confirmacion {
  static preguntar(texto) {
    const $modal = $('#modalConfirmar');
    const modal = bootstrap.Modal.getOrCreateInstance($modal[0]);
    $modal.find('[data-texto]').text(texto);
    return new Promise((resolver) => {
      let aceptado = false;
      $modal.find('[data-aceptar]').off('click').on('click', () => { aceptado = true; modal.hide(); });
      $modal.off('hidden.bs.modal').on('hidden.bs.modal', () => resolver(aceptado));
      modal.show();
    });
  }
}

/**
 * Tabla con altas, bajas y cambios (CRUD) conectada a un recurso de la API REST.
 * Las clases hijas (PlanesCrud, ContratosCrud) solo dicen cómo dibujar cada fila.
 */
class CrudTabla {
  constructor({ api, recurso, nombre, parametrosLista = {} }) {
    this.api = api;
    this.recurso = recurso; // por ejemplo '/planes'
    this.nombre = nombre; // por ejemplo 'plan'
    this.parametrosLista = parametrosLista;
    this.registros = [];
    this.editandoId = null;
    this.$tabla = $('#tabla');
    this.$modal = $('#modalForm');
    this.modal = new bootstrap.Modal(this.$modal[0]);
    this.form = new Formulario($('#formulario'));
    this.$guardar = this.$modal.find('[data-guardar]');
    this.temporizador = null;
  }

  iniciar() {
    $('[data-nuevo]').on('click', () => this.nuevo());
    $('#formulario').on('submit', (e) => { e.preventDefault(); this.guardar(); });
    this.$tabla.on('click', '[data-editar]', (e) => this.editar(Number($(e.currentTarget).data('editar'))));
    this.$tabla.on('click', '[data-eliminar]', (e) => this.eliminar(Number($(e.currentTarget).data('eliminar'))));
    $('#buscarTabla').on('input', () => {
      clearTimeout(this.temporizador);
      this.temporizador = setTimeout(() => this.cargar(), 300);
    });
    this.cargar();
  }

  async cargar() {
    const q = $('#buscarTabla').val() || '';
    try {
      const respuesta = await this.api.get(this.recurso, { ...this.parametrosLista, q });
      this.registros = respuesta.datos;
      this.dibujar();
    } catch (error) {
      Notificador.error(error.mensaje);
    }
  }

  dibujar() {
    const columnas = this.$tabla.closest('table').find('thead th').length;
    if (!this.registros.length) {
      this.$tabla.html(`<tr><td colspan="${columnas}" class="text-center text-muted py-4">Sin registros.</td></tr>`);
      return;
    }
    this.$tabla.html(this.registros.map((r) => this.fila(r)).join(''));
  }

  botones(id) {
    const svg = (d) => `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${d}</svg>`;
    const lapiz = svg('<path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z"/>');
    const bote = svg('<path d="M3 6h18M8 6V4h8v2M19 6l-1 14H6L5 6"/><path d="M10 11v6M14 11v6"/>');
    return `<td class="text-end text-nowrap">
      <button class="btn btn-sm btn-outline-secondary" data-editar="${id}" aria-label="Editar">${lapiz} Editar</button>
      <button class="btn btn-sm btn-outline-danger btn-icono" data-eliminar="${id}" aria-label="Eliminar">${bote}</button></td>`;
  }

  /** Cada clase hija regresa el HTML de una fila. */
  fila(_registro) { throw new Error('Implementar fila() en la clase hija'); }

  valoresNuevo() { return {}; }

  nuevo() {
    this.editandoId = null;
    this.form.reiniciar();
    this.form.llenar(this.valoresNuevo());
    this.$modal.find('.modal-title').text(`Nuevo ${this.nombre}`);
    this.modal.show();
  }

  editar(id) {
    const registro = this.registros.find((r) => r.id === id);
    if (!registro) return;
    this.editandoId = id;
    this.form.reiniciar();
    this.form.llenar(registro);
    this.$modal.find('.modal-title').text(`Editar ${this.nombre}`);
    this.modal.show();
  }

  async guardar() {
    this.$guardar.prop('disabled', true); // evita guardar dos veces con doble clic
    try {
      const datos = this.form.datos();
      const respuesta = this.editandoId
        ? await this.api.put(`${this.recurso}/${this.editandoId}`, datos)
        : await this.api.post(this.recurso, datos);
      this.modal.hide();
      Notificador.exito(respuesta.mensaje);
      await this.cargar();
    } catch (error) {
      this.form.mostrarErrores(error.errores);
      Notificador.error(error.mensaje);
    } finally {
      this.$guardar.prop('disabled', false);
    }
  }

  async eliminar(id) {
    const registro = this.registros.find((r) => r.id === id);
    const nombre = registro ? this.descripcion(registro) : `#${id}`;
    if (!(await Confirmacion.preguntar(`¿Eliminar ${this.nombre} «${nombre}»? Esta acción no se puede deshacer.`))) return;
    try {
      const respuesta = await this.api.delete(`${this.recurso}/${id}`);
      Notificador.exito(respuesta.mensaje);
      await this.cargar();
    } catch (error) {
      Notificador.error(error.mensaje);
    }
  }

  descripcion(registro) { return registro.nombre || `#${registro.id}`; }
}

/** Botones de eliminar en la lista paginada de sugerencias. */
class SugerenciasAdmin {
  constructor(api) {
    this.api = api;
  }

  iniciar() {
    $('[data-eliminar-sugerencia]').on('click', (e) => this.eliminar($(e.currentTarget).data('eliminar-sugerencia')));
  }

  async eliminar(id) {
    if (!(await Confirmacion.preguntar(`¿Eliminar la sugerencia #${id}?`))) return;
    try {
      await this.api.delete(`/sugerencias/${id}`);
      location.reload();
    } catch (error) {
      Notificador.error(error.mensaje);
    }
  }
}
