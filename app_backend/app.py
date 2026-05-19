from flask import Flask
from routes.alumnos import alumnos_bp
from routes.profesores import profesores_bp

app = Flask(__name__)
app.register_blueprint(alumnos_bp, url_prefix='/api/alumnos')
app.register_blueprint(profesores_bp, url_prefix='/api/profesores')

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':    
    app.run(debug=True)

