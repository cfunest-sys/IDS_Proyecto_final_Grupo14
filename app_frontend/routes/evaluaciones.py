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
    rol = ""
    try:
        if not session:
            flash("Sesión no iniciada", "warning")
            return render_template("evaluaciones.html", evas=evaluaciones, rol=rol, cursos=[], stats={})

        token = session.get("token", "")
        auth_headers = {"Authorization": "Bearer " + token}
        data = {"rol": session.get("rol", ""), "user_id": session.get("user_id", "")}
        rol = data["rol"]

        response = requests.post(
            f"{current_app.config['BACKEND_URL']}/api/evaluaciones/usuario", headers=auth_headers, json=data, timeout=5
        )

        if response.status_code == 204:
            pass  # sin evaluaciones
        elif response.ok:
            json_data = response.json()
            for eva in json_data.get("body", []):
                # Ahora leemos de forma segura como diccionario mapeado desde el backend
                evaluaciones.append({
                    "id": eva.get("id_evaluacion"), 
                    "nombre": eva.get("nombre"), 
                    "tipo": eva.get("tipo"), 
                    "fecha": eva.get("fecha"), 
                    "id_curso": eva.get("id_curso"),
                    "curso_nombre": eva.get("curso_nombre", "N/A"),
                    "cuatrimestre": eva.get("cuatrimestre"), # <-- AGREGADO
                    "anio": eva.get("anio")                  # <-- AGREGADO
                })
        else:
            flash("No se pudieron cargar las evaluaciones", "warning")

    except requests.exceptions.RequestException:
        flash("Error de conexión con el servidor", "danger")
        return render_template("evaluaciones.html", evas=evaluaciones, rol=rol, cursos=[], stats={})

    # 1. Capturar los filtros de la URL (lo que manda el form HTML)
    tipo_filtro = request.args.get("tipo")
    cuatrimestre_filtro = request.args.get("cuatrimestre")
    anio_filtro = request.args.get("anio")
    curso_filtro = request.args.get("curso") # ¡Acá capturamos el curso!

    # 2. Aplicar los filtros a la lista 'evaluaciones'
    if tipo_filtro:
        evaluaciones = [e for e in evaluaciones if e.get("tipo") == tipo_filtro]

    if cuatrimestre_filtro:
        evaluaciones = [e for e in evaluaciones if str(e.get("cuatrimestre")) == str(cuatrimestre_filtro)]

    if anio_filtro:
        evaluaciones = [e for e in evaluaciones if str(e.get("anio")) == str(anio_filtro)]
        
    if curso_filtro:
        evaluaciones = [e for e in evaluaciones if str(e.get("id_curso")) == str(curso_filtro)]

    # Obtención de cursos para los selects de los modales
    cursos = []
    try:
        if rol == "profesor":
            # Consumimos el nuevo endpoint optimizado para profesores
            resp = requests.post(
                f"{current_app.config['BACKEND_URL']}/api/evaluaciones/cursos",
                headers={"Authorization": f"Bearer {session.get('token', '')}"},
                json={"rol": rol, "user_id": session.get("user_id", "")},
                timeout=5,
            )
            if resp.ok:
                cursos = resp.json().get("body", [])
        else:
            # Alumnos siguen usando el fallback de su perfil asignado
            resp = requests.get(
                f"{current_app.config['BACKEND_URL']}/api/perfil/",
                headers={"Authorization": f"Bearer {session.get('token', '')}"},
                timeout=5,
            )
            if resp.ok:
                data = resp.json()
                detalles = data.get("detalles") or {}
                cursos = detalles.get("cursos_asignados", [])
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

    return render_template(
        "evaluaciones.html", 
        evas=evaluaciones, 
        rol=rol, 
        cursos=cursos, 
        stats=stats,
        filtro_tipo=tipo_filtro,
        filtro_cuatrimestre=cuatrimestre_filtro,
        filtro_anio=anio_filtro,
        filtro_curso=curso_filtro
    )

# 2. RUTA DEL CALENDARIO: http://127.0.0.1:8080/evaluaciones/calendario
# Redirige a la ruta principal /calendario en app.py
@evaluaciones_blueprint.route("/calendario", methods=["GET"])
def calendario_evaluaciones():
    return redirect(url_for("inicio.mostrar_calendario"))

# 3. RUTA CREAR EVALUACION: http://127.0.0.1:8080/evaluaciones/
@evaluaciones_blueprint.route("/", methods=["POST"])
def crear_evaluacion():
    if not session.get("user_id"):
        flash("Sesión no iniciada", "warning")
        return redirect("/")
    try:
        token = session.get("token", "")
        auth_headers = {"Authorization": "Bearer " + token}
        data = {
            "rol":      session.get("rol", ""),
            "user_id":  session.get("user_id", ""),
            "nombre":   request.form.get("nombre"),
            "tipo":     request.form.get("tipo"),
            "fecha":    request.form.get("fecha"),
            "curso_id": request.form.get("curso"),
        }
        response = requests.post(
            f"{current_app.config['BACKEND_URL']}/api/evaluaciones/crear",
            json=data,
            headers=auth_headers,
            timeout=5
        )
        if not response.ok:
            err = response.json().get("error", "Error desconocido")
            flash(f"Error al crear evaluación: {err}", "danger")
            return redirect(url_for("evaluaciones.listar_evaluaciones"))
    except requests.exceptions.RequestException:
        flash("Error de conexión con el servidor", "danger")
        return redirect(url_for("evaluaciones.listar_evaluaciones"))
    flash("Evaluación creada con éxito", "success")
    return redirect(url_for("evaluaciones.listar_evaluaciones"))

# 4. RUTA ACTUALIZAR EVALUACION
@evaluaciones_blueprint.route("/actualizar", methods=["POST"])
def actualizar_evaluacion():
    if not session.get("user_id"):
        flash("Sesión no iniciada", "warning")
        return redirect("/")
    try:
        token = session.get("token", "")
        auth_headers = {"Authorization": "Bearer " + token}
        data = {
            "id":       request.form.get("id"),
            "nombre":   request.form.get("nombre"),
            "tipo":     request.form.get("tipo"),
            "fecha":    request.form.get("fecha"),
            "curso_id": request.form.get("curso"),
        }
        response = requests.put(
            f"{current_app.config['BACKEND_URL']}/api/evaluaciones/actualizar/",
            json=data,
            headers=auth_headers,
            timeout=5
        )
        if response.ok:
            flash("Evaluación actualizada con éxito", "success")
        else:
            err = response.json().get("error", "Error desconocido")
            flash(f"Error al actualizar: {err}", "danger")
    except requests.exceptions.RequestException:
        flash("Error de conexión con el servidor", "danger")
    return redirect(url_for("evaluaciones.listar_evaluaciones"))


# 5. RUTA ELIMINAR EVALUACION
@evaluaciones_blueprint.route("/eliminar", methods=["POST"])
def eliminar_evaluacion():
    if not session.get("user_id"):
        flash("Sesión no iniciada", "warning")
        return redirect("/")
    if request.form.get("method") != "delete":
        flash("Error, intento de conexión indebido", "danger")
        return redirect(url_for("evaluaciones.listar_evaluaciones"))
    try:
        token = session.get("token", "")
        auth_headers = {"Authorization": "Bearer " + token}
        id_evaluacion = request.form.get("id_evaluacion", "")
        response = requests.delete(
            f"{current_app.config['BACKEND_URL']}/api/evaluaciones/destruir/{id_evaluacion}",
            headers=auth_headers,
            timeout=5
        )
        if response.ok:
            body = response.json().get("body", {})
            if body.get("estado") == True:
                flash("Eliminado con éxito", "success")
            else:
                flash("No se pudo eliminar", "danger")
        else:
            flash("Error al eliminar la evaluación", "danger")
    except requests.exceptions.RequestException:
        flash("Error de conexión con el servidor", "danger")
    return redirect(url_for("evaluaciones.listar_evaluaciones"))
