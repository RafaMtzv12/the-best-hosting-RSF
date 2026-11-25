# The Best Hosting

Proyecto final de **Desarrollo de Aplicaciones Web**: sitio web de una empresa de hospedaje web, con parte pública y panel privado para administradores.

**Tecnologías:** Python 3 + Flask, SQLite + SQLAlchemy (ORM), HTML5, CSS3, Bootstrap 5, jQuery, JavaScript con clases y Chart.js. No usa PHP.

## Cómo correrlo

### En WSL (Ubuntu)

```bash
cd ~/proyectos/the-best-hosting
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
bash descargar_librerias.sh      # solo la primera vez, si app/static/vendor está vacío
python run.py
```

### En Windows (PowerShell)

```powershell
cd the-best-hosting
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```

Si PowerShell bloquea la activación: `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`.

Después se abre **http://localhost:5000**. Para detener el servidor: `Ctrl + C`.

| Parte | Dirección | Acceso |
|---|---|---|
| Sitio público | http://localhost:5000 | Libre |
| Administración | http://localhost:5000/admin/login | Usuario `admin`, contraseña `admin123` (de práctica) |

La base de datos (`the_best_hosting.db`) y los datos de ejemplo se crean solos la primera vez. Para empezar de cero: detener el servidor, borrar ese archivo y volver a correr `python run.py`.

### Correo del formulario de contacto (opcional)

Copiar `.env.example` como `.env` y llenar `MAIL_USERNAME` y `MAIL_PASSWORD` (contraseña de aplicación de Gmail). Sin esos datos, las sugerencias se guardan igual en la base de datos, pero no se envían por correo.

## Estructura

```
the-best-hosting/
├── run.py                  Arranca el servidor
├── config.py               Configuración (lee el archivo .env)
├── requirements.txt        Librerías de Python
├── descargar_librerias.sh  Descarga Bootstrap, jQuery y Chart.js
├── docs/                   Documentación del proyecto
└── app/
    ├── __init__.py         Clase Aplicacion: arma todo el sitio
    ├── extensions.py       Objeto db del ORM
    ├── models.py           Modelos (tablas)
    ├── patrones/           Patrón Singleton
    ├── controllers/        Controladores (rutas) y API REST
    ├── services/           Lógica de negocio
    ├── templates/          Vistas HTML (Jinja2)
    └── static/             CSS, JavaScript, imágenes, audio, video y librerías
```

Arquitectura **MVC** con capa de servicios: el controlador recibe la petición, el servicio hace la lógica, el modelo habla con la base de datos y la vista (plantilla) muestra el resultado.

## Dónde está cada requisito

| Requisito | Dónde |
|---|---|
| Sitio acorde al diseño de Photoshop | `templates/base.html`, `static/css/estilos.css`, imágenes en `static/img/` |
| Estrategia de búsqueda de servicios | `services/plan_service.py` (`buscar`), `static/js/buscador.js`, página `/servicios` |
| Altas, bajas y cambios de planes (solo admin) | `templates/admin/planes.html`, `static/js/admin.js` (`CrudTabla`) y `admin_planes.js`, API `/api/v1/planes` |
| Autenticación de administradores | `controllers/auth.py`, `controllers/seguridad.py`, `models.py` (`Usuario` con contraseña cifrada) |
| Responsivo | `static/css/estilos.css` (sección "Diseño responsivo") y Bootstrap |
| Video | `templates/public/compania.html`, archivo `static/media/presentacion.mp4` |
| Audio | Mensaje de bienvenida en Compañía y sonido del chatbot (`static/media/`) |
| Slideshow | Carrusel de Bootstrap en `templates/public/inicio.html` |
| Formulario de contacto por correo | `templates/_form_sugerencia.html`, `services/correo_service.py` |
| Sugerencias con paginación, Excel y PDF | `templates/admin/sugerencias.html`, `services/excel_service.py`, `services/pdf_service.py` |
| Clientes con imagen y link | `templates/public/clientes.html`, modelo `Cliente` |
| Búsqueda y PDF con ficha técnica de cada plan | `/servicios` y `/planes/<id>/ficha.pdf` (`PdfService.ficha_plan`, con QR) |
| Contador de visitas y usuarios conectados | `services/visitas_service.py`, clase `Presencia` en `static/js/sitio.js` |
| Preguntas frecuentes con acordeón | `templates/public/preguntas.html` |
| Dashboard 1: tipos de planes registrados | `templates/admin/dashboard.html`, `services/dashboard_service.py`, `static/js/dashboard.js` |
| Dashboard 2: planes a vencer en 10 días | Mismos archivos (botones "Próximos 10 días" y "Últimos 10 días") |
| Chatbot 24 horas | `templates/_chatbot.html`, `services/chatbot_service.py`, clase `Chatbot` en `sitio.js` |
| Base de datos | `models.py` (9 tablas) y `services/seed.py` (datos de ejemplo) |
| ORM | SQLAlchemy en `extensions.py`, `models.py` y todos los servicios |
| Patrón Singleton | `patrones/singleton.py`, usado por `ContadorVisitas`, `PdfService` y `CorreoService` |
| API REST | `controllers/api.py` (tabla de rutas al inicio del archivo) |
| Programación orientada a objetos | Clases en Python (controladores, servicios, modelos) y en JavaScript (`static/js/`) |
| Optimización de imágenes | `docs/optimizacion_imagenes.md` (de 1.8 MB a 104 KB) |
