from flask import Blueprint, redirect, render_template, request, flash, current_app, session
import requests

equipos_bp = Blueprint("equipos_bp",__name__)

@equipos_bp.route("/equipos", methods=['GET'])
def ver_equipos():
    if session.get("rol") != "profesor":
        flash("Solo los profesores tienen acceso a esta funcionalidad.", "warning")
        return redirect("/")

    id_curso = request.args.get("id_curso")
    id_equipo = request.args.get("id_equipo")
    nombre_equipo = request.args.get("nombre_equipo")
    pag = request.args.get("pag", default=1, type=int)

    params = {"pag": pag}

    if id_curso:
        params["id_curso"] = int(id_curso)
        
    if id_equipo:
        params["id_equipo"] = int(id_equipo)
        
    if nombre_equipo:
        params["nombre_equipo"] = nombre_equipo

    lista_equipos = []
    lista_cursos = []

    try:
        token = session.get("token") 
        headers = {"Authorization": f"Bearer {token}"} if token else {}

        response_todo = requests.get(f"{current_app.config['BACKEND_URL']}/api/equipos", headers=headers)
        if response_todo.status_code == 200:
            equipos_todos = response_todo.json()

            for equipo in equipos_todos:
                if equipo.get("id_curso") not in lista_cursos:
                    lista_cursos.append(equipo.get("id_curso"))

        response_filtrada = requests.get(
            f"{current_app.config['BACKEND_URL']}/api/equipos",
            params=params,
            headers=headers
        ) 

        if response_filtrada.status_code == 200:
            equipos = response_filtrada.json()
            
            for equipo in equipos:
                id_eq = equipo.get("id_equipo")
                response_detalle = requests.get(
                    f"{current_app.config['BACKEND_URL']}/api/equipos/{id_eq}", 
                    headers=headers
                )
                if response_detalle.status_code == 200:
                    lista_equipos.append(response_detalle.json())
                else:
                    equipo["alumnos"] = []
                    lista_equipos.append(equipo)
                
    except Exception as e:
        print(f"Error al traer los equipos: {e}")
        flash("No se pudieron cargar los equipos del servidor", "danger")
    
    lista_cursos.sort()

    return render_template("equipos.html", equipos=lista_equipos, cursos=lista_cursos, pag=pag)


@equipos_bp.route("/equipos/crear", methods=['POST'])
def crear_equipo():
    if session.get("rol") != "profesor":
        flash("Solo los profesores tienen acceso a esta funcionalidad.", "warning")
        return redirect("/")
    
    nombre = request.form.get("nombre_equipo")
    id_curso = request.form.get("id_curso")

    data = {
        "nombre_equipo": nombre,
        "id_curso": id_curso
    }

    try:
        token = session.get("token") 
        headers = {"Authorization": f"Bearer {token}"} if token else {}

        response = requests.post(
            f"{current_app.config['BACKEND_URL']}/api/equipos",
            json=data,
            headers=headers
        )
        
        if response.status_code == 201:
            flash("Equipo creado correctamente", "success")
        else:
            error_msg = response.json().get("error", "No se pudo crear el equipo")
            flash(f"Error: {error_msg}", "danger")

    except Exception as e:
        print(f"Error al conectar con la API: {e}")
        flash("Error interno: No se pudo conectar con el servidor", "danger")

    return redirect("/equipos")


@equipos_bp.route("/equipos/modificar", methods=['POST'])
def modificar_equipo():
    if session.get("rol") != "profesor":
        flash("Solo los profesores tienen acceso a esta funcionalidad.", "warning")
        return redirect("/")
    
    id_equipo = request.form.get("id_equipo")
    nombre = request.form.get("nombre_equipo")
    id_curso = request.form.get("id_curso")

    data = {
        "nombre_equipo": nombre,
        "id_curso": id_curso
    }

    try:
        token = session.get("token") 
        headers = {"Authorization": f"Bearer {token}"} if token else {}

        response = requests.put(
            f"{current_app.config['BACKEND_URL']}/api/equipos/{id_equipo}",
            json=data,
            headers=headers
        )
        
        if response.status_code == 200:
            flash("Equipo actualizado correctamente", "success")
        else:
            error_msg = response.json().get("error", "No se pudo actualizar el equipo")
            flash(f"Error: {error_msg}", "danger")

    except Exception as e:
        print(f"Error al conectar con la API: {e}")
        flash("Error interno: No se pudo conectar con el servidor", "danger")

    return redirect("/equipos")


@equipos_bp.route("/equipos/eliminar", methods=['POST'])
def eliminar_equipo():
    if session.get("rol") != "profesor":
        flash("Solo los profesores tienen acceso a esta funcionalidad.", "warning")
        return redirect("/")
    
    id_equipo = request.form.get("id_equipo")

    try:
        token = session.get("token") 
        headers = {"Authorization": f"Bearer {token}"} if token else {}

        response = requests.delete(
            f"{current_app.config['BACKEND_URL']}/api/equipos/{id_equipo}",
            headers=headers
        )
        
        if response.status_code == 204:
            flash("Equipo eliminado correctamente", "success")
        else:
            error_msg = response.json().get("error", "No se pudo eliminar el equipo")
            flash(f"Error: {error_msg}", "danger")

    except Exception as e:
        print(f"Error al conectar con la API: {e}")
        flash("Error interno: No se pudo conectar con el servidor", "danger")

    return redirect("/equipos")


@equipos_bp.route("/equipos/agregar-alumno", methods=['POST'])
def agregar_alumno_equipo():
    if session.get("rol") != "profesor":
        flash("Solo los profesores tienen acceso a esta funcionalidad.", "warning")
        return redirect("/")
    
    id_equipo = request.form.get("id_equipo")
    legajo_alumno = request.form.get("legajo_alumno")

    data = {
        "id_equipo": int(id_equipo),
        "legajo_alumno": int(legajo_alumno)
    }

    try:
        token = session.get("token") 
        headers = {"Authorization": f"Bearer {token}"} if token else {}

        response = requests.post(
            f"{current_app.config['BACKEND_URL']}/api/equipos/miembros",
            json=data,
            headers=headers
        )
        
        if response.status_code == 201:
            flash("Alumno agregado al equipo correctamente", "success")
        else:
            error_msg = response.json().get("error", "No se pudo asignar el alumno")
            flash(f"Error: {error_msg}", "danger")

    except Exception as e:
        flash("Error al asignar el alumno", "danger")

    return redirect("/equipos")


@equipos_bp.route("/equipos/eliminar-alumno", methods=['POST'])
def eliminar_alumno_equipo():
    if session.get("rol") != "profesor":
        flash("Solo los profesores tienen acceso a esta funcionalidad.", "warning")
        return redirect("/")
    
    id_miembro = request.form.get("id_miembro")

    try:
        token = session.get("token") 
        headers = {"Authorization": f"Bearer {token}"} if token else {}

        response = requests.delete(
            f"{current_app.config['BACKEND_URL']}/api/equipos/miembros/{id_miembro}",
            headers=headers
        )
        
        if response.status_code == 204:
            flash("Alumno eliminado del equipo", "success")
        else:
            error_msg = response.json().get("error", "No se pudo eliminar el alumno")
            flash(f"Error: {error_msg}", "danger")

    except Exception as e:
        flash("Error al eliminar el alumno", "danger")

    return redirect("/equipos")