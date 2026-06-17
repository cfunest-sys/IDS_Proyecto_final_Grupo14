import os
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
from utils.auth import token_required, rol_required
import tempfile

reportes_bp = Blueprint("reportes", __name__)


def crear_pdf_por_cuatrimestre(titulo, encabezados, datos_agrupados):

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

    estilos = getSampleStyleSheet()
    elementos = []

    elementos.append(
        Paragraph(titulo, estilos["Title"])
    )

    elementos.append(Spacer(1, 12))

    for (anio, cuatrimestre), filas in datos_agrupados.items():

        elementos.append(
            Paragraph(
                f"Año {anio} - {cuatrimestre}° Cuatrimestre",
                estilos["Heading2"]
            )
        )

        elementos.append(Spacer(1, 8))

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
        elementos.append(Spacer(1, 15))

    doc.build(elementos)

    return archivo.name


@reportes_bp.route("/api/reportes/alumnos", methods=["GET"])
@token_required
def reporte_alumnos(current_user):
    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                a.legajo,
                CONCAT(a.nombre, ' ', a.apellido),
                a.estado,
                u.email,
                a.anio,
                a.cuatrimestre
            FROM alumnos a
            LEFT JOIN usuarios u
                ON a.id_usuario = u.id_usuario
            ORDER BY
                a.anio,
                a.cuatrimestre,
                a.apellido,
                a.nombre
        """)

        resultado = cur.fetchall()

        datos_agrupados = {}

        for fila in resultado:

            anio = fila[4]
            cuatrimestre = fila[5]

            clave = (anio, cuatrimestre)

            if clave not in datos_agrupados:
                datos_agrupados[clave] = []

            datos_agrupados[clave].append(
                fila[:4]
            )

        ruta = crear_pdf_por_cuatrimestre(
            "Reporte de Alumnos",
            ["Legajo", "Nombre", "Estado", "Email"],
            datos_agrupados
        )
        
        try:
            return send_file(
                ruta,
                as_attachment=True,
                download_name="reporte_alumnos.pdf",
                mimetype="application/pdf"
            )
        finally:
            os.unlink(ruta)

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
@token_required
def reporte_estadisticas(current_user):
    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()



        cur.execute("""
            SELECT DISTINCT
                anio,
                cuatrimestre
            FROM cursos
            ORDER BY
                anio,
                cuatrimestre
        """)

        periodos = cur.fetchall()

        datos_agrupados = {}

        for anio, cuatrimestre in periodos:

            filas = []

            cur.execute("""
                SELECT COUNT(*)
                FROM alumnos
                WHERE anio = %s
                AND cuatrimestre = %s
            """, (anio, cuatrimestre))

            filas.append(
                ("Total de alumnos", cur.fetchone()[0])
            )

            cur.execute("""
                SELECT COUNT(*)
                FROM cursos
                WHERE anio = %s
                AND cuatrimestre = %s
            """, (anio, cuatrimestre))

            filas.append(
                ("Total de cursos", cur.fetchone()[0])
            )

            cur.execute("""
                SELECT COUNT(*)
                FROM evaluaciones e
                INNER JOIN cursos c
                    ON e.id_curso = c.id_curso
                WHERE c.anio = %s
                AND c.cuatrimestre = %s
            """, (anio, cuatrimestre))

            filas.append(
                ("Total de evaluaciones", cur.fetchone()[0])
            )

            cur.execute("""
                SELECT COUNT(*)
                FROM equipos e
                INNER JOIN cursos c
                    ON e.id_curso = c.id_curso
                WHERE c.anio = %s
                AND c.cuatrimestre = %s
            """, (anio, cuatrimestre))

            filas.append(
                ("Total de equipos", cur.fetchone()[0])
            )

            datos_agrupados[
                (anio, cuatrimestre)
            ] = filas

        ruta = crear_pdf_por_cuatrimestre(
            "Reporte de Estadísticas",
            ["Indicador", "Valor"],
            datos_agrupados
        )

        try:
            return send_file(
                ruta,
                as_attachment=True,
                download_name="reporte_estadisticas.pdf",
                mimetype="application/pdf"
            )
        finally:
            os.unlink(ruta)

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
@token_required
def reporte_equipos(current_user):
    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                e.id_equipo,
                e.nombre_equipo,
                CONCAT(c.anio, ' ', c.cuatrimestre),
                c.anio,
                c.cuatrimestre
            FROM equipos e
            LEFT JOIN cursos c
                ON e.id_curso = c.id_curso
            ORDER BY
                c.anio,
                c.cuatrimestre,
                e.nombre_equipo
        """)

        resultado = cur.fetchall()

        datos_agrupados = {}

        for fila in resultado:

            anio = fila[3]
            cuatrimestre = fila[4]

            clave = (anio, cuatrimestre)

            if clave not in datos_agrupados:
                datos_agrupados[clave] = []

            datos_agrupados[clave].append(
                fila[:3]
            )

        ruta = crear_pdf_por_cuatrimestre(
            "Reporte de Equipos",
            ["ID", "Equipo", "Curso"],
            datos_agrupados
        )

        try:
            return send_file(
                ruta,
                as_attachment=True,
                download_name="reporte_equipos.pdf",
                mimetype="application/pdf"
            )
        finally:
            os.unlink(ruta)

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
            
