from flask import Blueprint, render_template, flash, request, session, redirect, url_for, current_app
import requests
from datetime import datetime

alumnos_bp = Blueprint("alumnos", __name__)

@alumnos_bp.route("/alumnos", methods=["GET"])
def mostrar_alumnos(): 
    try:
        año_actual    = datetime.now().year
        años_disponibles = list(range(año_actual - 5, año_actual + 3))

        token = session.get("token", "")
        auth_headers = {'Authorization': 'Bearer ' + token}

        anio = request.args.get("anio")
        cuatrimestre = request.args.get("cuatrimestre")

        params = {}
        if anio:
        	params["anio"] = anio
        if cuatrimestre:
        	params["cuatrimestre"] = cuatrimestre

        resp = requests.get(f"{current_app.config['BACKEND_URL']}/api/alumnos/", 
            timeout=5, headers=auth_headers, params=params)
        if resp.ok:
            alumnos = resp.json()
        else:
            alumnos = []
    except Exception:
        alumnos = []
    return render_template("alumnos.html", alumnos=alumnos, 
    	años_disponibles=años_disponibles, cuatrimestre=cuatrimestre, 
    	anio=anio)

@alumnos_bp.route("/alumnos/desactivar", methods=["POST"])
def desactivar_alumno():
    try:
        legajo = request.form.get("legajo", "")
        estado = request.form.get("estado", "")
        data = {"legajo":legajo, "estado":estado}
        token = session.get("token", "")
        auth_headers = {'Authorization': 'Bearer ' + token}
        resp = requests.put(f"{app.config['BACKEND_URL']}/api/alumnos/actualizar/desactivar", 
            timeout=5, json=data, headers=auth_headers)
    except requests.exceptions.RequestException:
        flash("Error de conexión con el servidor", "danger")

    if resp.ok:
        flash("Estado cambiado con éxito", "success")
    return redirect("/alumnos") 