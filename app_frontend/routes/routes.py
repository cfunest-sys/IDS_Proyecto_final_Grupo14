from urllib import response

from flask import Blueprint, jsonify, redirect, render_template, request, flash, session
import requests

inicio = Blueprint("inicio", __name__)


@inicio.route("/")
def index():
    return render_template("inicio.html")


@inicio.route("/asistencia", methods=["GET", "POST"])
def asistencia():

    if request.method == "POST":

        alumno = request.form.get("alumno")
        fecha = request.form.get("fecha")

    return render_template("asistencia.html")


@inicio.route("/reportes")
def reportes():
    return render_template("reportes.html")


@inicio.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        nombre = request.form.get("nombre")
        email = request.form.get("email")
        password = request.form.get("password")
        departamento = request.form.get("departamento")

        data = {
            "nombre": nombre,
            "email": email,
            "password": password,
            "departamento": departamento
        }

        response = requests.post(
            "http://127.0.0.1:5001/api/profesores/register",
            json=data,
            timeout=5
        )

        if response.ok:
            flash("Usuario registrado correctamente", "success")
            return redirect("/")

        return render_template(
            "registro.html",
            error="No se pudo registrar el profesor"
        )

    return render_template("registro.html")


@inicio.route("/material")
def material():
    materiales = []
    token = ""
    return render_template("materiales_profesor.html", materiales=materiales, token=token)


@inicio.route("/material/alumno")
def material_alumno():
    materiales = [
        {
            "id_material": 1,
            "titulo": "Apunte Clase 1 - Introducción",
            "descripcion": "Primer apunte del curso con conceptos básicos",
            "tipo_material": "apunte",
            "tema": "Introducción",
            "fecha_material": "2026-05-20",
            "estado": "publicado",
            "es_libre": False,
        },
        {
            "id_material": 2,
            "titulo": "Guía de Ejercicios N°1",
            "descripcion": "Ejercicios resueltos de la primera semana",
            "tipo_material": "guia",
            "tema": "Ejercicios",
            "fecha_material": "2026-05-22",
            "estado": "publicado",
            "es_libre": False,
        },
        {
            "id_material": 3,
            "titulo": "Video - Clase Grabada 1",
            "descripcion": "Grabación de la primera clase del curso",
            "tipo_material": "video",
            "tema": "Introducción",
            "fecha_material": "2026-05-20",
            "estado": "publicado",
            "es_libre": False,
        },
        {
            "id_material": 4,
            "titulo": "Guía de Python Básico",
            "descripcion": "Recopilación de conceptos de Python para principiantes",
            "tipo_material": "bibliografia",
            "tema": "Python",
            "fecha_material": "2026-05-25",
            "estado": "publicado",
            "es_libre": True,
        },
    ]
    return render_template("materiales_alumno.html", materiales=materiales, token="")


@inicio.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        data = {
            "email": email,
            "password": password
        }

        response = requests.post(
            "http://127.0.0.1:5001/api/login",
            json=data,
            timeout=5
        )

        if response.ok:

            resultado = response.json()
            usuario = resultado["usuario"]

            session["user_id"] = usuario["id"]
            session["email"] = usuario["email"]
            session["rol"] = usuario["rol"]

            if usuario.get("perfil"):
                session["nombre"] = usuario["perfil"].get("nombre")

            flash("Login exitoso", "success")

            if usuario["rol"] == "profesor":
                return redirect("/dashboard/profesor")

            return redirect("/")

        return render_template(
            "login.html",
            error="No se pudo iniciar sesión"
        )

    return render_template("login.html")


@inicio.route("/sesion")
def ver_sesion():

    return {
        "user_id": session.get("user_id"),
        "email": session.get("email"),
        "rol": session.get("rol"),
        "nombre": session.get("nombre")
    }


@inicio.route("/logout", methods=["GET"])
def logout():

    if not session.get("user_id"):
        flash("No hay una sesión iniciada.", "warning")
        return redirect("/")

    session.clear()

    flash("Sesión cerrada correctamente.", "success")

    return redirect("/")

@inicio.route("/alumnos/cargar-csv", methods=["POST"])
def cargar_csv():
    archivo = request.files.get("archivo")
    if not archivo:
        flash("No se envió archivo", "danger")
        return redirect("/alumnos")
    resp = requests.post(
        "http://127.0.0.1:5000/api/alumnos/cargar-csv",
        files={"archivo": (archivo.filename, archivo.stream, archivo.content_type)},
        timeout=30,
    )
    if resp.ok:
        data = resp.json()
        exitosos = data.get("exitosos", 0)
        errores = data.get("errores", [])
        flash(f"Se cargaron {exitosos} alumnos correctamente", "success")
        if errores:
            for e in errores:
                flash(f"Fila {e['fila']}: {e['motivo']}", "danger")
    else:
        flash("Error al cargar el archivo", "danger")
    return redirect("/alumnos")
