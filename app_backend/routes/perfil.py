from flask import Blueprint, jsonify, session
from data.queries import get_user_by_id

perfil_bp = Blueprint('perfil', __name__)

@perfil_bp.route('/', methods=['GET'])
def get_perfil():
    try:
        user_id = session.get('user_id')

        if not user_id:
            return jsonify({'error': 'No autorizado. Por favor, inicia sesión.'}), 401

        user_data = get_user_by_id(user_id)

        if not user_data:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        return jsonify({
            "id": user_data['id_usuario'],
            "email": user_data['email'],
            "rol": user_data['rol']
        }), 200

    except Exception as e:
        return jsonify({"error": "Error interno", "detalles": str(e)}), 500
