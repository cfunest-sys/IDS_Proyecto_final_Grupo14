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
    eventos = ({"nombre":"tp1", "tipo":"TP", "dia": "21", "curso":1},
        {"nombre":"Primer Parcial Teórico-Práctico", "tipo":"parcial", "dia": "20", "curso":2},
        {"nombre":"Trabajo Práctico Integrador Final", "tipo":"TP", "dia": "1", "curso":1},
        {"nombre":"Control de Lectura - Parcialito 1", "tipo":"parcialito", "dia": "13", "curso":1});
    mes="febrero"
    dias=29
    ##por como lo hice cada vez que se quiera avanzar o retroceder mes hay que llamar al /calendario devuelta
    ##o el endpoint del front con el que lo renderizemos al calendario.html
    ##tambien solo hay que pasarle los eventos de ese mes, si diferencia si eran de este mes en jinja era muy engorroso
    año=2026 
    bisiesto=False
    return render_template("calendario.html", mes=mes, dias=dias, año=año, bisiesto=bisiesto,eventos=eventos)

@app.route("/notas")
def notas():
    return render_template("notas.html")

if __name__ == "__main__":
    app.run(debug=True, port=PORT)