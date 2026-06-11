from flask import Blueprint, jsonify
from utils.auth import token_required
from data.queries import obtener_usuario_por_id, obtener_detalles_alumno, obtener_detalles_profesor

perfil_bp = Blueprint('perfil', __name__)

@perfil_bp.route('/', methods=['GET'])
@token_required
def get_perfil(current_user):
    try:
        user_id = current_user["id"]

        user_data = obtener_usuario_por_id(user_id)

        if not user_data:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        response_data = {
            "id": user_data['id_usuario'],
            "email": user_data['email'],
            "rol": user_data['rol'],
            "detalles": None
        }

        if user_data['rol'] == 'alumno':
            alumno_data = obtener_detalles_alumno(user_id)
            if alumno_data:
                response_data["detalles"] = alumno_data
        
        elif user_data['rol'] == 'profesor':
            profesor_data = obtener_detalles_profesor(user_id)
            if profesor_data:
                response_data["detalles"] = profesor_data

        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({"error": "Error interno", "detalles": str(e)}), 500
