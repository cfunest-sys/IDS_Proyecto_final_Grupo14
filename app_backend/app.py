from flask import Flask
from flask_jwt_extended import JWTManager
import config
from utils.extensions import mail
from routes.alumnos import alumnos_bp
from routes.profesores import profesores_bp
from routes.auth import auth_bp
from routes.reportes import reportes_bp
from routes.evaluaciones import evaluaciones_bp
from routes.equipos import equipos_bp
from routes.perfil import perfil_bp
from routes.materiales import materiales_bp
from routes.notas import notas_bp
from routes.login import login_bp
from routes.dashboard import dashboard_bp
from routes.registro_asistencia import asistencia_bp
from routes.cursos import cursos_bp



PORT = 5001
app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = config.JWT_SECRET_KEY
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = config.JWT_ACCESS_TOKEN_EXPIRES
jwt = JWTManager(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_DEFAULT_SENDER'] = 'noreply.ids14@gmail.com'
app.config['MAIL_USERNAME'] = 'noreply.ids14@gmail.com'
app.config['MAIL_PASSWORD'] = 'ixnr exlk necd zqhu'

mail.init_app(app)

app.register_blueprint(alumnos_bp, url_prefix="/api/alumnos")
app.register_blueprint(profesores_bp, url_prefix="/api/profesores")
app.register_blueprint(evaluaciones_bp, url_prefix="/api/evaluaciones")
app.register_blueprint(auth_bp)
app.register_blueprint(reportes_bp)
app.register_blueprint(equipos_bp, url_prefix="/api/equipos")
app.register_blueprint(perfil_bp, url_prefix="/api/perfil")
app.register_blueprint(materiales_bp, url_prefix="/api/materiales")
app.register_blueprint(notas_bp, url_prefix="/api/notas")
app.register_blueprint(login_bp, url_prefix="/api/login")
app.register_blueprint(dashboard_bp)
app.register_blueprint(asistencia_bp, url_prefix="/api/asistencia")
app.register_blueprint(cursos_bp, url_prefix="/api/cursos")


@app.route("/")
def hello_world():
    respuesta = {"mensaje": "Hello, World!"}
    return respuesta, 202


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=PORT)
