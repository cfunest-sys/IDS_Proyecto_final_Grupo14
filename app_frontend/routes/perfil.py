# from flask import Blueprint, flash, render_template, session, redirect
# import requests

# perfil_bp = Blueprint("perfil", __name__)


# @perfil_bp.route("/perfil/alumno")
# def perfil_alumno():
#     if session.get("rol") != "alumno":
#         flash("Solo los alumnos tienen acceso a esta funcionalidad.", "warning")
#         return redirect("/")

#     datos_perfil = {}
#     try:
#         response = requests.get(
#             "http://127.0.0.1:5001/perfil",
#             timeout=5
#         )
#         if response.ok:
#             datos_perfil = response.json()
#     except Exception:
#         pass

#     return render_template(
#         "perfil_alumno.html",
#         usuario=datos_perfil,
#         detalle=datos_perfil.get("detalles", {})
#     )


# @perfil_bp.route("/perfil/profesor")
# def perfil_profesor():
#     if session.get("rol") != "profesor":
#         flash("Solo los profesores tienen acceso a esta funcionalidad.", "warning")
#         return redirect("/")

#     datos_perfil = {}
#     try:
#         response = requests.get(
#             "http://127.0.0.1:5001/perfil",
#             timeout=5
#         )
#         if response.ok:
#             datos_perfil = response.json()
#     except Exception:
#         pass

#     return render_template(
#         "perfil_profesor.html",
#         usuario=datos_perfil,
#         detalle=datos_perfil.get("detalles", {})
#     )

# from flask import Blueprint, flash, render_template, session, redirect
# import requests

# perfil_bp = Blueprint("perfil", __name__)


# @perfil_bp.route("/perfil/alumno")
# def perfil_alumno():

#     # Informacion de prueba para testeo
#     datos_perfil = {
#         "id": 3,
#         "email": "jperez@gmail.com",
#         "rol": "alumno",
#         "detalles": {
#             "legajo": 115598,
#             "nombre": "Juan",
#             "apellido": "Pérez",
#             "dni": "40123456",
#             "curso": "75.40",
#             "anio": 2026,
#             "cuatrimestre": 1,
#             "estado": "activo",
#             "evaluaciones": [
#                 {
#                     "evaluacion_nombre": "Primer Parcial Teórico-Práctico",
#                     "evaluacion_tipo": "parcial",
#                     "calificacion": 2.0
#                 },
#                 {
#                     "evaluacion_nombre": "Trabajo Práctico Integrador Final",
#                     "evaluacion_tipo": "TP",
#                     "calificacion": 9.0
#                 },
#                 {
#                     "evaluacion_nombre": "Parcialito 1",
#                     "evaluacion_tipo": "parcialito",
#                     "calificacion": "-"
#                 }
#             ],
#             "equipos": [
#                 {   
#                     "nombre_equipo": "Equipo Artemis 3",
#                     "curso_nombre": "Introduccion al Desarrollo de Software - Lanzillota",
#                     "anio": 2026,
#                     "semestre": 1   
#                 },
#                 {
#                     "nombre_equipo": "Equipo Backend Masters",
#                     "curso_nombre": "Introduccion al Desarrollo de Software - Lanzillota",
#                     "anio": 2026,
#                     "semestre": 1
#                 }
#             ]
#         }           
#     }   
   
#     return render_template(
#         "perfil_alumno.html",
#         usuario=datos_perfil,
#         detalle=datos_perfil.get("detalles", {})
#     )


# @perfil_bp.route("/perfil/profesor")
# def perfil_profesor():

#     # Informacion de prueba para testeo
#     datos_perfil = {
#         "id": 2,
#         "email": "tvillegas@fi.uba.ar",
#         "rol": "profesor",
#         "detalles": {
#             "id_profesor": 1,
#             "nombre": "Tomas",
#             "apellido": "Villegas",
#             "departamento": "Computación",
#             "cursos_asignados": [
#                 {
#                     "curso_nombre": "Introducción al Desarrollo de Software - Lanzillota",
#                     "anio": 2026,
#                     "semestre": 1
#                 }
#             ],
#             "evaluaciones": [
#                 {
#                     "evaluacion_nombre": "Primer Parcial Teórico-Práctico",
#                     "evaluacion_tipo": "parcial",
#                     "estado_evaluacion": "corregido",
#                     "fecha": "2026-05-20"
#                 },
#                 {
#                     "evaluacion_nombre": "Trabajo Práctico Integrador Final",
#                     "evaluacion_tipo": "TP",
#                     "estado_evaluacion": "corregido",
#                     "fecha": "2026-06-17"
#                 },
#                 {
#                     "evaluacion_nombre": "Parcialito 1",
#                     "evaluacion_tipo": "parcialito",
#                     "estado_evaluacion": "pendiente",
#                     "fecha": "2026-05-13"
#                 }
#             ]    
#         }
#     }
   

#     return render_template(
#         "perfil_profesor.html",
#         usuario=datos_perfil,
#         detalle=datos_perfil.get("detalles", {})
#     )

from flask import Blueprint, flash, render_template, session, redirect, request
import requests

perfil_bp = Blueprint("perfil", __name__)


@perfil_bp.route("/perfil/alumno")
def perfil_alumno():
    if session.get("rol") != "alumno":
        flash("Solo los alumnos tienen acceso a esta funcionalidad.", "warning")
        return redirect("/")

    datos_perfil = {}
    try:
        response = requests.get(
            "http://127.0.0.1:5001/perfil/",
            headers={"Authorization": f"Bearer {session.get('token')}"},
            timeout=5
        )
        if response.ok:
            datos_perfil = response.json()
    except Exception:
        pass

    return render_template(
        "perfil_alumno.html",
        usuario=datos_perfil,
        detalle=datos_perfil.get("detalles", {})
    )


@perfil_bp.route("/perfil/profesor")
def perfil_profesor():
    if session.get("rol") != "profesor":
        flash("Solo los profesores tienen acceso a esta funcionalidad.", "warning")
        return redirect("/")

    datos_perfil = {}
    try:
        response = requests.get(
            "http://127.0.0.1:5001/perfil/",
            headers={"Authorization": f"Bearer {session.get('token')}"},
            timeout=5
        )
        if response.ok:
            datos_perfil = response.json()
    except Exception:
        pass

    return render_template(
        "perfil_profesor.html",
        usuario=datos_perfil,
        detalle=datos_perfil.get("detalles", {})
    )


@perfil_bp.route("/perfil/contrasena", methods=["POST"])
def cambiar_contrasena():
    try:
        response = requests.put(
            "http://127.0.0.1:5001/perfil/contrasena",
            headers={"Authorization": f"Bearer {session.get('token')}"},
            json={
                "contrasena_actual": request.form.get("contrasena_actual"),
                "contrasena_nueva": request.form.get("contrasena_nueva")
            },
            timeout=5
        )
        if response.ok:
            flash("Contraseña actualizada correctamente.", "success")
        else:
            flash(response.json().get("error", "Error al actualizar."), "danger")
    except Exception as e:
        flash(str(e), "danger")
    return redirect(request.referrer)


@perfil_bp.route("/perfil/editar", methods=["POST"])
def editar_perfil():
    try:
        rol = session.get("rol")
        body = {
            "nombre": request.form.get("nombre"),
            "email": request.form.get("email")
        }
        if rol == "alumno":
            body["apellido"] = request.form.get("apellido")
        elif rol == "profesor":
            body["departamento"] = request.form.get("departamento")

        response = requests.put(
            "http://127.0.0.1:5001/perfil/editar",
            headers={"Authorization": f"Bearer {session.get('token')}"},
            json=body,
            timeout=5
        )
        if response.ok:
            flash("Perfil actualizado correctamente.", "success")
        else:
            flash(response.json().get("error", "Error al actualizar."), "danger")
    except Exception as e:
        flash(str(e), "danger")
    return redirect(request.referrer)


@perfil_bp.route("/perfil/historial", methods=["GET"])
def descargar_historial():
    try:
        response = requests.get(
            "http://127.0.0.1:5001/perfil/historial",
            headers={"Authorization": f"Bearer {session.get('token')}"},
            timeout=5
        )
        if response.ok:
            return response.content, 200, {
                "Content-Type": "text/csv",
                "Content-Disposition": "attachment; filename=historial.csv"
            }
        else:
            flash("No se pudo descargar el historial.", "danger")
    except Exception as e:
        flash(str(e), "danger")
    return redirect(request.referrer)