from flask import Flask, render_template
from routes.routes import inicio
from routes.evaluaciones import evaluaciones
from routes.equipos import equipos

PORT = 8080

app = Flask(__name__)
app.register_blueprint(inicio)
app.register_blueprint(evaluaciones)
app.register_blueprint(equipos)

app.secret_key = "six_seven"

@app.route("/alumnos")##solamente de prueba
def mostrar_alumnos():
    alumnos = ({"nombre":"pepe", "legajo":112533, "estado": "activo"},
        {"nombre":"maria", "legajo":114529, "estado": "activo"},
        {"nombre":"pedro", "legajo":111572, "estado": "inactivo"},
        {"nombre":"laura", "legajo":115343, "estado": "activo"},
        {"nombre":"juan", "legajo":113323, "estado": "inactivo"});
    return render_template("alumnos.html", alumnos=alumnos)

@app.route("/notas")
def notas():
    return render_template("notas.html")



if __name__ == "__main__":
    app.run(debug=True, port=PORT)