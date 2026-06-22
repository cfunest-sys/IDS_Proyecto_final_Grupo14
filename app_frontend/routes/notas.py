from flask import Blueprint, render_template, flash, request, session, redirect, url_for, current_app
import requests
from datetime import datetime

notas_blueprint = Blueprint("notas", __name__)

@notas_blueprint.route("/", methods=["GET"])
def ver_notas():
    resumen_promedios = []
    eventos           = []
    alumnos           = []
    periodos          = []
    rol               = ""

    año_actual    = datetime.now().year
    mes_actual    = datetime.now().month
    semestre_default = "1" if mes_actual <= 7 else "2"

    anio_activo     = request.args.get("anio",     str(año_actual))      # ← default: año actual
    semestre_activo = request.args.get("cuatrimestre", semestre_default)      # ← default: cuatrimestre actual

    años_disponibles = list(range(año_actual - 5, año_actual + 3))
    try:
        token        = session.get("token", "")
        auth_headers = {'Authorization': 'Bearer ' + token}

        # 1. Períodos disponibles para el selector de cuatrimestre
        response_periodos = requests.get(
            f"{current_app.config['BACKEND_URL']}/api/notas/periodos",
            headers=auth_headers,
            timeout=5
        )
        if response_periodos.ok:
            periodos = response_periodos.json()

        # 2. Resumen de promedios con filtros de período opcionales
        params_resumen = {}
        if anio_activo:     
            params_resumen["anio"] = int(anio_activo)
        if semestre_activo: 
            params_resumen["cuatrimestre"] = int(semestre_activo)

        response = requests.get(
            f"{current_app.config['BACKEND_URL']}/api/notas/resumen-promedios",
            headers=auth_headers,
            params=params_resumen,
            timeout=5
        )
        if response.ok:
            resumen_promedios = response.json()
        else:
            flash("No se pudieron procesar las actas académicas", "warning")

        # 3. Evaluaciones del usuario para el modal
        if session:
            rol  = session.get("rol", "")
            data = {
                "rol":     rol,
                "user_id": session.get("user_id", "")
            }
            response_eva = requests.post(
                f"{current_app.config['BACKEND_URL']}/api/evaluaciones/usuario",
                headers=auth_headers,
                json=data,
                timeout=5
            )
            if response_eva.ok and response_eva.status_code != 204:
                data_eventos = response_eva.json()
                for evento in data_eventos.get("body", []):
                    eventos.append({
                        "nombre":        evento[1],
                        "id_evaluacion": evento[0]
                    })

        # 4. Lista completa de alumnos para el modal (solo profesores)
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
    año_actual = datetime.now().year
    return render_template(
        "notas.html",
        resumen=resumen_promedios,
        eventos=eventos,
        alumnos=alumnos,
        periodos=periodos,
        anio_activo=anio_activo,
        años_disponibles=años_disponibles,
        semestre_activo=semestre_activo,
        rol=rol
    )


@notas_blueprint.route("/", methods=["POST"])
def cargar_nota():
    try:
        body = {
            "legajo_alumno": request.form.get("alumno"),
            "id_evaluacion": request.form.get("evaluacion"),
            "calificacion":  request.form.get("nota"),
        }
        token = session.get("token", "") if session else ""
        response = requests.post(
            f"{current_app.config['BACKEND_URL']}/api/notas/notas",
            headers={'Authorization': 'Bearer ' + token},
            json=body,
            timeout=5
        )
        if response.ok:
            flash("Nota guardada correctamente", "success")
        else:
            flash(response.json().get("error", "Error al guardar la nota"), "warning")
    except requests.exceptions.RequestException:
        flash("El servidor de datos (Backend) no responde", "danger")

    return redirect(url_for('notas.ver_notas'))
