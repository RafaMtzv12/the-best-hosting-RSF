"""Patrón de diseño Singleton.

Un Singleton garantiza que de una clase exista UNA sola instancia en todo el programa.
Cada vez que se escribe ContadorVisitas() se recibe el mismo objeto, no uno nuevo.

Se usa como "metaclase": la clase que la declara (class X(metaclass=SingletonMeta))
cambia la forma en que se crean sus objetos.
"""
import threading


class SingletonMeta(type):
    _instancias = {}
    _candado = threading.Lock()  # evita que dos peticiones simultáneas creen dos instancias

    def __call__(cls, *args, **kwargs):
        with cls._candado:
            if cls not in cls._instancias:
                cls._instancias[cls] = super().__call__(*args, **kwargs)
        return cls._instancias[cls]
