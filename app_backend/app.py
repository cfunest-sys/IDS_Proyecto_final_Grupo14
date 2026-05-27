from flask import Flask, render_template
from flask_jwt_extended import JWTManager
import config
from routes.alumnos import alumnos_bp
from routes.profesores import profesores_bp
from routes.auth import auth_bp
from routes.reportes import reportes_bp
from routes.evaluaciones import evaluaciones_bp
from routes.equipos import equipos_bp
from routes.perfil import perfil_bp

app = Flask(__name__, 
            template_folder='../app_frontend/templates', 
            static_folder='../app_frontend/static')

app.config["JWT_SECRET_KEY"] = config.JWT_SECRET_KEY
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = config.JWT_ACCESS_TOKEN_EXPIRES
jwt = JWTManager(app)

app.register_blueprint(alumnos_bp, url_prefix="/api/alumnos")
app.register_blueprint(profesores_bp, url_prefix="/api/profesores")
app.register_blueprint(evaluaciones_bp, url_prefix="/api/evaluaciones")
app.register_blueprint(auth_bp)
app.register_blueprint(reportes_bp)
app.register_blueprint(equipos_bp, url_prefix='/api/equipos')
app.register_blueprint(perfil_bp, url_prefix='/api/perfil')

@app.route('/dashboard')
def dashboard_profesor():
    return "Este es el dashboard del profesor (provisional)"

@app.route('/')
def home():
    return "Hola! El servidor está funcionando."

@app.route('/evaluaciones')
def evaluaciones():
    return render_template('evaluaciones.html')

@app.route('/notas')
def notas():
    return render_template('notas.html') 

if __name__ == '__main__':
    app.run(debug=True)

if __name__ == "__main__":
    app.run(debug=True)
