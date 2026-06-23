from flask import Blueprint, request, jsonify, send_file
from database.db import get_connection
from utils.auth import token_required, rol_required
from datetime import datetime, timedelta
import secrets
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from utils.auth import token_required, rol_required
import tempfile



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
    
#GENERAR REPORTE DE ASISTENCIA 
@asistencia_bp.route("/generar-reporte", methods=["POST"])
@token_required
@rol_required("profesor")
def generar_reporte(current_user):
    
    try:
     data = request.get_json()

     if not data:
        return jsonify({"error": "No se recibieron datos"}), 400

     fecha = data.get("fecha")
     id_curso = data.get("curso")

     if not fecha:
        return jsonify({"error": "Fecha obligatoria"}), 400

     if not id_curso:
        return jsonify({"error": "Curso obligatorio"}), 400

     connection = get_connection()
     cursor = connection.cursor(dictionary=True)

     # Total de alumnos del curso
     query_total = """
        SELECT COUNT(*) AS total_alumnos
        FROM alumnos
        WHERE curso = %s
     """

     cursor.execute(query_total, (id_curso,))
     total_alumnos = cursor.fetchone()["total_alumnos"]

     # Datos del curso
     query_curso = """
        SELECT *
        FROM cursos
        WHERE id_curso = %s
     """

     cursor.execute(query_curso, (id_curso,))
     curso = cursor.fetchone()

     # Asistencias registradas
     query_presentes = """
        SELECT
            a.alumno_legajo,
            al.nombre,
            al.apellido
        FROM asistencia a
        JOIN alumnos al
            ON a.alumno_legajo = al.legajo
        WHERE a.fecha = %s
        AND al.curso = %s
        ORDER BY al.apellido, al.nombre
     """

     cursor.execute(query_presentes, (fecha, id_curso))
     presentes = cursor.fetchall()

     total_presentes = len(presentes)

     # Crear PDF temporal
     temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf")

     doc = SimpleDocTemplate(
        temp_file.name,
        pagesize=A4)

     styles = getSampleStyleSheet()

     elementos = []

     elementos.append(
        Paragraph(
            "Reporte de Asistencia",
            styles["Title"]
        )
     )

     elementos.append(Spacer(1, 12))

     elementos.append(
        Paragraph(
            f"Fecha: {fecha}",
            styles["Normal"]
        ))

     elementos.append(
        Paragraph(
            f"Curso: Año {curso['anio']} - Semestre {curso['semestre']}",
            styles["Normal"]
        )
    )

     elementos.append(
        Paragraph(
            f"Total de alumnos: {total_alumnos}",
            styles["Normal"]
        )
    )

     elementos.append(
        Paragraph(
            f"Total de presentes: {total_presentes}",
            styles["Normal"]
        )
    )

     elementos.append(Spacer(1, 20))

     data_tabla = [
        ["Legajo", "Nombre", "Apellido"]
    ]

     for alumno in presentes:
        data_tabla.append([
            str(alumno["alumno_legajo"]),
            alumno["nombre"],
            alumno["apellido"]
        ])

     tabla = Table(data_tabla)

     tabla.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold")
        ])
     )

     elementos.append(tabla)

     doc.build(elementos)

     cursor.close()
     connection.close()

     return send_file(
        temp_file.name,
        as_attachment=True,
        download_name=f"reporte_asistencia_{fecha}.pdf",
        mimetype="application/pdf"
     )

    except Exception as e:
     print(e)

     return jsonify({
        "error": "Error interno del servidor"
     }), 500
