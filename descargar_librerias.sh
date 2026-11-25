#!/usr/bin/env bash
# Descarga las librerías del frontend (Bootstrap, jQuery y Chart.js) a app/static/vendor.
# Se corre UNA sola vez; después los archivos se suben a GitHub junto con el proyecto,
# así el sitio funciona aunque no haya internet en la exposición.
set -e
cd "$(dirname "$0")/app/static/vendor"
curl -fsSLo bootstrap.min.css       https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css
curl -fsSLo bootstrap.bundle.min.js https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js
curl -fsSLo jquery.min.js           https://code.jquery.com/jquery-3.7.1.min.js
curl -fsSLo chart.umd.js            https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.js
echo "Librerías descargadas:"
ls -lh
