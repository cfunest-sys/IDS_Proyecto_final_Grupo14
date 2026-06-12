from flask import Flask, render_template
from routes.routes import inicio
from routes.equipos import equipos_bp
from routes.evaluaciones import evaluaciones_blueprint
from routes.notas import notas_blueprint
from routes.dashboard_profesor import dashboard_bp
from routes.perfil import perfil_bp
from routes.cursos import cursos_bp
import os

PORT = 8080

app = Flask(__name__)
app.secret_key = "six_seven"

app.config["BACKEND_URL"] = os.getenv("BACKEND_URL", "http://127.0.0.1:5001")

app.register_blueprint(inicio)
app.register_blueprint(evaluaciones_blueprint, url_prefix="/evaluaciones")
app.register_blueprint(notas_blueprint, url_prefix="/notas")
app.register_blueprint(dashboard_bp)
app.register_blueprint(equipos_bp)
app.register_blueprint(perfil_bp)
app.register_blueprint(cursos_bp)


@app.route("/alumnos")
def mostrar_alumnos():
    import requests

    try:
        resp = requests.get(f"{app.config['BACKEND_URL']}/api/alumnos/", timeout=5)
        if resp.ok:
            alumnos = resp.json()
        else:
            alumnos = []
    except Exception:
        alumnos = []
    return render_template("alumnos.html", alumnos=alumnos)


@app.route("/calendario")
def mostrar_calendario():
    eventos = (
        {"nombre": "tp1", "tipo": "TP", "dia": "21", "curso": 1},
        {"nombre": "Primer Parcial Teórico-Práctico", "tipo": "parcial", "dia": "20", "curso": 2},
        {"nombre": "Trabajo Práctico Integrador Final", "tipo": "TP", "dia": "1", "curso": 1},
        {"nombre": "Control de Lectura - Parcialito 1", "tipo": "parcialito", "dia": "13", "curso": 1},
    )
    mes = "febrero"
    dias = 29
    año = 2026
    bisiesto = False
    return render_template("calendario.html", mes=mes, dias=dias, año=año, bisiesto=bisiesto, eventos=eventos)

if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() in ("true", "1", "t")
    app.run(debug=debug_mode, host="0.0.0.0", port=PORT)
