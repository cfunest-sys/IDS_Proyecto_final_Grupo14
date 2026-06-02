from flask import Blueprint, request, jsonify
# Decorador de sesión @token_required (autenticación JWT)
from utils.auth import token_required 
from data.queries import get_notas_filtradas, get_promedio_notas

notas_bp = Blueprint('notas', __name__)

@notas_bp.route('/notas', methods=['GET'])
@token_required
def listar_notas(current_user): 
    try:
        usuario_id = current_user.get('id')
        rol = current_user.get('rol')

        alumno_id = request.args.get('alumno_id', type=int)
        evaluacion_id = request.args.get('evaluacion_id', type=int)
        id_curso = request.args.get('id_curso', type=int)

        # Paginación
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=10, type=int)
        
        if page < 1: 
            page = 1
        if per_page < 1: 
            per_page = 10
        
        offset = (page - 1) * per_page

        # Llamo a las funciones de consulta
        notas = get_notas_filtradas(rol, usuario_id, alumno_id, evaluacion_id, id_curso, per_page, offset)
        promedio = get_promedio_notas(rol, usuario_id, alumno_id, evaluacion_id, id_curso)

        # Formateo de fechas a string para JSON
        for nota in notas:
            if nota['fecha']:
                nota['fecha'] = nota['fecha'].strftime('%Y-%m-%d')

        return jsonify({
            "page": page,
            "per_page": per_page,
            "promedio": promedio,
            "notas": notas
        }), 200

    except Exception as e:
        print(f"Error en endpoint listar_notas: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500