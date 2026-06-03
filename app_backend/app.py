from flask import Flask
from flask_jwt_extended import JWTManager
import config
from routes.alumnos import alumnos_bp
from routes.profesores import profesores_bp
from routes.auth import auth_bp
from routes.reportes import reportes_bp
from routes.evaluaciones import evaluaciones_bp
from routes.notas import notas_bp
from routes.equipos import equipos_bp
from routes.perfil import perfil_bp

PORT = 5001
app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = config.JWT_SECRET_KEY
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = config.JWT_ACCESS_TOKEN_EXPIRES
jwt = JWTManager(app)

app.register_blueprint(alumnos_bp, url_prefix="/api/alumnos")
app.register_blueprint(profesores_bp, url_prefix="/api/profesores")
app.register_blueprint(evaluaciones_bp, url_prefix="/api/evaluaciones")
app.register_blueprint(notas_bp, url_prefix="/api/notas")
app.register_blueprint(auth_bp)
app.register_blueprint(reportes_bp)
app.register_blueprint(equipos_bp, url_prefix='/api/equipos')
app.register_blueprint(perfil_bp, url_prefix='/api/perfil')


@app.route("/")
def hello_world():
    respuesta = {"mensaje":"Hello, World!"}
    return respuesta, 202


if __name__ == "__main__":
    app.run(debug=True, port=PORT)
