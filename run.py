"""Punto de entrada: arranca el servidor de desarrollo de Flask."""
from app import Aplicacion

app = Aplicacion().construir()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=app.config["DEBUG"])
