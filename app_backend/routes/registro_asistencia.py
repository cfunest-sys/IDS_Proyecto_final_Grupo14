from flask import Blueprint, request, jsonify
from database.db import get_connection
from utils.auth import token_required, rol_required
from datetime import datetime, timedelta
import secrets

asistencia_bp = Blueprint("asistencia", __name__)
#GENERAR QR
@asistencia_bp.route("/generar-qr", methods=["POST"])
@token_required
def generar_qr(current_user):

    try:

        connection = get_connection()
        cursor = connection.cursor()

        # Desactivar QR anteriores
        query_desactivar = """ UPDATE qr_asistencia SET activo = FALSE WHERE activo = TRUE """

        cursor.execute(query_desactivar)

        # Generar código aleatorio
        codigo_qr = secrets.token_urlsafe(16)

        expiracion = datetime.now() + timedelta(minutes=45)

        query_insert = """ INSERT INTO qr_asistencia ( codigo, fecha_generacion, expiracion, activo ) VALUES ( %s, NOW(), %s, TRUE) """

        cursor.execute(
            query_insert,
            (
                codigo_qr,
                expiracion
            )
        )

        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({
            "success": True,
            "message": "QR generado correctamente",
            "qr_code": codigo_qr,
            "expira": expiracion.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        }), 200

    except Exception as e:

        try:
            connection.rollback()
            connection.close()
        except:
            pass

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


#REGISTRAR ASISTENCIA
@asistencia_bp.route("/registrar", methods=["POST"])
def registrar_asistencia():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "No se recibieron datos"
        }), 400

    legajo = data.get("legajo")
    qr_code = data.get("qr_code")

    if not legajo:
        return jsonify({
            "error": "Legajo no proporcionado"
        }), 400

    if not qr_code:
        return jsonify({
            "error": "Código QR no proporcionado"
        }), 400

    try:

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # Verificar QR activo
        query_qr = """ SELECT * FROM qr_asistencia WHERE codigo = %s AND activo = TRUE AND expiracion > NOW() """

        cursor.execute(query_qr, (qr_code,))
        qr = cursor.fetchone()

        if not qr:

            cursor.close()
            connection.close()

            return jsonify({
                "error": "QR inválido o expirado"
            }), 400

        # Verificar alumno existente
        query_alumno = """ SELECT legajo FROM alumnos WHERE legajo = %s """

        cursor.execute(query_alumno, (legajo,))
        alumno = cursor.fetchone()

        if not alumno:

            cursor.close()
            connection.close()

            return jsonify({
                "error": "Alumno inexistente"
            }), 404

        # Verificar asistencia duplicada
        query_duplicado = """ SELECT * FROM asistencia WHERE alumno_legajo = %s AND fecha = CURDATE() """

        cursor.execute(query_duplicado, (legajo,))

        if cursor.fetchone():

            cursor.close()
            connection.close()

            return jsonify({
                "error": "La asistencia ya fue registrada"
            }), 400

        # Registrar asistencia
        query_insert = """ INSERT INTO asistencia ( alumno_legajo, qr_id , fecha, registrado_en) VALUES ( %s, %s, CURDATE(), NOW()) """

        cursor.execute(
            query_insert,
            (
                legajo,
                qr["id_qr"]
            )
        )

        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({
            "message": "Asistencia registrada correctamente"
        }), 201

    except Exception as e:

        try:
            connection.rollback()
            connection.close()
        except:
            pass

        return jsonify({
            "error": f"Error del servidor: {str(e)}"
        }), 500