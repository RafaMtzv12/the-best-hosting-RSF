"""Seeder: llena la base de datos con datos de ejemplo la primera vez que se ejecuta.

Cada método revisa si su tabla está vacía, así que correrlo varias veces no duplica nada.
"""
import random
from datetime import date, datetime, timedelta

from ..extensions import db
from ..models import (Cliente, Contrato, Plan, PreguntaFrecuente, RespuestaChatbot, Sugerencia, TipoPlan,
                      Usuario)


class Seeder:
    def ejecutar(self):
        self.administrador()
        self.tipos_y_planes()
        self.clientes()
        self.contratos()
        self.preguntas()
        self.chatbot()
        self.sugerencias()
        db.session.commit()

    @staticmethod
    def _vacia(modelo):
        return db.session.execute(db.select(modelo.id).limit(1)).first() is None

    def administrador(self):
        if self._vacia(Usuario):
            admin = Usuario(usuario="admin", nombre="Administrador")
            admin.asignar_password("admin123")  # contraseña de práctica: cámbiala para producción
            db.session.add(admin)

    def tipos_y_planes(self):
        if not self._vacia(TipoPlan):
            return
        tipos = {
            "compartido": TipoPlan(clave="compartido", nombre="Hosting compartido",
                                   descripcion="Ideal para sitios personales, blogs y pequeñas empresas."),
            "vps": TipoPlan(clave="vps", nombre="Servidor VPS",
                            descripcion="Recursos garantizados y acceso root para proyectos que crecen."),
            "dedicado": TipoPlan(clave="dedicado", nombre="Servidor dedicado",
                                 descripcion="Un servidor físico completo solo para ti, máximo rendimiento."),
            "reseller": TipoPlan(clave="reseller", nombre="Reseller",
                                 descripcion="Revende hosting con tu propia marca y administra a tus clientes."),
        }
        db.session.add_all(tipos.values())
        comunes = "Configuración instantánea\nTransferencia ilimitada\nCertificado SSL gratis"
        planes = [
            # Los 4 planes del diseño de Photoshop
            dict(nombre="Starter", tipo=tipos["compartido"], precio_anterior=580, precio=250, destacado=True,
                 lema="¡Todo lo que necesitas para comenzar!", icono="planes/starter.webp", espacio="10 GB",
                 dominios="1", cuentas_correo="5", bases_datos="1",
                 descripcion="El plan perfecto para tu primera página web o tu blog personal.",
                 caracteristicas="Espacio web: 10 GB\nRegistro de dominio\n" + comunes),
            dict(nombre="Básico", tipo=tipos["compartido"], precio_anterior=955, precio=455, destacado=True,
                 lema="¡La mejor solución para grandes proyectos!", icono="planes/basico.webp", espacio="100 GB",
                 dominios="1 gratis", cuentas_correo="50", bases_datos="10",
                 descripcion="Más espacio y aplicaciones para el sitio de tu negocio.",
                 caracteristicas="Espacio web: 100 GB\nIncluye 1 dominio gratis\n" + comunes
                                 + "\nMás de 140 apps\nSiteBuilder con plantillas"),
            dict(nombre="No Límite", tipo=tipos["compartido"], precio_anterior=1548, precio=799, destacado=True,
                 lema="¡Máximo rendimiento para proyectos interactivos y con contenidos dinámicos!",
                 icono="planes/nolimite.webp", espacio="Ilimitado", dominios="1 gratis",
                 cuentas_correo="Ilimitadas", bases_datos="Ilimitadas",
                 descripcion="Sin límites de espacio, correo ni bases de datos para tiendas en línea y portales.",
                 caracteristicas="Espacio web: ilimitado\nIncluye 1 dominio gratis\n" + comunes
                                 + "\nMás de 140 apps\nSiteBuilder con plantillas\nBases de datos MySQL ilimitadas"
                                   "\nCuentas de correo ilimitadas"),
            dict(nombre="Avanzado", tipo=tipos["compartido"], precio_anterior=2988, precio=1039, destacado=True,
                 lema="¡Un plan superior, ideal para desarrolladores!", icono="planes/avanzado.webp",
                 espacio="Ilimitado", dominios="1 gratis", cuentas_correo="Ilimitadas", bases_datos="Ilimitadas",
                 ram="2 GB garantizados",
                 descripcion="Recursos garantizados y soporte especializado para desarrolladores.",
                 caracteristicas="Soporte de expertos en apps\nEspacio web: ilimitado\nIncluye 1 dominio gratis"
                                 "\n2 GB de memoria RAM garantizados\n" + comunes
                                 + "\nMás de 140 apps\nBases de datos MySQL ilimitadas\nCuentas de correo ilimitadas"),
            # Planes extra para que la búsqueda y los dashboards tengan más datos
            dict(nombre="VPS Básico", tipo=tipos["vps"], precio_anterior=4200, precio=3499, icono="menu/servicios.webp",
                 lema="Tu propio servidor virtual", espacio="80 GB SSD", dominios="Ilimitados",
                 cuentas_correo="Ilimitadas", bases_datos="Ilimitadas", ram="2 GB",
                 descripcion="Servidor virtual con acceso root, ideal para aplicaciones en Python, Node o Java.",
                 caracteristicas="Acceso root\n2 núcleos de CPU\nLinux o Windows\nIP dedicada"),
            dict(nombre="VPS Pro", tipo=tipos["vps"], precio=6999, icono="menu/servicios.webp",
                 lema="Más potencia para tus aplicaciones", espacio="160 GB SSD", dominios="Ilimitados",
                 cuentas_correo="Ilimitadas", bases_datos="Ilimitadas", ram="8 GB",
                 descripcion="Más núcleos y memoria para tiendas en línea con mucho tráfico.",
                 caracteristicas="Acceso root\n4 núcleos de CPU\nLinux o Windows\nIP dedicada\nRespaldos diarios"),
            dict(nombre="Dedicado Esencial", tipo=tipos["dedicado"], precio=700, periodo="mes",
                 icono="sitio/footer_servidor.webp", lema="Servidores de alto rendimiento",
                 espacio="1 TB SSD", dominios="Ilimitados", cuentas_correo="Ilimitadas", bases_datos="Ilimitadas",
                 ram="16 GB", descripcion="Un servidor físico completo para aplicaciones avanzadas.",
                 caracteristicas="Intel Xeon de 8 núcleos\nRAID 1\nAdministración incluida\nIP dedicada"),
            dict(nombre="Dedicado Empresarial", tipo=tipos["dedicado"], precio=1499, periodo="mes",
                 icono="sitio/footer_servidor.webp", lema="Para empresas que no pueden detenerse",
                 espacio="2 TB SSD", dominios="Ilimitados", cuentas_correo="Ilimitadas", bases_datos="Ilimitadas",
                 ram="64 GB", descripcion="Máximo rendimiento con georedundancia en dos centros de datos.",
                 caracteristicas="Intel Xeon de 16 núcleos\nRAID 10\nGeoredundancia\nSoporte prioritario"),
            dict(nombre="Reseller Inicial", tipo=tipos["reseller"], precio=1899, icono="menu/resellers.webp",
                 lema="Empieza tu negocio de hosting", espacio="50 GB", dominios="25 cuentas",
                 cuentas_correo="Ilimitadas", bases_datos="Ilimitadas",
                 descripcion="Crea hasta 25 cuentas de hosting con tu propia marca.",
                 caracteristicas="Panel de reseller\nMarca blanca\nFacturación incluida"),
            dict(nombre="Reseller Plus", tipo=tipos["reseller"], precio=3499, icono="menu/resellers.webp",
                 lema="Haz crecer tu cartera de clientes", espacio="150 GB", dominios="100 cuentas",
                 cuentas_correo="Ilimitadas", bases_datos="Ilimitadas",
                 descripcion="Hasta 100 cuentas de hosting con soporte técnico para tus clientes.",
                 caracteristicas="Panel de reseller\nMarca blanca\nFacturación incluida\nSoporte a tus clientes"),
        ]
        for datos in planes:
            db.session.add(Plan(**datos))
        db.session.flush()  # asigna ids sin cerrar la transacción

    def clientes(self):
        if not self._vacia(Cliente):
            return
        clientes = [
            ("Café Coahuila", "Cafetería", "cafe-coahuila"), ("Ferretería El Tornillo", "Ferretería", "ferreteria-el-tornillo"),
            ("Clínica Vida Sana", "Salud", "clinica-vida-sana"), ("Autopartes del Norte", "Automotriz", "autopartes-del-norte"),
            ("Colegio Futuro", "Educación", "colegio-futuro"), ("TecnoSoft MX", "Software", "tecnosoft-mx"),
            ("Panadería La Espiga", "Alimentos", "panaderia-la-espiga"), ("Gimnasio Fuerza", "Deportes", "gimnasio-fuerza"),
        ]
        for nombre, giro, slug in clientes:
            db.session.add(Cliente(nombre=nombre, giro=giro, logo=f"clientes/{slug}.webp",
                                   url=f"https://www.{slug.replace('-', '')}.com.mx"))

    def contratos(self):
        if not self._vacia(Contrato):
            return
        planes = db.session.execute(db.select(Plan)).scalars().all()
        empresas = ["Café Coahuila", "Ferretería El Tornillo", "Clínica Vida Sana", "Autopartes del Norte",
                    "Colegio Futuro", "TecnoSoft MX", "Panadería La Espiga", "Gimnasio Fuerza", "Dulces Saltillo",
                    "Taller Mecánico Ruiz", "Estética Bella", "Consultorio Dental Sonrisa", "Abarrotes Doña Mary",
                    "Floristería Primavera", "Despacho Jurídico Treviño", "Inmobiliaria Casa Linda",
                    "Veterinaria Patitas", "Papelería El Lápiz", "Mueblería Hogar", "Agencia Viajes Sol",
                    "Pizzería Napoli", "Lavandería Burbujas", "Óptica Visión", "Tienda Deportiva Gol",
                    "Academia de Inglés Talk"]
        # Desfases (días respecto a hoy) para que siempre haya vencimientos en el dashboard
        desfases = [-9, -7, -5, -3, -2, -1, 0, 1, 2, 2, 3, 5, 6, 8, 9, 15, 30, 45, 60, 90, 120, 180, 200, 250, 300]
        rnd = random.Random(26)  # semilla fija: siempre los mismos datos
        hoy = date.today()
        for empresa, desfase in zip(empresas, desfases):
            plan = rnd.choice(planes)
            vence = hoy + timedelta(days=desfase)
            slug = empresa.lower().translate(str.maketrans("áéíóúñ", "aeioun")).replace(" ", "")
            db.session.add(Contrato(cliente_nombre=empresa, correo=f"contacto@{slug}.com.mx",
                                    dominio=f"{slug}.com.mx", plan=plan, fecha_vencimiento=vence,
                                    fecha_inicio=vence - timedelta(days=365)))

    def preguntas(self):
        if not self._vacia(PreguntaFrecuente):
            return
        preguntas = [
            ("¿Qué es un hosting?", "Es el espacio en un servidor conectado a internet donde se guardan los archivos "
             "de tu página web para que cualquier persona pueda visitarla las 24 horas."),
            ("¿Qué plan me conviene?", "Si es tu primer sitio, el plan Starter es suficiente. Para un negocio con "
             "tienda o muchos correos, te recomendamos Básico o No Límite. Los desarrolladores prefieren Avanzado o un VPS."),
            ("¿El dominio está incluido?", "Los planes Básico, No Límite y Avanzado incluyen un dominio gratis el "
             "primer año. En Starter puedes registrar tu dominio con nosotros a precio preferencial."),
            ("¿Puedo cambiar de plan después?", "Sí. Puedes subir de plan en cualquier momento y solo pagas la "
             "diferencia proporcional del tiempo restante."),
            ("¿Qué formas de pago aceptan?", "Tarjeta de crédito o débito, transferencia bancaria, depósito en OXXO y PayPal."),
            ("¿Ofrecen soporte técnico?", "Sí, 24 horas los 365 días: chat en línea, teléfono (844) 414 5676 y "
             "correo help@thebesthost.com."),
            ("¿Hacen respaldos de mi sitio?", "Todos los planes incluyen respaldos diarios automáticos que se "
             "guardan durante 7 días."),
            ("¿Tienen garantía de reembolso?", "Sí, si no estás satisfecho te devolvemos tu dinero en los primeros 30 días."),
        ]
        for orden, (pregunta, respuesta) in enumerate(preguntas, start=1):
            db.session.add(PreguntaFrecuente(pregunta=pregunta, respuesta=respuesta, orden=orden))

    def chatbot(self):
        if not self._vacia(RespuestaChatbot):
            return
        respuestas = [
            ("saludo", "hola,buenas,buenos dias,buenas tardes,buenas noches,que tal,hey",
             "¡Hola! 👋 Soy el asistente de The Best Hosting. Pregúntame por planes, precios, dominios o soporte."),
            ("planes", "plan,planes,precio,precios,costo,cuanto,barato,hosting,paquete,oferta",
             "Tenemos planes desde <b>$250 al año</b>: Starter, Básico, No Límite y Avanzado, además de VPS, "
             "servidores dedicados y reseller. <a href='/servicios'>Ver todos los planes</a>"),
            ("dominios", "dominio,dominios,punto com,nombre de mi pagina,registrar",
             "Registramos dominios .com desde $249 y .mx desde $399 al año. Los planes Básico, No Límite y "
             "Avanzado incluyen uno gratis. <a href='/seccion/dominios'>Más información</a>"),
            ("soporte", "soporte,ayuda,problema,error,falla,no funciona,caido,tecnico",
             "Nuestro soporte técnico trabaja 24/7. Llama al <b>(844) 414 5676</b> o escribe a "
             "help@thebesthost.com y un ingeniero te atenderá."),
            ("pagos", "pago,pagar,tarjeta,oxxo,paypal,transferencia bancaria,factura,facturacion",
             "Aceptamos tarjeta de crédito o débito, transferencia, OXXO y PayPal. Todas las compras se facturan."),
            ("correo", "correo,email,e-mail,cuentas de correo,outlook,gmail",
             "Todos los planes incluyen cuentas de correo con tu dominio (por ejemplo ventas@tuempresa.com). "
             "En No Límite y Avanzado son ilimitadas."),
            ("wordpress", "wordpress,joomla,tienda,ecommerce,apps,instalar",
             "Con un clic puedes instalar WordPress, Joomla y más de 140 apps desde tu panel de control."),
            ("garantia", "garantia,reembolso,devolucion,cancelar",
             "Tienes <b>30 días de garantía</b>: si no estás satisfecho te devolvemos tu dinero. "
             "<a href='/seccion/garantias'>Ver póliza</a>"),
            ("servidores", "vps,dedicado,servidor,root,linux,windows",
             "Si necesitas más potencia, tenemos VPS desde $3,499 al año y servidores dedicados desde $700 al mes, "
             "con Linux o Windows. <a href='/servicios?tipo=dedicado'>Ver servidores</a>"),
            ("contacto", "contacto,telefono,llamar,direccion,ubicacion,donde estan,horario",
             "Estamos en 202 Bitters Road, San Antonio, TX. Teléfono (844) 414 5676. "
             "También puedes dejarnos un mensaje en <a href='/contacto'>Contacto</a>."),
            ("despedida", "gracias,adios,bye,hasta luego,es todo",
             "¡Gracias por escribirnos! Si tienes otra duda, aquí estaré las 24 horas. 😊"),
        ]
        for tema, claves, respuesta in respuestas:
            db.session.add(RespuestaChatbot(tema=tema, palabras_clave=claves, respuesta=respuesta))

    def sugerencias(self):
        if not self._vacia(Sugerencia):
            return
        nombres = ["Ana López", "Carlos Ruiz", "María Treviño", "Jorge Garza", "Lucía Flores", "Pedro Sánchez",
                   "Sofía Martínez", "Diego Hernández", "Valeria Castro", "Luis Ramírez", "Fernanda Morales",
                   "Ricardo Ortiz", "Daniela Rojas", "Andrés Vega", "Paola Cruz", "Miguel Torres", "Karla Díaz",
                   "Roberto Mendoza", "Elena Silva", "Héctor Aguilar", "Natalia Ríos", "Óscar Navarro", "Laura Peña"]
        mensajes = ["Me gustaría que tuvieran un plan mensual más económico.",
                    "Excelente servicio, el soporte me ayudó a migrar mi sitio en una hora.",
                    "¿Podrían agregar dominios .org a su catálogo?",
                    "Sugiero un tutorial en video para configurar el correo en el celular.",
                    "El chat en línea me resolvió la duda muy rápido, gracias.",
                    "Quisiera información para revender hosting con mi marca.",
                    "Sería bueno pagar con tarjeta a meses sin intereses."]
        rnd = random.Random(7)
        ahora = datetime.now()
        for i, nombre in enumerate(nombres):
            usuario = nombre.lower().split()[0].translate(str.maketrans("áéíóúñ", "aeioun"))
            db.session.add(Sugerencia(nombre=nombre, correo=f"{usuario}{i}@correo.com",
                                      mensaje=rnd.choice(mensajes), fecha=ahora - timedelta(days=i * 2, hours=i)))
