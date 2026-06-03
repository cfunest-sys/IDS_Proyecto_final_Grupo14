from flask import Blueprint, request, jsonify
# Decorador de sesión @token_required (autenticación JWT)
from utils.auth import token_required 
from data.queries import get_notas_filtradas, get_promedio_notas, verificar_alumno_y_evaluacion, guardar_o_actualizar_nota

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

@notas_bp.route('/notas', methods=['POST'])
@token_required
def cargar_nota(current_user):
    try:
        # Validación de rol
        if current_user.get('rol') != 'profesor':
            return jsonify({"error": "Acceso denegado. Solo profesores."}), 403

        data = request.get_json()
        if not data:
            return jsonify({"error": "Body vacío"}), 400

        # Extracción de campos
        alumno_id = data.get('alumno_id')
        evaluacion_id = data.get('evaluacion_id')
        calificacion = data.get('calificacion')

        # Validación de campos obligatorios
        if alumno_id is None or evaluacion_id is None or calificacion is None:
            return jsonify({"error": "Faltan campos obligatorios"}), 400

        # Validación de rango
        try:
            calificacion = float(calificacion)
            if calificacion < 0 or calificacion > 10:
                return jsonify({"error": "Calificación debe ser 0 a 10"}), 400
        except (ValueError, TypeError):
            return jsonify({"error": "Calificación inválida"}), 400

        # Validación existencia
        if not verificar_alumno_y_evaluacion(alumno_id, evaluacion_id):
            return jsonify({"error": "Alumno o evaluación no existe"}), 404

        # Guardar/actualizar nota
        nota = guardar_o_actualizar_nota(alumno_id, evaluacion_id, calificacion)

        # Formato de fecha para respuesta
        fecha_respuesta = None

        if nota and nota.get('fecha'):
            fecha_log = nota['fecha'].strftime('%Y-%m-%d')
            fecha_respuesta = fecha_log

        # Log simple
        print(f"LOG - [{fecha_log}] Profesor {current_user.get('id')} actualizó nota alumno {alumno_id}")

        # Notificación simple
        print(f"NOTIFICACIÓN - Alumno {alumno_id}: nota registrada")

        # Respuesta con datos de la nota
        return jsonify({
            "mensaje": "Nota guardada correctamente",
            "nota": {
                "alumno_id": nota.get("alumno_id"),
                "evaluacion_id": nota.get("evaluacion_id"),
                "calificacion": nota.get("calificacion"),
                "fecha": fecha_respuesta
            }
        }), 201

    except Exception as e:
        print(f"Error en cargar_nota: {e}")
        return jsonify({"error": "Error interno"}), 500    