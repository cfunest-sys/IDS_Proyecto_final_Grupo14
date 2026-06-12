from datetime import datetime
from flask import Blueprint, redirect, render_template, request, flash, session, current_app, url_for
import requests
import calendar

evaluaciones_blueprint = Blueprint("evaluaciones", __name__)


# 1. RUTA PRINCIPAL: http://127.0.0.1:8080/evaluaciones
# Acá se muestra el listado/gestión de evaluaciones
@evaluaciones_blueprint.route("/", methods=["GET"])
def listar_evaluaciones():
    evaluaciones = []
    data = {}
    try:
        if session:
            data = {"rol": session.get("rol", ""), "user_id": session.get("user_id", "")}
            # data = {"rol": "profesor", "user_id": 2}  #--para probar--
            # data = {"rol": "alumno", "user_id": 2}  #--para probar--
        response = requests.post(f"{current_app.config['BACKEND_URL']}/api/evaluaciones/usuario", json=data)
    except requests.exceptions.RequestException:
        flash("Error de conexión con el servidor", "danger")
        return render_template("evaluaciones.html", evaluaciones=evaluaciones)
    if response.status_code != 204:
        json_data = response.json()
        for eva in json_data["body"]:
            evaluaciones.append({"id": eva[0], "nombre": eva[1], "tipo": eva[2], "fecha": eva[3], "curso": eva[4]})
    # --- FILTROS ---
    tipo_filtro = request.args.get("tipo")
    fecha_desde = request.args.get("fecha_desde")
    fecha_hasta = request.args.get("fecha_hasta")
    if tipo_filtro:
        evaluaciones = [e for e in evaluaciones if e["tipo"] == tipo_filtro]
    if fecha_desde:
        evaluaciones = [e for e in evaluaciones if datetime.strptime(e["fecha"], "%Y-%m-%d") >= datetime.strptime(fecha_desde, "%Y-%m-%d")]
    if fecha_hasta:
        evaluaciones = [e for e in evaluaciones if datetime.strptime(e["fecha"], "%Y-%m-%d") <= datetime.strptime(fecha_hasta, "%Y-%m-%d")]
    rol = data.get("rol", "")
    return render_template("evaluaciones.html", evaluaciones=evaluaciones, rol=rol)


# 2. RUTA DEL CALENDARIO: http://127.0.0.1:8080/evaluaciones/calendario
# Acá se muestra el calendario con las evaluaciones
@evaluaciones_blueprint.route("/calendario", methods=["GET"])
def calendario_evaluaciones():
    # eventos = [{"nombre":"tp1", "tipo":"TP", "fecha": "2026-05-21", "curso":1},]

    # activar esto para probar el calendario sin iniciar sesion
    # session["rol"] = "profesor"
    # session["user_id"] = 2
    if session:
        data = {"rol": session.get("rol", ""), "user_id": session.get("user_id", "")}
    else:
        data = {}
    eventos = []
    try:
        response = requests.post(f"{current_app.config['BACKEND_URL']}/api/evaluaciones/usuario", json=data)
    except requests.exceptions.RequestException:
        flash("Error de conexión con el servidor", "danger")
        return render_template("calendario.html", mes_actual=5, año_actual=2026, dias=(31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31), mes_nombre=("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"), eventos=[])
    if response.ok and response.status_code != 204:
        json = response.json()
        if json.get("error", "") == "":
            for evento in json["body"]:
                d = datetime.strptime(evento[3], "%Y-%m-%d")
                eventos.append(
                    {"nombre": evento[1], "tipo": evento[2], "fecha": d.strftime("%Y-%m-%d"), "curso": evento[4]}
                )
    mes_nombre = (
        "enero",
        "febrero",
        "marzo",
        "abril",
        "mayo",
        "junio",
        "julio",
        "agosto",
        "septiembre",
        "octubre",
        "noviembre",
        "diciembre",
    )
    año_actual = 2026
    mes_actual = 5

    dias = tuple(calendar.monthrange(año_actual, mes)[1] for mes in range(1, 13))

    # return render_template("prueba.html", eventos=eventos)

    return render_template(
        "calendario.html",
        mes_actual=mes_actual,
        año_actual=año_actual,
        dias=dias,
        mes_nombre=mes_nombre,
        eventos=eventos,
    )

# 3. RUTA CREAR EVALUACION: http://127.0.0.1:8080/evaluaciones/crear
# Acá se crean evaluaciones
@evaluaciones_blueprint.route("/", methods=["POST"])
def crear_evaluacion():
    data = {}
    try:
        if session:
            data = {"rol": session.get("rol", ""), "user_id": session.get("user_id", "")}
            # data = {"rol": "profesor", "user_id": 2}  #--para probar--
            # data = {"rol": "alumno", "user_id": 2}  #--para probar--
        data["nombre"] = request.form.get("nombre")
        data["tipo"] = request.form.get("tipo")
        data["fecha"] = request.form.get("fecha")
        data["curso_id"] = request.form.get("curso")
        response = requests.post(f"{current_app.config['BACKEND_URL']}/api/evaluaciones/crear", json=data)
    except requests.exceptions.RequestException:
        flash("Error de conexión con el servidor", "danger")
        return redirect(url_for('evaluaciones.listar_evaluaciones'))
    return redirect(url_for('evaluaciones.listar_evaluaciones'))

# 4. RUTA ELIMINAR EVALUACION: http://127.0.0.1:8080/evaluaciones/destruir/<int:id>
# Acá se crean evaluaciones
@evaluaciones_blueprint.route("/eliminar", methods=["POST","DELETE"])
def eliminar_evaluacion():
    data = {}
    if (request.form.get("method") != "delete"):
        flash("Error, intento de conexión indebido", "danger")
        return redirect(url_for('evaluaciones.listar_evaluaciones'))
    try:
        if session:
            data = {"rol": session.get("rol", ""), "user_id": session.get("user_id", "")}
            # data = {"rol": "profesor", "user_id": 2}  #--para probar--
            # data = {"rol": "alumno", "user_id": 2}  #--para probar--
        data["id"] = request.form.get("id_evaluacion", "")
        response = requests.delete(f"{current_app.config['BACKEND_URL']}/api/evaluaciones/destruir/{str(data['id'])}")
        if response.ok:
            if response.json().get("body", "") != "":
                json = response.json().get("body", "")
                if json.get("estado") == True:
                    flash("Eliminado con éxito","success")
                else:
                    flash("No se pudo eliminar", "danger")
    except requests.exceptions.RequestException:
        flash("Error de conexión con el servidor", "danger")
        return redirect(url_for('evaluaciones.listar_evaluaciones'))
    return redirect(url_for('evaluaciones.listar_evaluaciones'))
