from datetime import datetime
import calendar
from flask import Flask, render_template, session, flash
from routes.routes import inicio
from routes.equipos import equipos_bp
from routes.evaluaciones import evaluaciones_blueprint
from routes.notas import notas_blueprint
from routes.dashboard_profesor import dashboard_bp
from routes.perfil import perfil_bp
from routes.cursos import cursos_bp
from routes.asistencia import asistencia_bp
from routes.dashboard_alumno import dashboard_alumno_bp
import os
import requests

PORT = 8080

app = Flask(__name__)
app.secret_key = "six_seven"

app.config["BACKEND_URL"] = os.getenv("BACKEND_URL", "http://127.0.0.1:5001")
app.config["PUBLIC_URL"] = os.getenv("PUBLIC_URL", "national-unlit-unseated.ngrok-free.dev")

app.register_blueprint(inicio)
app.register_blueprint(evaluaciones_blueprint, url_prefix="/evaluaciones")
app.register_blueprint(notas_blueprint, url_prefix="/notas")
app.register_blueprint(dashboard_bp)
app.register_blueprint(equipos_bp)
app.register_blueprint(perfil_bp)
app.register_blueprint(cursos_bp)
app.register_blueprint(asistencia_bp)



@app.route("/alumnos")
def mostrar_alumnos():
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
    eventos = []
    rol = ""

    try:
        if not session:
            flash("Sesión no iniciada", "warning")
        else:
            token = session.get("token", "")
            auth_headers = {'Authorization': 'Bearer ' + token}
            data = {
                "rol": session.get("rol", ""),
                "user_id": session.get("user_id", "")
            }
            rol = data["rol"]

            response = requests.post(
                f"{app.config['BACKEND_URL']}/api/evaluaciones/usuario",
                headers=auth_headers,
                json=data,
                timeout=5
            )

            if response.ok and response.status_code != 204:
                json_data = response.json()
                if not json_data.get("error"):
                    for evento in json_data.get("body", []):
                        d = datetime.strptime(evento[3], "%Y-%m-%d")
                        eventos.append({
                            "nombre": evento[1],
                            "tipo": evento[2],
                            "fecha": d.strftime("%Y-%m-%d"),
                            "curso": evento[4]
                        })

    except requests.exceptions.RequestException:
        flash("Error de conexión con el servidor", "danger")

    hoy = datetime.now()
    año_actual = hoy.year
    mes_actual = hoy.month

    mes_nombre = (
        "enero", "febrero", "marzo", "abril",
        "mayo", "junio", "julio", "agosto",
        "septiembre", "octubre", "noviembre", "diciembre"
    )

    dias = tuple(calendar.monthrange(año_actual, mes)[1] for mes in range(1, 13))

    return render_template(
        "calendario.html",
        mes_actual=mes_actual,
        año_actual=año_actual,
        dias=dias,
        mes_nombre=mes_nombre,
        eventos=eventos,
        rol=rol
    )

if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() in ("true", "1", "t")
    app.run(debug=debug_mode, host="0.0.0.0", port=PORT)
