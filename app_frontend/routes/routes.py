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

        data = {
            "nombre": nombre,
            "email": email,
            "password": password
        
        }
        print("Antes del requests.post")

        response = requests.post(
            "http://127.0.0.1:5000/api/alumnos/register",
            json=data,
            timeout=5
        )

        print("Después del requests.post")
        print(response.status_code)
        print(response.text)
        if response.ok:
            flash("Usuario registrado correctamente", "success")
            return redirect("/")


        return render_template(
            "registro.html",
            error="No se pudo registrar el alumno"
        )

    return render_template("registro.html")

@inicio.route("/equipos")
def equipos():

    return render_template("equipos.html")

@inicio.route("/login", methods=["GET", "POST"])
def login():
 #logica del login
    return render_template("login.html")
