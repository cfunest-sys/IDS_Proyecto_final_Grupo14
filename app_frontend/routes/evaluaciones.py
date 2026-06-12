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
    rol          = ""

    try:
        if not session:
            flash("Sesión no iniciada", "warning")
            return render_template("evaluaciones.html", evas=evaluaciones, rol=rol, cursos=[])

        token        = session.get("token", "")
        auth_headers = {'Authorization': 'Bearer ' + token}
        data         = {
            "rol":     session.get("rol", ""),
            "user_id": session.get("user_id", "")
        }
        rol = data["rol"]

        response = requests.post(
            f"{current_app.config['BACKEND_URL']}/api/evaluaciones/usuario",
            headers=auth_headers,
            json=data,
            timeout=5
        )

        if response.status_code == 204:
            pass   #sin evaluaciones
        elif response.ok:
            json_data = response.json()
            for eva in json_data.get("body", []):
                evaluaciones.append({
                    "id":     eva[0],
                    "nombre": eva[1],
                    "tipo":   eva[2],
                    "fecha":  eva[3],
                    "curso":  eva[4]
                })
        else:
            flash("No se pudieron cargar las evaluaciones", "warning")

    except requests.exceptions.RequestException:
        flash("Error de conexión con el servidor", "danger")
        return render_template("evaluaciones.html", evas=evaluaciones, rol=rol, cursos=[])

    #Filtros
    tipo_filtro = request.args.get("tipo")
    fecha_desde = request.args.get("fecha_desde")
    fecha_hasta = request.args.get("fecha_hasta")

    if tipo_filtro:
        evaluaciones = [e for e in evaluaciones if e["tipo"] == tipo_filtro]
    if fecha_desde:
        fecha_desde_dt = datetime.strptime(fecha_desde, "%Y-%m-%d")
        evaluaciones   = [
            e for e in evaluaciones
            if datetime.strptime(e["fecha"], "%Y-%m-%d") >= fecha_desde_dt
        ]
    if fecha_hasta:
        fecha_hasta_dt = datetime.strptime(fecha_hasta, "%Y-%m-%d")
        evaluaciones   = [
            e for e in evaluaciones
            if datetime.strptime(e["fecha"], "%Y-%m-%d") <= fecha_hasta_dt
        ]

    cursos = []
    try:
        resp = requests.get(
            f"{current_app.config['BACKEND_URL']}/api/perfil/",
            headers={"Authorization": f"Bearer {session.get('token', '')}"},
            timeout=5
        )
        if resp.ok:
            data = resp.json()
            cursos = data.get("detalles", {}).get("cursos_asignados", [])
    except requests.exceptions.RequestException:
        pass

    stats = {"total": len(evaluaciones), "parcial": 0, "tp": 0, "parcialito": 0}
    for e in evaluaciones:
        t = e["tipo"]
        if t == "Parcial":
            stats["parcial"] += 1
        elif t == "TP":
            stats["tp"] += 1
        elif t == "Parcialito":
            stats["parcialito"] += 1

    return render_template("evaluaciones.html", evas=evaluaciones, rol=rol, cursos=cursos, stats=stats)


# 2. RUTA DEL CALENDARIO: http://127.0.0.1:8080/evaluaciones/calendario
# Acá se muestra el calendario con las evaluaciones
@evaluaciones_blueprint.route("/calendario", methods=["GET"])
def calendario_evaluaciones():
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
                f"{current_app.config['BACKEND_URL']}/api/evaluaciones/usuario",
                headers=auth_headers,
                json=data,
                timeout=5
            )

            if response.ok and response.status_code != 204:
                json_data = response.json()   # fix: variable renombrada, no pisa el módulo json
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

    # fix: año y mes dinámicos desde la fecha actual, no hardcodeados
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
        if not response.ok:
            err = response.json().get("error", "Error desconocido")
            flash(f"Error al crear evaluación: {err}", "danger")
            return redirect(url_for('evaluaciones.listar_evaluaciones'))
    except requests.exceptions.RequestException:
        flash("Error de conexión con el servidor", "danger")
        return redirect(url_for('evaluaciones.listar_evaluaciones'))
    flash("Evaluación creada con éxito", "success")
    return redirect(url_for('evaluaciones.listar_evaluaciones'))

# 4. RUTA ACTUALIZAR EVALUACION
@evaluaciones_blueprint.route("/actualizar", methods=["POST"])
def actualizar_evaluacion():
    data = {}
    if not session:
        flash("Sesión no iniciada", "warning")
        return redirect(url_for('evaluaciones.listar_evaluaciones'))
    try:
        data["id"] = request.form.get("id")
        data["nombre"] = request.form.get("nombre")
        data["tipo"] = request.form.get("tipo")
        data["fecha"] = request.form.get("fecha")
        data["curso_id"] = request.form.get("curso")
        response = requests.put(
            f"{current_app.config['BACKEND_URL']}/api/evaluaciones/actualizar/",
            json=data,
            timeout=5
        )
        if response.ok:
            flash("Evaluación actualizada con éxito", "success")
        else:
            err = response.json().get("error", "Error desconocido")
            flash(f"Error al actualizar: {err}", "danger")
    except requests.exceptions.RequestException:
        flash("Error de conexión con el servidor", "danger")
    return redirect(url_for('evaluaciones.listar_evaluaciones'))


# 5. RUTA ELIMINAR EVALUACION: http://127.0.0.1:8080/evaluaciones/destruir/<int:id>
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
