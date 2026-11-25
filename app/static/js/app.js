/* Utilidades compartidas por el sitio público y el panel de administración (con jQuery). */
'use strict';

/** Cliente de la API REST propia (/api/v1). Devuelve promesas para usar async/await. */
class ApiClient {
  constructor(base = '/api/v1') {
    this.base = base;
  }

  peticion(metodo, ruta, datos = null, parametros = null) {
    let url = this.base + ruta;
    if (parametros) {
      const limpios = Object.fromEntries(Object.entries(parametros).filter(([, v]) => v !== '' && v != null));
      const query = $.param(limpios);
      if (query) url += '?' + query;
    }
    return new Promise((resolver, rechazar) => {
      $.ajax({
        url,
        method: metodo,
        contentType: 'application/json',
        dataType: 'json',
        data: datos ? JSON.stringify(datos) : undefined,
      })
        .done(resolver)
        .fail((xhr) => rechazar(xhr.responseJSON || { ok: false, mensaje: 'No se pudo conectar con el servidor.' }));
    });
  }

  get(ruta, parametros) { return this.peticion('GET', ruta, null, parametros); }
  post(ruta, datos) { return this.peticion('POST', ruta, datos); }
  put(ruta, datos) { return this.peticion('PUT', ruta, datos); }
  delete(ruta) { return this.peticion('DELETE', ruta); }
}

/** Mensajes emergentes (toasts de Bootstrap). */
class Notificador {
  static mostrar(mensaje, tipo = 'success') {
    const $toast = $(`
      <div class="toast align-items-center text-bg-${tipo} border-0" role="status" aria-live="polite">
        <div class="d-flex"><div class="toast-body"></div>
          <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Cerrar"></button>
        </div>
      </div>`);
    $toast.find('.toast-body').text(mensaje);
    $('#toasts').append($toast);
    const toast = new bootstrap.Toast($toast[0], { delay: 4500 });
    $toast.on('hidden.bs.toast', () => $toast.remove());
    toast.show();
  }

  static exito(mensaje) { Notificador.mostrar(mensaje, 'success'); }
  static error(mensaje) { Notificador.mostrar(mensaje, 'danger'); }
}

/** Ayudas para formularios: leer datos, mostrar errores por campo y limpiarlos. */
class Formulario {
  constructor($form) {
    this.$form = $form;
  }

  datos() {
    const datos = {};
    this.$form.find('input[name], select[name], textarea[name]').each((_, el) => {
      datos[el.name] = el.type === 'checkbox' ? el.checked : $(el).val().trim();
    });
    return datos;
  }

  llenar(datos) {
    this.$form.find('input[name], select[name], textarea[name]').each((_, el) => {
      const valor = datos[el.name];
      if (el.type === 'checkbox') el.checked = Boolean(valor);
      else $(el).val(Array.isArray(valor) ? valor.join('\n') : (valor ?? ''));
    });
  }

  limpiarErrores() {
    this.$form.find('.is-invalid').removeClass('is-invalid');
    this.$form.find('.invalid-feedback').text('');
  }

  mostrarErrores(errores = {}) {
    this.limpiarErrores();
    Object.entries(errores).forEach(([campo, mensaje]) => {
      const $campo = this.$form.find(`[name="${campo}"]`);
      $campo.addClass('is-invalid');
      $campo.siblings('.invalid-feedback').text(mensaje);
    });
    this.$form.find('.is-invalid').first().trigger('focus');
  }

  reiniciar() {
    this.$form[0].reset();
    this.limpiarErrores();
  }
}

/** Reglas de validación del lado del navegador (el servidor vuelve a validar). */
class Validador {
  static correo(valor) { return /^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$/.test(valor); }

  static sugerencia(datos) {
    const errores = {};
    if (!datos.nombre) errores.nombre = 'El nombre es obligatorio.';
    if (!datos.correo) errores.correo = 'El correo es obligatorio.';
    else if (!Validador.correo(datos.correo)) errores.correo = 'Escribe un correo válido (ejemplo: nombre@dominio.com).';
    if (!datos.mensaje) errores.mensaje = 'El mensaje es obligatorio.';
    else if (datos.mensaje.length < 10) errores.mensaje = 'El mensaje debe tener al menos 10 caracteres.';
    return errores;
  }
}

/** Formato de dinero y escapado de texto para insertar HTML de forma segura. */
class Formato {
  static dinero(valor, decimales = 0) {
    return '$' + Number(valor).toLocaleString('es-MX', { minimumFractionDigits: decimales, maximumFractionDigits: decimales });
  }

  static escapar(texto) {
    return $('<div>').text(texto ?? '').html();
  }

  static fecha(iso) {
    const [a, m, d] = iso.split('-');
    return `${d}/${m}/${a}`;
  }
}
