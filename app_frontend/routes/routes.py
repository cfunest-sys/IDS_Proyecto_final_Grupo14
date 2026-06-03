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

@inicio.route("/equipos")
def equipos():

    return render_template("equipos.html")

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
            "http://127.0.0.1:5001/api/profesores/login",
            json=data,
            timeout=5
        )

        if response.ok:
            flash("Login exitoso", "success")
            return redirect("/")

        return render_template(
            "login.html",
            error="No se pudo iniciar sesion"
        )

    return render_template("login.html")
