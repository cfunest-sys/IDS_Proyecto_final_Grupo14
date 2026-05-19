from flask import Blueprint, request, jsonify

profesores_bp = Blueprint('profesores', __name__)

@profesores_bp.route('/login', methods=['POST'])
def login():
    # Hace falta agregar la lógica para el inicio de sesión
    return 'Inicio de sesión exitoso'