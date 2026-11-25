/* Buscador de planes: consulta GET /api/v1/planes mientras el usuario escribe o cambia filtros. */
'use strict';

class BuscadorPlanes {
  constructor(api) {
    this.api = api;
    this.$form = $('#buscador');
    this.$resultados = $('#resultados');
    this.$estado = $('#estadoBusqueda');
    this.plantilla = document.getElementById('plantillaPlan');
    this.temporizador = null;
    this.ultimaPeticion = 0;
  }

  iniciar() {
    this.$form.on('submit', (e) => { e.preventDefault(); this.buscar(); });
    this.$form.find('input').on('input', () => this.buscarConPausa());
    this.$form.find('select').on('change', () => this.buscar());
    this.buscar();
  }

  /** Espera 300 ms después de la última tecla para no consultar en cada letra. */
  buscarConPausa() {
    clearTimeout(this.temporizador);
    this.temporizador = setTimeout(() => this.buscar(), 300);
  }

  filtros() {
    return {
      q: $('#q').val().trim(),
      tipo: $('#tipo').val(),
      precio_max: $('#precio_max').val(),
      orden: $('#orden').val(),
    };
  }

  async buscar() {
    const filtros = this.filtros();
    const numero = ++this.ultimaPeticion; // si llegan respuestas viejas, se ignoran
    this.actualizarUrl(filtros);
    this.$estado.text('Buscando…');
    try {
      const respuesta = await this.api.get('/planes', filtros);
      if (numero !== this.ultimaPeticion) return;
      this.mostrar(respuesta.datos, filtros);
    } catch (error) {
      this.$estado.text(error.mensaje || 'No se pudo realizar la búsqueda.');
    }
  }

  mostrar(planes, filtros) {
    this.$resultados.empty();
    if (!planes.length) {
      this.$estado.html(`No encontramos planes${filtros.q ? ` con «${Formato.escapar(filtros.q)}»` : ''}. Prueba con otras palabras o
        <button type="button" class="boton-enlace" data-abrir-chat>pregúntale al asistente</button>.`);
      return;
    }
    this.$estado.text(`${planes.length} plan${planes.length === 1 ? '' : 'es'} encontrado${planes.length === 1 ? '' : 's'}`);
    planes.forEach((plan) => this.$resultados.append(this.tarjeta(plan)));
  }

  tarjeta(plan) {
    const nodo = this.plantilla.content.cloneNode(true);
    const $t = $(nodo);
    const campo = (nombre) => $t.find(`[data-campo="${nombre}"]`);
    campo('nombre').text(plan.nombre);
    campo('icono').attr('src', `/static/img/${plan.icono}`);
    campo('precio_anterior').text(plan.precio_anterior ? Formato.dinero(plan.precio_anterior) : '');
    campo('precio').text(Formato.dinero(plan.precio));
    campo('periodo').text('/' + plan.periodo);
    campo('tipo').text(plan.tipo);
    campo('lema').text(plan.lema || '');
    campo('caracteristicas').append(plan.caracteristicas.slice(0, 6).map((c) => $('<li>').text(c)));
    campo('detalles').attr('href', `/planes/${plan.id}`);
    campo('pdf').attr('href', `/planes/${plan.id}/ficha.pdf`);
    return $t.children();
  }

  /** Guarda los filtros en la dirección, así se puede compartir o recargar la búsqueda. */
  actualizarUrl(filtros) {
    const limpios = Object.fromEntries(Object.entries(filtros).filter(([k, v]) => v && !(k === 'orden' && v === 'precio')));
    const query = $.param(limpios);
    history.replaceState(null, '', location.pathname + (query ? '?' + query : ''));
  }
}

$(() => new BuscadorPlanes(new ApiClient()).iniciar());
