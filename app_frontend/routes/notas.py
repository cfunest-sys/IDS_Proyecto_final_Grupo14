from flask import Blueprint, render_template, flash, request, session, redirect, url_for, current_app
import requests

notas_blueprint = Blueprint("notas", __name__)

@notas_blueprint.route("/", methods=["GET"])
def ver_notas():
    resumen_promedios = []
    eventos = []
    alumnos = []           #lista de alumnos para el modal
    rol = ""

    try:
        token = session.get("token", "")
        auth_headers = {'Authorization': 'Bearer ' + token}
        response = requests.get(
            f"{current_app.config['BACKEND_URL']}/api/notas/resumen-promedios",
            headers=auth_headers,
            timeout=5
        )
        if response.ok:
            resumen_promedios = response.json()
        else:
            flash("No se pudieron procesar las actas académicas", "warning")

        #Evaluaciones del usuario (ahora POST, con token)
        if session:
            rol = session.get("rol", "")
            data = {
                "rol": rol,
                "user_id": session.get("user_id", "")
            }
            response_eva = requests.post(
                f"{current_app.config['BACKEND_URL']}/api/evaluaciones/usuario",
                headers=auth_headers,              #token incluido
                json=data,
                timeout=5
            )
            if response_eva.ok and response_eva.status_code != 204:
                data_eventos = response_eva.json() #antes "json", pisaba el módulo
                for evento in data_eventos.get("body", []):
                    eventos.append({"nombre": evento[1], "id_evaluacion": evento[0]})

        #Lista completa de alumnos para modal (solo profesores la necesitan)
        if rol == "profesor":
            response_alumnos = requests.get(
                f"{current_app.config['BACKEND_URL']}/api/alumnos",
                headers=auth_headers,
                timeout=5
            )
            if response_alumnos.ok:
                alumnos = response_alumnos.json()
            else:
                flash("No se pudo cargar la lista de alumnos", "warning")

    except requests.exceptions.RequestException:
        flash("El servidor de datos (Backend) no responde", "danger")

    return render_template("notas.html", resumen=resumen_promedios, eventos=eventos, alumnos=alumnos, rol=rol)


@notas_blueprint.route("/", methods=["POST"])
def cargar_nota():
    try:
        body = {
            "legajo_alumno": request.form.get("alumno"),
            "id_evaluacion": request.form.get("evaluacion"),
            "calificacion": request.form.get("nota"),
        }
        token = session.get("token", "") if session else ""
        response = requests.post(
            f"{current_app.config['BACKEND_URL']}/api/notas/notas",
            headers={'Authorization': 'Bearer ' + token},
            json=body,
            timeout=5
        )
        if response.ok:
            flash("Nota guardada correctamente", "success")  # ← flash de éxito que faltaba
        else:
            flash(response.json().get("error", "Error al guardar la nota"), "warning")
    except requests.exceptions.RequestException:
        flash("El servidor de datos (Backend) no responde", "danger")

    return redirect(url_for('notas.ver_notas'))
