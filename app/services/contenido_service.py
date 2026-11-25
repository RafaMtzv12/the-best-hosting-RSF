"""Contenido de las páginas informativas del menú lateral (texto fijo, no cambia seguido)."""
from .errores import ErrorNegocio


class Seccion:
    def __init__(self, clave, titulo, icono, parrafos, puntos=None, enlace=None):
        self.clave = clave
        self.titulo = titulo
        self.icono = icono
        self.parrafos = parrafos
        self.puntos = puntos or []
        self.enlace = enlace  # (texto, url) botón al final de la página


class ContenidoService:
    SECCIONES = [
        Seccion("garantias", "Póliza de garantías", "menu/garantia.webp", [
            "En The Best Hosting respaldamos cada plan con garantías por escrito.",
            "Si no estás satisfecho durante los primeros 30 días, te devolvemos tu dinero sin preguntas.",
        ], ["99.9% de tiempo en línea garantizado", "30 días de garantía de reembolso",
            "Respaldos diarios automáticos", "Certificado SSL gratis en todos los planes"]),
        Seccion("por-que-nosotros", "¿Por qué nosotros?", "menu/porque.webp", [
            "Más de 10 años ofreciendo hospedaje web a empresas y emprendedores de México.",
            "Nuestra georedundancia guarda tu sitio en dos centros de datos independientes: "
            "si uno falla, el otro sigue funcionando.",
        ], ["Soporte en español 24/7", "Servidores Linux y Windows", "Precios sin sorpresas",
            "Migración gratuita de tu sitio actual"], ("Ver planes", "/servicios")),
        Seccion("centro-de-ayuda", "Centro de ayuda", "menu/ayuda.webp", [
            "¿Tienes una duda? Nuestro asistente virtual responde las 24 horas, los 365 días del año.",
            "Si prefieres hablar con una persona, llámanos al (844) 414 5676 o escríbenos a help@thebesthost.com.",
        ], ["Chat de ayuda en línea 24/7", "Preguntas frecuentes", "Soporte por teléfono y correo"],
            ("Ver preguntas frecuentes", "/preguntas-frecuentes")),
        Seccion("dominios", "Dominios", "menu/dominios.webp", [
            "Registra el nombre de tu empresa en internet. Todos nuestros planes, excepto Starter, "
            "incluyen un dominio gratis el primer año.",
        ], [".com desde $249 al año", ".mx desde $399 al año", ".com.mx desde $299 al año",
            "Transferencia de dominios sin costo"], ("Contratar un plan con dominio", "/servicios")),
        Seccion("tecnologia", "Tecnología", "menu/tecnologia.webp", [
            "Trabajamos con las mejores tecnologías del mercado: servidores Cisco, bases de datos MySQL, "
            "SQL Server y Oracle, y soporte para Java, WordPress y Joomla.",
        ], ["Discos SSD NVMe", "Panel de control en español", "Instalador de más de 140 apps",
            "Firewall y antivirus en el servidor"]),
        Seccion("terminos", "Términos y condiciones", "menu/porque.webp", [
            "El uso de los servicios de The Best Hosting implica la aceptación de estos términos. "
            "Los planes se pagan por adelantado y se renuevan al término del periodo contratado.",
            "Está prohibido alojar contenido ilegal, spam o software malicioso.",
        ]),
        Seccion("privacidad", "Políticas de privacidad", "menu/garantia.webp", [
            "Tus datos personales se usan únicamente para prestar el servicio contratado y nunca se venden a terceros.",
            "Puedes solicitar la corrección o eliminación de tus datos escribiendo a help@thebesthost.com.",
        ]),
        Seccion("reembolso", "Políticas de reembolso", "menu/garantia.webp", [
            "Si cancelas dentro de los primeros 30 días te devolvemos el 100% del pago del plan de hosting.",
            "Los dominios registrados no son reembolsables.",
        ]),
    ]

    def obtener(self, clave):
        for seccion in self.SECCIONES:
            if seccion.clave == clave:
                return seccion
        raise ErrorNegocio("La página no existe.", 404)
