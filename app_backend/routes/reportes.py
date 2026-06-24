import os
from flask import Blueprint, jsonify, send_file, request
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

        id_curso = request.args.get("id_curso", type=int)

        if id_curso:

            cur.execute("""
                SELECT
                    a.legajo,
                    CONCAT(a.nombre, ' ', a.apellido),
                    a.estado,
                    a.email,
                    ROUND(AVG(n.calificacion), 2) AS promedio,
                    a.anio,
                    a.cuatrimestre
                FROM alumnos a
                LEFT JOIN notas n
                    ON a.legajo = n.legajo_alumno
                WHERE a.curso = %s
                GROUP BY
                    a.legajo,
                    a.nombre,
                    a.apellido,
                    a.estado,
                    a.email,
                    a.anio,
                    a.cuatrimestre
                ORDER BY
                    a.anio,
                    a.cuatrimestre,
                    a.apellido,
                    a.nombre
            """, (id_curso,))
        
        
        else:
        
            cur.execute("""
                SELECT
                    a.legajo,
                    CONCAT(a.nombre, ' ', a.apellido),
                    a.estado,
                    a.email,
                    ROUND(AVG(n.calificacion), 2) AS promedio,
                    a.anio,
                    a.cuatrimestre
                FROM alumnos a
                LEFT JOIN notas n
                    ON a.legajo = n.legajo_alumno
                GROUP BY
                    a.legajo,
                    a.nombre,
                    a.apellido,
                    a.estado,
                    a.email,
                    a.anio,
                    a.cuatrimestre
                ORDER BY
                    a.anio,
                    a.cuatrimestre,
                    a.apellido,
                    a.nombre
            """)

        resultado = cur.fetchall()

        datos_agrupados = {}

        for fila in resultado:

            anio = fila[5]
            cuatrimestre = fila[6]

            clave = (anio, cuatrimestre)

            if clave not in datos_agrupados:
                datos_agrupados[clave] = []

            datos_agrupados[clave].append(
                (
                    fila[0],
                    fila[1],
                    fila[2],
                    fila[3],
                    round(float(fila[4]), 2) if fila[4] is not None else "-"
                )
            )

        ruta = crear_pdf_por_cuatrimestre(
            "Reporte de Alumnos",
            ["Legajo", "Nombre", "Estado", "Email", "Promedio"],
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

        id_curso = request.args.get("id_curso", type=int)

        if id_curso:

            cur.execute("""
                SELECT
                    anio,
                    cuatrimestre
                FROM cursos
                WHERE id_curso = %s
            """, (id_curso,))
        
        else:
        
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
                FROM alumnos a
                INNER JOIN cursos c
                    ON a.curso = c.id_curso
                WHERE c.anio = %s
                AND c.cuatrimestre = %s
            """, (anio, cuatrimestre))
            
            total_alumnos = cur.fetchone()[0]
            
            filas.append(
                ("Total de alumnos", total_alumnos)
            )

            cur.execute("""
                SELECT COUNT(*)
                FROM alumnos a
                INNER JOIN cursos c
                    ON a.curso = c.id_curso
                WHERE c.anio = %s
                AND c.cuatrimestre = %s
                AND a.estado = 'inactivo'
            """, (anio, cuatrimestre))
            
            inactivos = cur.fetchone()[0]
            
            porcentaje_inactivos = (
                round((inactivos / total_alumnos) * 100, 2)
                if total_alumnos > 0 else 0
            )
            
            filas.append(
                (
                    "Alumnos inactivos",
                    f"{inactivos} ({porcentaje_inactivos}%)"
                )
            )

            cur.execute("""
                SELECT COUNT(DISTINCT n.legajo_alumno)
                FROM notas n
                INNER JOIN alumnos a
                    ON n.legajo_alumno = a.legajo
                INNER JOIN cursos c
                    ON a.curso = c.id_curso
                WHERE c.anio = %s
                AND c.cuatrimestre = %s
            """, (anio, cuatrimestre))
            
            alumnos_con_nota = cur.fetchone()[0]

            cur.execute("""
                SELECT COUNT(DISTINCT n.legajo_alumno)
                FROM notas n
                INNER JOIN alumnos a
                    ON n.legajo_alumno = a.legajo
                INNER JOIN cursos c
                    ON a.curso = c.id_curso
                WHERE c.anio = %s
                AND c.cuatrimestre = %s
                AND n.calificacion >= 4
            """, (anio, cuatrimestre))
            
            aprobados = cur.fetchone()[0]

            porcentaje_aprobados = (
                round((aprobados / alumnos_con_nota) * 100, 2)
                if alumnos_con_nota > 0 else 0
            )
            
            filas.append(
                (
                    "Alumnos aprobados",
                    f"{aprobados} ({porcentaje_aprobados}%)"
                )
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
    cur_miembros = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        id_curso = request.args.get("id_curso", type=int)

        if id_curso:

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
                WHERE e.id_curso = %s
                ORDER BY
                    c.anio,
                    c.cuatrimestre,
                    e.nombre_equipo
            """, (id_curso,))
        
        else:
        
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

        cur_miembros = conn.cursor()

        for fila in resultado:
            id_equipo = fila[0]
            nombre_equipo = fila[1]
            curso = fila[2]
            anio = fila[3]
            cuatrimestre = fila[4]
            clave = (anio, cuatrimestre)
        
            if clave not in datos_agrupados:
                datos_agrupados[clave] = []
        
            datos_agrupados[clave].append(
                (id_equipo, nombre_equipo, curso)
            )

            cur_miembros.execute("""
                SELECT legajo_alumno
                FROM miembros_equipo
                WHERE id_equipo = %s
                ORDER BY legajo_alumno
            """, (id_equipo,))
            
            integrantes = cur_miembros.fetchall()
        
            for integrante in integrantes:
                datos_agrupados[clave].append(
                    (
                        "Integrante",
                        integrante[0],
                        ""
                    )
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
        if cur_miembros:
            cur_miembros.close()
        if cur:
            cur.close()
        if conn:
            conn.close()
            
