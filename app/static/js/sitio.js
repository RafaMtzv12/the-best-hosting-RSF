/* Comportamiento del sitio público: contador en vivo, formulario de sugerencias y chatbot. */
'use strict';

/** Mantiene actualizado el contador de visitas y de usuarios conectados. */
class Presencia {
  constructor(api, intervaloMs = 60000) {
    this.api = api;
    this.intervaloMs = intervaloMs;
  }

  iniciar() {
    setInterval(() => this.latido(), this.intervaloMs);
  }

  async latido() {
    if (document.hidden) return; // si la pestaña no está visible, no cuenta como activo
    try {
      const { datos } = await this.api.post('/presencia', {});
      $('[data-conectados]').text(datos.conectados);
      $('[data-visitas]').html([...datos.visitas_digitos].map((d) => `<span>${d}</span>`).join(''));
    } catch (e) { /* sin conexión: se intenta en el siguiente minuto */ }
  }
}

/** Formulario de contacto: valida, envía a la API y avisa el resultado. */
class FormularioSugerencia {
  constructor($form, api) {
    this.form = new Formulario($form);
    this.$boton = $form.find('button[type="submit"]');
    this.api = api;
    $form.on('submit', (e) => { e.preventDefault(); this.enviar(); });
  }

  async enviar() {
    const datos = this.form.datos();
    const errores = Validador.sugerencia(datos);
    if (Object.keys(errores).length) {
      this.form.mostrarErrores(errores);
      return;
    }
    this.form.limpiarErrores();
    this.$boton.prop('disabled', true).text('Enviando…');
    try {
      const respuesta = await this.api.post('/sugerencias', datos);
      this.form.reiniciar();
      Notificador.exito(respuesta.mensaje);
    } catch (error) {
      this.form.mostrarErrores(error.errores);
      Notificador.error(error.mensaje || 'No se pudo enviar tu mensaje.');
    } finally {
      this.$boton.prop('disabled', false).text('Enviar sugerencia');
    }
  }
}

/** Chatbot de ayuda en línea 24/7. Las respuestas vienen de POST /api/v1/chatbot. */
class Chatbot {
  constructor(api) {
    this.api = api;
    this.$raiz = $('#chatbot');
    this.$panel = $('#chatbotPanel');
    this.$mensajes = this.$panel.find('.chatbot-mensajes');
    this.$sugerencias = this.$panel.find('.chatbot-sugerencias');
    this.$entrada = $('#chatbotTexto');
    this.audio = document.getElementById('chatbotAudio');
    this.sonidoActivo = this.leerPreferencia();
    this.saludado = false;
    this.enlazarEventos();
    this.pintarBotonSonido();
  }

  enlazarEventos() {
    $(document).on('click', '[data-abrir-chat]', () => this.abrir());
    this.$panel.find('.chatbot-cerrar').on('click', () => this.cerrar());
    this.$panel.find('.chatbot-sonido').on('click', () => this.alternarSonido());
    this.$panel.find('.chatbot-form').on('submit', (e) => {
      e.preventDefault();
      this.enviar(this.$entrada.val());
    });
    this.$sugerencias.on('click', 'button', (e) => this.enviar($(e.currentTarget).text()));
  }

  abrir() {
    this.$panel.prop('hidden', false);
    this.$raiz.addClass('abierto').find('.chatbot-boton').attr('aria-expanded', 'true');
    if (!this.saludado) {
      this.saludado = true;
      this.agregar('¡Hola! 👋 Soy el asistente virtual de The Best Hosting. ¿En qué te puedo ayudar?', 'bot');
      this.mostrarSugerencias(['Planes y precios', 'Dominios', 'Soporte técnico', 'Formas de pago']);
    }
    this.$entrada.trigger('focus');
  }

  cerrar() {
    this.$panel.prop('hidden', true);
    this.$raiz.removeClass('abierto').find('.chatbot-boton').attr('aria-expanded', 'false');
  }

  async enviar(texto) {
    texto = (texto || '').trim();
    if (!texto) return;
    this.$entrada.val('');
    this.mostrarSugerencias([]);
    this.agregar(Formato.escapar(texto), 'usuario');
    const $escribiendo = this.agregar('<span class="escribiendo"><i></i><i></i><i></i></span>', 'bot');
    try {
      const [{ datos }] = await Promise.all([this.api.post('/chatbot', { mensaje: texto }), this.esperar(600)]);
      $escribiendo.remove();
      this.agregar(datos.respuesta, 'bot'); // HTML de la base de conocimiento (contenido propio)
      this.mostrarSugerencias(datos.sugerencias);
    } catch (e) {
      $escribiendo.remove();
      this.agregar('Uy, no pude conectarme. Llámanos al (844) 414 5676.', 'bot');
    }
    this.sonar();
  }

  agregar(html, autor) {
    const $msg = $(`<div class="chat-msg chat-${autor}"></div>`).html(html);
    this.$mensajes.append($msg).scrollTop(this.$mensajes[0].scrollHeight);
    return $msg;
  }

  mostrarSugerencias(lista) {
    this.$sugerencias.empty();
    (lista || []).forEach((s) => this.$sugerencias.append($('<button type="button"></button>').text(s)));
  }

  esperar(ms) { return new Promise((r) => setTimeout(r, ms)); }

  sonar() {
    if (!this.sonidoActivo || !this.audio) return;
    this.audio.currentTime = 0;
    this.audio.play().catch(() => {}); // algunos navegadores bloquean el audio: no pasa nada
  }

  alternarSonido() {
    this.sonidoActivo = !this.sonidoActivo;
    try { localStorage.setItem('chatbotSonido', this.sonidoActivo ? '1' : '0'); } catch (e) { /* sin almacenamiento */ }
    this.pintarBotonSonido();
  }

  leerPreferencia() {
    try { return localStorage.getItem('chatbotSonido') !== '0'; } catch (e) { return true; }
  }

  pintarBotonSonido() {
    this.$panel.find('.chatbot-sonido').html(this.sonidoActivo ? '&#128266;' : '&#128263;')
      .attr('aria-pressed', String(this.sonidoActivo));
  }
}

/** Arranca todo lo del sitio público. */
class SitioPublico {
  constructor() {
    this.api = new ApiClient();
  }

  iniciar() {
    new Presencia(this.api).iniciar();
    new Chatbot(this.api);
    $('[data-formulario-sugerencia]').each((_, form) => new FormularioSugerencia($(form), this.api));
  }
}

$(() => new SitioPublico().iniciar());
