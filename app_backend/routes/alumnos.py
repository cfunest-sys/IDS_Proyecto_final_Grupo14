from flask import Blueprint

alumnos_bp = Blueprint('alumnos', __name__)

@alumnos_bp.route('/login', methods=['POST'])
def login():
    # Hace falta agregar la lógica para el inicio de sesión
    return 'Inicio de sesión exitoso'

@alumnos_bp.route('/register', methods=['POST'])
def register():
    # Hace falta agregar la lógica para el registro de usuarios
    return 'Registro exitoso'