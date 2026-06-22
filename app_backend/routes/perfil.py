from flask import Blueprint, jsonify, request, session
from werkzeug.security import check_password_hash
from utils.auth import token_required
from data.queries import obtener_usuario_por_id, obtener_detalles_profesor, cambiar_contrasena, editar_perfil_profesor

perfil_bp = Blueprint('perfil', __name__)

@perfil_bp.route('/', methods=['GET'])
@token_required
def get_perfil(current_user):
   try:
       user_id = current_user.get("id")
       
       if user_id == "id_usuario" or not user_id:
           user_id = session.get("user_id")
       else:
           user_id = int(user_id)
           
       if not user_id:
           return jsonify({'error': 'Usuario no encontrado o sesión inválida'}), 404

       user_data = obtener_usuario_por_id(user_id)

       if not user_data:
           return jsonify({'error': 'Usuario no encontrado'}), 404

       response_data = {
           "id": user_data['id_usuario'],
           "email": user_data['email'],
           "rol": user_data['rol'],
           "detalles": None
       }


       if user_data['rol'] == 'profesor':
           profesor_data = obtener_detalles_profesor(user_id)
           if profesor_data:
               response_data["detalles"] = profesor_data

       return jsonify(response_data), 200

   except Exception as e:
       return jsonify({"error": "Error interno", "detalles": str(e)}), 500


@perfil_bp.route('/contrasena/', methods=['PUT'])
@token_required
def put_contrasena(current_user):
   try:
       user_id = current_user.get("id")
       if user_id == "id_usuario" or not user_id:
           user_id = session.get("user_id")
       else:
           user_id = int(user_id)
           
       if not user_id:
           return jsonify({'error': 'Usuario no autenticado'}), 401

       data = request.get_json()
       contrasena_actual = data.get('contrasena_actual')
       contrasena_nueva = data.get('contrasena_nueva')

       if not contrasena_actual or not contrasena_nueva:
           return jsonify({'error': 'Faltan datos'}), 400

       user_data = obtener_usuario_por_id(user_id)
       if not check_password_hash(user_data['contrasenia'], contrasena_actual):
           return jsonify({'error': 'Contraseña actual incorrecta'}), 401

       resultado = cambiar_contrasena(user_id, contrasena_nueva)
       if resultado:
           return jsonify({'message': 'Contraseña actualizada correctamente'}), 200

       return jsonify({'error': 'No se pudo actualizar la contraseña'}), 500

   except Exception as e:
       return jsonify({"error": "Error interno", "detalles": str(e)}), 500


@perfil_bp.route('/editar/', methods=['PUT'])
@token_required
def put_editar_perfil(current_user):
   try:
       user_id = current_user.get("id")
       if user_id == "id_usuario" or not user_id:
           user_id = session.get("user_id")
       else:
           user_id = int(user_id)
           
       rol = current_user.get("rol") or session.get("rol")
       
       if not user_id:
           return jsonify({'error': 'Usuario no autenticado'}), 401

       data = request.get_json()

       if rol == 'profesor':
           resultado = editar_perfil_profesor(
               user_id,
               data.get('nombre'),
               data.get('departamento'),
               data.get('email')
           )
       else:
           return jsonify({'error': 'Rol no reconocido'}), 403

       if resultado:
           return jsonify({'message': 'Perfil actualizado correctamente'}), 200

       return jsonify({'error': 'No se pudo actualizar el perfil'}), 500

   except Exception as e:
       return jsonify({"error": "Error interno", "detalles": str(e)}), 500


