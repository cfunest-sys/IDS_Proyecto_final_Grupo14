from flask import Blueprint, render_template, flash, request, session, redirect, url_for, current_app
import requests

notas_blueprint = Blueprint("notas", __name__)

@notas_blueprint.route("/", methods=["GET"])
def ver_notas():
    resumen_promedios = []
    eventos = []
    try:
        # session["rol"] = "afasd"
        # session["user_id"] = 2
        # data = {
        #     "rol": session["rol"],
        #     "user_id": session["user_id"]
        # }
        token = session.get("token", "")
        response = requests.get(
            f"{current_app.config['BACKEND_URL']}/api/notas/resumen-promedios",
            headers={'Authorization': 'Bearer ' + token},
            timeout=5
        )
        if response.ok:
            resumen_promedios = response.json()
        else:
            flash("No se pudieron procesar las actas académicas", "warning")
        if session:
            # data = {"rol": session.get("rol", ""), "user_id": session.get("user_id", "")}
            data = {"rol": session.get("rol", ""), "user_id": 2}
        response = requests.get(f"{current_app.config['BACKEND_URL']}/api/evaluaciones/usuario", json=data)
        if response.ok and response.status_code != 204:
            json = response.json()
            for evento in json["body"]:
                eventos.append({"nombre": evento[1], "id_evaluacion": evento[0]})
    except requests.exceptions.RequestException:
        flash("El servidor de datos (Backend) no responde", "danger")

    return render_template("notas.html", resumen=resumen_promedios, eventos=eventos)

@notas_blueprint.route("/", methods=["POST"])
def cargar_nota():
    resumen_promedios = []
    try:
        body = {
            "legajo_alumno":request.form.get("alumno"),
            "id_evaluacion": request.form.get("evaluacion"),
            "calificacion": request.form.get("nota"),
            }
        token = ""
        if (session):
            token = session.get("token", "")
        response = requests.post(
            f"{current_app.config['BACKEND_URL']}/api/notas/notas",
            headers={'Authorization': 'Bearer ' + token},
            json=body,
            timeout=5
        )
        if response.ok:
            resumen_promedios = response.json()
        else:
            flash(response.json().get("error"), "warning")
    except requests.exceptions.RequestException:
        flash("El servidor de datos (Backend) no responde", "danger")
    return redirect(url_for('notas.ver_notas'))
    # return render_template("notas.html", resumen=resumen_promedios)
