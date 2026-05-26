from flask import Blueprint, jsonify, send_file
from database.db import get_connection
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
import tempfile

reportes_bp = Blueprint("reportes", __name__)


def crear_pdf_con_tabla(titulo, encabezados, filas):
    archivo = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    )

    archivo.close()

    doc = SimpleDocTemplate(
        archivo.name,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    elementos = []
    estilos = getSampleStyleSheet()

    elementos.append(
        Paragraph(titulo, estilos["Title"])
    )

    elementos.append(Spacer(1, 12))
    datos = [encabezados]

    for fila in filas:
        datos.append([
            str(valor) if valor is not None else ""
            for valor in fila
        ])

    tabla = Table(datos)

    tabla.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ])
    )
    
    elementos.append(tabla)
    doc.build(elementos)
    
    return archivo.name


@reportes_bp.route("/api/reportes/alumnos", methods=["GET"])
def reporte_alumnos():
    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                a.legajo,
                a.nombre,
                a.estado,
                u.email
            FROM alumnos a
            LEFT JOIN usuarios u
                ON a.id_usuario = u.id_usuario
            ORDER BY a.nombre
        """)

        filas = cur.fetchall()

        ruta = crear_pdf_con_tabla(
            "Reporte de Alumnos",
            ["Legajo", "Nombre", "Estado", "Email"],
            filas
        )

        return send_file(
            ruta,
            as_attachment=True,
            download_name="reporte_alumnos.pdf",
            mimetype="application/pdf"
        )

    except Exception as e:
        print(e)
        return jsonify({
            "error": "Error interno del servidor."
        }), 500

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@reportes_bp.route("/api/reportes/estadisticas", methods=["GET"])
def reporte_estadisticas():
    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        consultas = [
            ("Total de alumnos", "SELECT COUNT(*) FROM alumnos"),
            ("Total de profesores", "SELECT COUNT(*) FROM profesores"),
            ("Total de cursos", "SELECT COUNT(*) FROM cursos"),
            ("Total de evaluaciones", "SELECT COUNT(*) FROM evaluaciones"),
            ("Total de equipos", "SELECT COUNT(*) FROM equipos"),
        ]

        filas = []

        for descripcion, sql in consultas:
            cur.execute(sql)
            total = cur.fetchone()[0]
            filas.append((descripcion, total))

        ruta = crear_pdf_con_tabla(
            "Reporte de Estadísticas",
            ["Indicador", "Valor"],
            filas
        )

        return send_file(
            ruta,
            as_attachment=True,
            download_name="reporte_estadisticas.pdf",
            mimetype="application/pdf"
        )

    except Exception as e:
        print(e)
        return jsonify({
            "error": "Error interno del servidor."
        }), 500

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@reportes_bp.route("/api/reportes/equipos", methods=["GET"])
def reporte_equipos():
    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                e.id_equipo,
                e.nombre_equipo,
                c.nombre
            FROM equipos e
            LEFT JOIN cursos c
                ON e.id_curso = c.id_curso
            ORDER BY e.nombre_equipo
        """)

        filas = cur.fetchall()

        ruta = crear_pdf_con_tabla(
            "Reporte de Equipos",
            ["ID", "Equipo", "Curso"],
            filas
        )

        return send_file(
            ruta,
            as_attachment=True,
            download_name="reporte_equipos.pdf",
            mimetype="application/pdf"
        )

    except Exception as e:
        print(e)
        return jsonify({
            "error": "Error interno del servidor."
        }), 500

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
            
