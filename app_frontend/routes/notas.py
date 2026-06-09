from flask import Blueprint, render_template, flash, request, session, redirect, url_for
import requests

notas_blueprint = Blueprint("notas", __name__)

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
        token = session.get("token", "")
        response = requests.get(f"{BACKEND_URL}/resumen-promedios", 
            headers={'Authorization':'Bearer '+token}, timeout=5)
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
            "legajo_alumno":request.form.get("alumno"),
            "id_evaluacion": request.form.get("evaluacion"),
            "calificacion": request.form.get("nota"),
            }
        token = session.get("token", "")
        response = requests.post(f"{BACKEND_URL}/notas", 
        headers={'Authorization':'Bearer '+token}, json=body,timeout=5)
        if response.ok:
            resumen_promedios = response.json()
        else:
            flash(response.json().get("error"), "warning")
    except requests.exceptions.RequestException:
        flash("El servidor de datos (Backend) no responde", "danger")
    return redirect(url_for('notas.ver_notas'))
    # return render_template("notas.html", resumen=resumen_promedios)
