from flask import Blueprint, request, jsonify
from data.queries import get_alumno, get_alumnos, cargar_alumno, actualizar_alumno, eliminar_alumno

alumnos_bp = Blueprint('alumnos', __name__)

@alumnos_bp.route('/login', methods=['POST'])
def login():
    # Hace falta agregar la lógica para el inicio de sesión
    return 'Inicio de sesión exitoso'

@alumnos_bp.route('/register', methods=['POST'])
def register():
    # Hace falta agregar la lógica para el registro de usuarios
    return 'Registro exitoso'




@alumnos_bp.route('/<int:id>', methods=['GET'])
def obtener_alumno(id):
    alumno = get_alumno(id)
    return jsonify(alumno)

@alumnos_bp.route('/', methods=['GET'])
def obtener_alumnos():
    alumnos = get_alumnos()
    return jsonify(alumnos)

@alumnos_bp.route('/cargar', methods=['POST'])
def cargar_alumno_route():
    data = request.get_json()
    campo = ["nombre", "contrasenia", "email", "created_at", "estado", "rol"]
    if not data:
        return jsonify({"error": "Body vacío"}), 400
    for c in campo:
        if c not in data or data.get(c) is None:
            return jsonify({"error": "Body incompleto"}), 400
    resultado = cargar_alumno(data["nombre"], data["contrasenia"], data["email"], data["created_at"], data["estado"], data["rol"])
    return jsonify({"message": "Alumno cargado exitosamente", "id": resultado})

@alumnos_bp.route('/actualizar/<int:id>', methods=['PUT'])
def actualizar_alumno(id):
    data = request.get_json()
    campo = ["nombre", "contrasenia", "email", "created_at", "estado", "rol"]
    if not data:
        return jsonify({"error": "Body vacío"}), 400
    for c in campo:
        if c not in data or data.get(c) is None:
            return jsonify({"error": "Body incompleto"}), 400
    resultado = actualizar_alumno(id, data["nombre"], data["contrasenia"], data["email"], data["created_at"], data["estado"], data["rol"])
    return jsonify({"message": "Alumno actualizado exitosamente", "id": resultado})

@alumnos_bp.route('/eliminar/<int:id>', methods=['DELETE'])
def eliminar_alumno(id):
    resultado = eliminar_alumno(id)
    return jsonify({"message": "Alumno eliminado exitosamente", "id": resultado})