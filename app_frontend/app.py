from flask import Flask, render_template
from routes.routes import inicio

PORT = 8080

app = Flask(__name__)
app.register_blueprint(inicio)

app.secret_key = "six_seven"

@app.route("/alumnos")##solamente de prueba
def mostrar_alumnos():
    alumnos = ({"nombre":"pepe", "legajo":112533, "estado": "activo"},
        {"nombre":"maria", "legajo":114529, "estado": "activo"},
        {"nombre":"pedro", "legajo":111572, "estado": "inactivo"},
        {"nombre":"laura", "legajo":115343, "estado": "activo"},
        {"nombre":"juan", "legajo":113323, "estado": "inactivo"});
    return render_template("alumnos.html", alumnos=alumnos)

@app.route("/calendario")##solamente de prueba
def mostrar_calendario():
    eventos = [{"nombre":"tp1", "tipo":"TP", "fecha": "2026-05-21", "curso":1},
        {"nombre":"Primer Parcial Teórico-Práctico", "tipo":"parcial", "fecha": "2027-12-20", "curso":2},
        {"nombre":"Trabajo Práctico Integrador Final", "tipo":"TP", "fecha": "2026-05-01", "curso":2},
        {"nombre":"Control de Lectura - Parcialito 1", "tipo":"parcialito", "fecha": "2026-05-13", "curso":1}]
    mes_nombre = ("enero","febrero","marzo","abril","mayo","junio","julio","agosto",
                    "septiembre","octubre","noviembre","diciembre")
    año_actual = 2026 
    mes_actual = 5;
    dias=(31, 28 + año_actual % 4, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
    return render_template("calendario.html", mes_actual=mes_actual, dias=dias, año_actual=año_actual, 
        mes_nombre=mes_nombre,eventos=eventos)

@app.route("/notas")
def notas():
    return render_template("notas.html")



if __name__ == "__main__":
    app.run(debug=True, port=PORT)