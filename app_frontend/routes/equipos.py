from flask import Blueprint, redirect, render_template, request, flash, jsonify
import requests

equipos_bp = Blueprint("equipos_bp",__name__)

@equipos_bp.route("/equipos", methods=['GET'])
def ver_equipos():
    id_curso = request.args.get("id_curso")
    id_equipo = request.args.get("id_equipo")
    nombre_equipo = request.args.get("nombre_equipo")

    params = {}

    if id_curso:
        params["id_curso"] = int(id_curso)
        
    if id_equipo:
        params["id_equipo"] = int(id_equipo)
        
    if nombre_equipo:
        params["nombre_equipo"] = nombre_equipo

    lista_equipos = []
    lista_cursos = []

    try:
        response_todo = requests.get("http://127.0.0.1:5001/api/equipos")
        if response_todo.status_code == 200:
            equipos_todos = response_todo.json()

            for equipo in equipos_todos:
                if equipo.get("id_curso") not in lista_cursos:
                    lista_cursos.append(equipo.get("id_curso"))

        response_filtrada = requests.get(
            "http://127.0.0.1:5001/api/equipos",
            params=params
        ) 

        if response_filtrada.status_code == 200:
            lista_equipos = response_filtrada.json()
                
    except Exception as e:
        print(f"Error al traer los equipos: {e}")
        flash("No se pudieron cargar los equipos del servidor", "danger")
    
    lista_cursos.sort()

    return render_template("equipos.html", equipos=lista_equipos, cursos=lista_cursos)


@equipos_bp.route("/equipos/crear", methods=['POST'])
def crear_equipo():
    nombre = request.form.get("nombre_equipo")
    id_curso = request.form.get("id_curso")

    data = {
        "nombre_equipo": nombre,
        "id_curso": id_curso
    }

    try:
        response = requests.post(
            "http://127.0.0.1:5001/api/equipos",
            json=data
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
    id_equipo = request.form.get("id_equipo")
    nombre = request.form.get("nombre_equipo")
    id_curso = request.form.get("id_curso")

    data = {
        "nombre_equipo": nombre,
        "id_curso": id_curso
    }

    try:
        response = requests.put(
            f"http://127.0.0.1:5001/api/equipos/{id_equipo}",
            json=data
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
    id_equipo = request.form.get("id_equipo")

    try:
        response = requests.delete(
            f"http://127.0.0.1:5001/api/equipos/{id_equipo}"
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
    id_equipo = request.form.get("id_equipo")
    legajo_alumno = request.form.get("legajo_alumno")

    data = {
        "id_equipo": int(id_equipo),
        "legajo_alumno": int(legajo_alumno)
    }

    try:
        response = requests.post(
            "http://127.0.0.1:5001/api/equipos/miembros",
            json=data
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
    id_miembro = request.form.get("id_miembro")

    try:
        response = requests.delete(
            f"http://127.0.0.1:5001/api/equipos/miembros/{id_miembro}"
        )
        
        if response.status_code == 204:
            flash("Alumno eliminado del equipo", "success")
        else:
            error_msg = response.json().get("error", "No se pudo eliminar el alumno")
            flash(f"Error: {error_msg}", "danger")

    except Exception as e:
        flash("Error al eliminar el alumno", "danger")

    return redirect("/equipos")


#Ruta auxiliar para los datos que necesita js
@equipos_bp.route("/equipos/datos/<id_equipo>", methods=['GET'])
def obtener_datos_equipos(id_equipo):
    try:
        response = requests.get(f"http://127.0.0.1:5001/api/equipos/{id_equipo}")
        
        return jsonify(response.json()), response.status_code
    except Exception as e:
        print(f"Error en la ruta auxiliar: {e}")
        return jsonify({"error": "No se pudo conectar con el servidor"}), 500