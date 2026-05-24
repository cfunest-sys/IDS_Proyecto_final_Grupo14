from flask import Flask
from routes.alumnos import alumnos_bp
from routes.profesores import profesores_bp
from routes.auth import auth_bp
from routes.reportes import reportes_bp
from routes.evaluaciones import evaluaciones_bp
from routes.equipos import equipos_bp

app = Flask(__name__)
app.register_blueprint(alumnos_bp, url_prefix='/api/alumnos')
app.register_blueprint(profesores_bp, url_prefix='/api/profesores')
app.register_blueprint(evaluaciones_bp, url_prefix='/api/evaluaciones')
app.register_blueprint(auth_bp)
app.register_blueprint(reportes_bp)
app.register_blueprint(equipos_bp, url_prefix='/api/equipos')

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':    
    app.run(debug=True)
