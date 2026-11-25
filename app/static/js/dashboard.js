/* Dashboards con Chart.js: 1) tipos de planes registrados  2) planes a vencer en 10 días. */
'use strict';

class Dashboard {
  static COLORES = ['#8b0000', '#d35400', '#7f8c8d', '#2c3e50', '#c0392b', '#16a085'];

  constructor(api) {
    this.api = api;
    this.graficas = {};
  }

  async iniciar() {
    $('[data-modo]').on('click', (e) => {
      $('[data-modo]').removeClass('active');
      $(e.currentTarget).addClass('active');
      this.cargarVencimientos($(e.currentTarget).data('modo'));
    });
    await Promise.all([this.cargarTipos(), this.cargarVencimientos('proximos')]);
  }

  /** Crea la gráfica o la reemplaza si ya existía. */
  dibujar(id, configuracion) {
    if (this.graficas[id]) this.graficas[id].destroy();
    this.graficas[id] = new Chart(document.getElementById(id), configuracion);
  }

  async cargarTipos() {
    try {
      const { datos } = await this.api.get('/dashboard/tipos');
      this.dibujar('graficaPlanesTipo', {
        type: 'doughnut',
        data: { labels: datos.etiquetas, datasets: [{ data: datos.planes, backgroundColor: Dashboard.COLORES }] },
        options: { maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } } },
      });
      this.dibujar('graficaContratosTipo', {
        type: 'bar',
        data: {
          labels: datos.etiquetas,
          datasets: [
            { label: 'Planes', data: datos.planes, backgroundColor: '#c9a3a3' },
            { label: 'Contratos', data: datos.contratos, backgroundColor: '#8b0000' },
          ],
        },
        options: { maintainAspectRatio: false, scales: { y: { beginAtZero: true, ticks: { precision: 0 } } } },
      });
    } catch (error) {
      Notificador.error(error.mensaje);
    }
  }

  async cargarVencimientos(modo) {
    try {
      const { datos } = await this.api.get('/dashboard/vencimientos', { modo });
      $('#rangoVencimientos').text(`(${datos.desde} al ${datos.hasta})`);
      this.dibujar('graficaVencimientos', {
        type: 'bar',
        data: {
          labels: datos.etiquetas,
          datasets: [{ label: modo === 'ultimos' ? 'Vencieron' : 'Vencen', data: datos.totales, backgroundColor: '#d35400', borderRadius: 4 }],
        },
        options: { maintainAspectRatio: false, plugins: { legend: { display: false } },
          scales: { y: { beginAtZero: true, ticks: { precision: 0 } } } },
      });
      this.tabla(datos.contratos);
    } catch (error) {
      Notificador.error(error.mensaje);
    }
  }

  tabla(contratos) {
    const e = Formato.escapar;
    if (!contratos.length) {
      $('#tablaVencimientos').html('<tr><td colspan="5" class="text-center text-muted">No hay vencimientos en este periodo.</td></tr>');
      return;
    }
    $('#tablaVencimientos').html(contratos.map((c) => {
      const clase = c.dias_restantes < 0 ? 'text-bg-secondary' : c.dias_restantes <= 3 ? 'text-bg-danger' : 'text-bg-warning';
      const texto = c.dias_restantes < 0 ? `hace ${-c.dias_restantes}` : c.dias_restantes === 0 ? 'hoy' : c.dias_restantes;
      return `<tr><td>${e(c.cliente_nombre)}</td><td>${e(c.dominio)}</td><td>${e(c.plan)}</td>
        <td>${Formato.fecha(c.fecha_vencimiento)}</td><td><span class="badge ${clase}">${texto}</span></td></tr>`;
    }).join(''));
  }
}

$(() => new Dashboard(new ApiClient()).iniciar());
