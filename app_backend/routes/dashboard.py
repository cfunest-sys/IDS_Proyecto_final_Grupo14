from flask import Blueprint, jsonify
from utils.auth import token_required, rol_required
from database.db import get_connection

dashboard_bp = Blueprint(
    "dashboard",
    __name__
)

@dashboard_bp.route("/api/dashboard/resumen")
@token_required
def resumen_dashboard(current_user):

    conn = get_connection()
    cur = conn.cursor()

    try:

        cur.execute(
            "SELECT COUNT(*) FROM alumnos"
        )
        total_alumnos = cur.fetchone()[0]

        cur.execute(
            "SELECT COUNT(*) FROM evaluaciones"
        )
        total_evaluaciones = cur.fetchone()[0]

        cur.execute(
            "SELECT COUNT(*) FROM cursos"
        )
        total_cursos = cur.fetchone()[0]

        cur.execute(
            "SELECT COUNT(*) FROM alumnos WHERE estado = 'activo'"
        )
        total_alumnos_activos = cur.fetchone()[0]

        cur.execute(
            "SELECT COUNT(*) FROM alumnos WHERE estado = 'inactivo'"
        )
        total_alumnos_inactivos = cur.fetchone()[0]

        cur.execute(
            "SELECT COUNT(*) FROM equipos"
        )
        total_equipos = cur.fetchone()[0]

        return jsonify({
            "alumnos": total_alumnos,
            "evaluaciones": total_evaluaciones,
            "cursos": total_cursos,
            "alumnos_activos": total_alumnos_activos,
            "alumnos_inactivos": total_alumnos_inactivos,
            "equipos": total_equipos
        })

    finally:
        cur.close()
        conn.close()


@dashboard_bp.route("/api/dashboard/alumno/<int:legajo>")
@token_required
def dashboard_alumno(current_user, legajo):
    conn = get_connection()
    cur = conn.cursor()

    try:

        # DATOS PERSONALES
        cur.execute("""
            SELECT
                a.nombre,
                a.apellido,
                a.legajo,
                u.email
            FROM alumnos a
            INNER JOIN usuarios u
                ON a.id_usuario = u.id_usuario
            WHERE a.legajo = %s
        """, (legajo,))

        alumno = cur.fetchone()

        if not alumno:
            return jsonify({
                "error": "Alumno no encontrado"
            }), 404


        # NOTAS
        cur.execute("""
            SELECT COUNT(*)
            FROM notas
            WHERE legajo_alumno = %s
        """, (legajo,))

        cantidad_notas = cur.fetchone()[0]


        # ASISTENCIAS
        cur.execute("""
            SELECT COUNT(*)
            FROM asistencia
            WHERE alumno_legajo = %s
        """, (legajo,))

        total_asistencias = cur.fetchone()[0]


        # EQUIPOS
        cur.execute("""
            SELECT COUNT(*)
            FROM miembros_equipo
            WHERE legajo_alumno = %s
        """, (legajo,))

        total_equipos = cur.fetchone()[0]


        # EVALUACIONES PENDIENTES
        cur.execute("""
            SELECT COUNT(*)
            FROM evaluaciones
            WHERE fecha >= CURDATE()
        """)

        proximas = cur.fetchone()[0]


        return jsonify({

            "nombre": alumno[0],
            "apellido": alumno[1],
            "legajo": alumno[2],
            "email": alumno[3],

            "notas": cantidad_notas,
            "asistencias": total_asistencias,
            "equipos": total_equipos,
            "proximas_evaluaciones": proximas

        })

    finally:
        cur.close()
        conn.close()

