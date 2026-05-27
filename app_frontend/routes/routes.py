from flask import Blueprint, render_template, request

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
