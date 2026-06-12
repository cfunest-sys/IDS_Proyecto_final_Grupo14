from flask import Blueprint, redirect, render_template, request, flash, current_app, session
import requests

cursos_bp = Blueprint("cursos_bp",__name__)

@cursos_bp.route("/cursos", methods=['GET'])
def ver_cursos():
    if session.get("rol") != "profesor":
        flash("Solo los profesores tienen acceso a esta funcionalidad.", "warning")
        return redirect("/")

    id_curso = request.args.get("id_curso")
    nombre_curso = request.args.get("nombre_curso")
    anio = request.args.get("anio")
    cuatrimestre = request.args.get("cuatrimestre")
    pag = request.args.get("pag", default=1, type=int)

    lista_cursos_todos = []
    lista_cursos = []

    try:
        token = session.get("token") 
        headers = {"Authorization": f"Bearer {token}"} if token else {}

        response_todo = requests.get(f"{current_app.config['BACKEND_URL']}/api/cursos/", headers=headers)
        if response_todo.status_code == 200:
            lista_cursos_todos = response_todo.json()

        params = {"pag": pag}

        if id_curso and str(id_curso).strip():
            params["id_curso"] = int(id_curso)
            
        if nombre_curso and str(nombre_curso).strip():
            params["nombre_curso"] = nombre_curso
            
        if anio and str(anio).strip():
            params["anio"] = int(anio)

        if cuatrimestre and str(cuatrimestre).strip():
            params["cuatrimestre"] = int(cuatrimestre)

        if len(params) > 1: 
            response_filtrada = requests.get(
                f"{current_app.config['BACKEND_URL']}/api/cursos/filtros/",
                params=params,
                headers=headers
            ) 
        else:
            response_filtrada = requests.get(
                f"{current_app.config['BACKEND_URL']}/api/cursos/",
                params={"pag": pag},
                headers=headers
            )

        if response_filtrada.status_code == 200:
            datos_recibidos = response_filtrada.json()
            
            if isinstance(datos_recibidos, dict):
                if "error" in datos_recibidos:
                    lista_cursos = []
                else:
                    lista_cursos = [datos_recibidos]
            else:
                lista_cursos = datos_recibidos
                
    except Exception as e:
        print(f"Error al traer los cursos: {e}")
        flash("No se pudieron cargar los cursos del servidor", "danger")
    
    lista_cursos.sort(key=lambda x: x.get("id_curso", 0))

    return render_template("cursos.html", cursos=lista_cursos, cursos_todos=lista_cursos_todos, pag=pag)


@cursos_bp.route("/cursos/crear", methods=['POST'])
def crear_cursos():
    if session.get("rol") != "profesor":
        flash("Solo los profesores tienen acceso a esta funcionalidad.","warning")
        return redirect("/")
    
    nombre_curso = request.form.get("nombre_curso")
    anio_raw = request.form.get("anio")
    cuatrimestre_raw = request.form.get("cuatrimestre")

    data = {
        "nombre_curso": nombre_curso,
        "anio": int(anio_raw),
        "cuatrimestre": int(cuatrimestre_raw)
    }

    try:
        token = session.get("token") 
        headers = {"Authorization": f"Bearer {token}"} if token else {}

        response = requests.post(
            f"{current_app.config['BACKEND_URL']}/api/cursos/",
            json=data,
            headers=headers
        )
        
        if response.status_code == 201:
            flash("Curso creado correctamente", "success")
        else:
            error_msg = response.json().get("error", "No se pudo crear el curso")
            flash(f"Error: {error_msg}", "danger")

    except Exception as e:
        print(f"Error al conectar con la API: {e}")
        flash("Error interno: No se pudo conectar con el servidor", "danger")

    return redirect("/cursos")

    
@cursos_bp.route("/cursos/eliminar", methods=['POST'])
def eliminar_curso():
    if session.get("rol") != "profesor":
        flash("Solo los profesores tienen acceso a esta funcionalidad.","warning")
        return redirect("/")
    
    id_curso = request.form.get("id_curso")

    try:
        token = session.get("token") 
        headers = {"Authorization": f"Bearer {token}"} if token else {}

        response = requests.delete(
            f"{current_app.config['BACKEND_URL']}/api/cursos/{id_curso}", 
            headers=headers
        )
        
        if response.status_code == 204:
            flash("Curso eliminado correctamente", "success")
        else:
            error_msg = response.json().get("error", "No se pudo eliminar el curso")
            flash(f"Error: {error_msg}", "danger")

    except Exception as e:
        print(f"Error al conectar con la API: {e}")
        flash("Error interno: No se pudo conectar con el servidor", "danger")

    return redirect("/cursos")
