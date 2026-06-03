from flask import Flask, render_template
from routes.routes import inicio
from routes.evaluaciones import evaluaciones_blueprint
from routes.notas import notas_blueprint
from routes.dashboard_profesor import dashboard_bp

PORT = 8080

app = Flask(__name__)
app.secret_key = "six_seven"

app.register_blueprint(inicio)
app.register_blueprint(evaluaciones_blueprint, url_prefix='/evaluaciones')
app.register_blueprint(notas_blueprint, url_prefix='/notas')
app.register_blueprint(dashboard_bp)

@app.route("/perfil/profesor") #Temporal para testeo
def perfil_profesor():
    return render_template("perfil_profesor.html")

@app.route("/perfil/alumno") #Temporal para testeo
def perfil_alumno():
    return render_template("perfil_alumno.html")

# Solamente para testear
@app.route("/alumnos")
def mostrar_alumnos():
    alumnos = [
        {"nombre":"pepe", "legajo":112533, "estado": "activo"},
        {"nombre":"maria", "legajo":114529, "estado": "activo"},
        {"nombre":"pedro", "legajo":111572, "estado": "inactivo"},
        {"nombre":"laura", "legajo":115343, "estado": "activo"},
        {"nombre":"juan", "legajo":113323, "estado": "inactivo"}
    ]
    return render_template("alumnos.html", alumnos=alumnos)

import os

if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() in ("true", "1", "t")
    app.run(debug=debug_mode, port=PORT)
