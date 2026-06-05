from urllib import response

from flask import Blueprint, jsonify, redirect, render_template, request, flash, session
import requests

inicio = Blueprint("inicio", __name__)

@inicio.route("/")
def index():
    return render_template("inicio.html")

@inicio.route("/asistencia", methods=["GET", "POST"])
def asistencia():
    #LOGICA SOLO PARA LA GENERACION DE QR y EL REGISTRO DE LA ASISTENCIA
    qr_generado = None
    mensaje = None
    rol= session.get("rol")
    if request.method == "POST":
        if rol == "profesor":
            try:

                respuesta = requests.post( "http://localhost:5001/api/asistencia/generar-qr")
                data = respuesta.json()
                if respuesta.status_code == 200:
                    qr_generado = data.get("qr_code")
                else:
                    mensaje = data.get("error")
            except Exception as e:
                mensaje = str(e)

        elif rol == "alumno":
            legajo = request.form.get("legajo")
            qr_code = request.form.get("qr_code")
            try:

                respuesta = requests.post( "http://localhost:5001/api/asistencia/registrar",
                    json={
                        "legajo": legajo,
                        "qr_code": qr_code
                    }
                )
                data = respuesta.json()
                mensaje = (
                    data.get("message")
                    or data.get("error")
                )
            except Exception as e:
                mensaje = str(e)

    return render_template(
        "asistencia.html",
        rol=rol,
        qr_generado=qr_generado,
        mensaje=mensaje
    )

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