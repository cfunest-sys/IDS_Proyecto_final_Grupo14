from flask import Blueprint, render_template, flash
import requests

notas_blueprint = Blueprint("notas_blueprint", __name__)

BACKEND_URL = "http://127.0.0.1:5001/api/notas"

@notas_blueprint.route("/", methods=["GET"])
def ver_notas():
    resumen_promedios = []
    try:
        # session["rol"] = "afasd"
        # session["user_id"] = 2
        # data = {
        #     "rol": session["rol"],
        #     "user_id": session["user_id"]
        # }
        response = requests.get(f"{BACKEND_URL}/resumen-promedios", timeout=5)
        if response.ok:
            resumen_promedios = response.json()
        else:
            flash("No se pudieron procesar las actas académicas", "warning")
    except requests.exceptions.RequestException:
        flash("El servidor de datos (Backend) no responde", "danger")

    return render_template("notas.html", resumen=resumen_promedios)

@notas_blueprint.route("/", methods=["POST"])
def cargar_nota():
    resumen_promedios = []
    try:
        body = {
            "legajo_alumno":request.args.get("alumno"),
            "id_evaluacion": request.args.get("evaluacion"),
            "calificacion": request.args.get("nota"),
            }
        response = requests.post(f"{BACKEND_URL}/notas", json=body, timeout=5)
        if response.ok:
            resumen_promedios = response.json()
        else:
            flash("No se pudieron procesar las actas académicas", "warning")
    except requests.exceptions.RequestException:
        flash("El servidor de datos (Backend) no responde", "danger")

    return render_template("notas.html", resumen=resumen_promedios)
