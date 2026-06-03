from flask import Blueprint, jsonify
from database.db import get_connection

dashboard_bp = Blueprint(
    "dashboard",
    __name__
)

@dashboard_bp.route("/api/dashboard/resumen")
def resumen_dashboard():

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