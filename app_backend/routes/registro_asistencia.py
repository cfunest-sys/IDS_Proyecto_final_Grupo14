from flask import Blueprint, request, jsonify, session
from database.db import get_connection 

asistencia_bp = Blueprint("asistencia", __name__)

@asistencia_bp.route("/api/asistencia/registrar", methods= ["POST"])
def asistencia_registro():

    if 'usuario_id' not in session or session.get('rol') != 'alumno':
        return jsonify({"error": "No autorizado. Debe iniciar sesion como alumno"}), 401
    
    alumno_id = session.get('alumno_id')

    data = request.get_json()
    if not data or 'qr_code' not in data:
        return jsonify({"error": "Codigo QR no proporcionado"}), 400
    
    qr_code = data.get('qr_code')
    if not qr_code: 
            return jsonify({"error": "El codigo QR es invalido ha expirado"}), 400

    try:
        connection = get_connection()
        cursor = connection.cursor()

        #Evitemos que se duplique la asistencia
        query_duplicado= "SELECT id FROM asistencia WHERE alumno_id = %s and fecha = CURDATE() "
        cursor.execute(query_duplicado, (alumno_id,))
        if cursor.fetchone():
             cursor.close()
             connection.close()
             return jsonify({"error": "Ya has registrado tu asistencia en la clase de hoy"}), 400
        
        #Registramos asistencia
        query_asistencia = "INSERT INTO asistencia (alumno_id, fecha, qr_code, registrado_en) VALUES (%s, CURDATE(), %s, NOW())"
        cursor.execute(query_asistencia, (alumno_id, qr_code))
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({"message": "¡Asistencia guardada con éxito!"}), 200
    except Exception as e:
         try:
              connection.rollback()
              connection.close()
         except: 
              pass
         return jsonify({"error": f"Error del servidor {str(e)}"}), 500