from urllib import response

from flask import Blueprint, redirect, render_template, request, flash
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

        data = {"nombre": nombre, "email": email, "password": password}
        print("Antes del requests.post")

        response = requests.post("http://127.0.0.1:5000/api/alumnos/register", json=data, timeout=5)

        print("Después del requests.post")
        print(response.status_code)
        print(response.text)
        if response.ok:
            flash("Usuario registrado correctamente", "success")
            return redirect("/")

        return render_template("registro.html", error="No se pudo registrar el alumno")

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
