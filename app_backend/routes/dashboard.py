from flask import Blueprint, jsonify, request
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

        curso_param = request.args.get("curso")

        # Si no vino un curso seleccionado, buscar el curso asociado al profesor
        if curso_param == "todos":
            curso_id = None
            usar_todos = True

        elif curso_param:
            curso_id = int(curso_param)
            usar_todos = False

        else:
            # Primera carga
            usar_todos = False

            cur.execute("""
                SELECT pc.id_curso
                FROM profesor_curso pc
                JOIN profesores p
                    ON p.id_profesor = pc.id_profesor
                WHERE p.id_usuario = %s
                LIMIT 1
            """, (current_user["id"],))

            resultado = cur.fetchone()

            curso_id = resultado[0] if resultado else None

            if resultado is None:
                usar_todos = True

        # -------------------------
        # Modo todos los cursos
        # -------------------------

        if usar_todos:

            curso_actual = "Todos"

            cur.execute(
                "SELECT COUNT(*) FROM alumnos"
            )
            total_alumnos = cur.fetchone()[0]

            cur.execute(
                "SELECT COUNT(*) FROM evaluaciones"
            )
            total_evaluaciones = cur.fetchone()[0]

            cur.execute("""
                SELECT COUNT(*)
                FROM alumnos
                WHERE estado = 'activo'
            """)
            total_alumnos_activos = cur.fetchone()[0]

            cur.execute("""
                SELECT COUNT(*)
                FROM alumnos
                WHERE estado = 'inactivo'
            """)
            total_alumnos_inactivos = cur.fetchone()[0]

            cur.execute(
                "SELECT COUNT(*) FROM equipos"
            )
            total_equipos = cur.fetchone()[0]

        # -------------------------
        # Modo filtrado por curso
        # -------------------------

        else:

            cur.execute("""
                SELECT anio, cuatrimestre
                FROM cursos
                WHERE id_curso = %s
            """, (curso_id,))

            curso = cur.fetchone()

            if curso:
                curso_actual = f"{curso[0]} - {curso[1]}C"
            else:
                curso_actual = "Desconocido"

            cur.execute("""
                SELECT COUNT(*)
                FROM alumnos
                WHERE curso = %s
            """, (curso_id,))
            total_alumnos = cur.fetchone()[0]

            cur.execute("""
                SELECT COUNT(*)
                FROM evaluaciones
                WHERE id_curso = %s
            """, (curso_id,))
            total_evaluaciones = cur.fetchone()[0]

            cur.execute("""
                SELECT COUNT(*)
                FROM alumnos
                WHERE curso = %s
                AND estado = 'activo'
            """, (curso_id,))
            total_alumnos_activos = cur.fetchone()[0]

            cur.execute("""
                SELECT COUNT(*)
                FROM alumnos
                WHERE curso = %s
                AND estado = 'inactivo'
            """, (curso_id,))
            total_alumnos_inactivos = cur.fetchone()[0]

            cur.execute("""
                SELECT COUNT(*)
                FROM equipos
                WHERE id_curso = %s
            """, (curso_id,))
            total_equipos = cur.fetchone()[0]

        return jsonify({
            "alumnos": total_alumnos,
            "evaluaciones": total_evaluaciones,
            "curso_actual": curso_actual,
            "alumnos_activos": total_alumnos_activos,
            "alumnos_inactivos": total_alumnos_inactivos,
            "equipos": total_equipos
        })

    finally:
        cur.close()
        conn.close()


