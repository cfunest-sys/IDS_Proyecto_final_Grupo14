from database.db import get_connection
from flask import jsonify


def get_profesor_by_email(email):
    # JOIN entre usuarios y profesores
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """SELECT p.id_profesor as id, p.nombre, u.email, u.contrasenia as password, u.rol
           FROM profesores p
           INNER JOIN usuarios u ON p.id_usuario = u.id_usuario
           WHERE u.email = %s""",
            (email,),
        )
        profesor = cursor.fetchone()
        return profesor

    except Exception as e:
        print(f"Error al obtener profesor: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_alumno(nombre, contrasenia):
    """Obtiene un alumno por su nombre y contraseña."""
    if not nombre or not contrasenia:
        raise ValueError("Todos los campos son obligatorios")

    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        query = """
            SELECT *
            FROM usuarios u
            INNER JOIN alumnos a
                ON u.id_usuario = a.id_usuario
            WHERE u.email = %s
            AND u.contrasenia = %s
            """
        cur.execute(query, (nombre, contrasenia))
        return cur.fetchone()
    except Exception as e:
        raise Exception(f"Error obteniendo alumno: {e}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def get_alumnos():
    """Obtiene todos los alumnos."""
    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        query = """
            SELECT *
            FROM usuarios u
            INNER JOIN alumnos a
                ON u.id_usuario = a.id_usuario
        """

        cur.execute(query)
        return cur.fetchall()

    except Exception as e:
        raise Exception(f"Error obteniendo alumnos: {e}")

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def cargar_alumno(nombre, contrasenia, email, created_at, estado, rol):
    """Carga un nuevo alumno en la base de datos."""
    if not nombre or not contrasenia or not email or not created_at or estado is None or not rol:
        raise ValueError("Todos los campos son obligatorios")

    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        query = """
            INSERT INTO usuarios (email, contrasenia, created_at, rol)
            VALUES (%s, %s, %s, %s)
            """
        cur.execute(query, (email, contrasenia, created_at, rol))
        id_usuario = cur.lastrowid

        query_alumno = """
            INSERT INTO alumnos (id_usuario, nombre, estado)
            VALUES (%s, %s, %s)
            """
        cur.execute(query_alumno, (id_usuario, nombre, estado))

        return id_usuario
    except Exception as e:
        raise Exception(f"Error cargando alumno: {e}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def actualizar_alumno(legajo, nombre, contrasenia, email, created_at, estado, rol):
    """Actualiza un alumno existente en la base de datos."""
    if not legajo or not nombre or not contrasenia or not email or not created_at or estado is None or not rol:
        raise ValueError("Todos los campos son obligatorios")

    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        query = """
            UPDATE usuarios u
            INNER JOIN alumnos a ON u.id_usuario = a.id_usuario
            SET u.email = %s, u.contrasenia = %s, u.created_at = %s, u.rol = %s,
                a.nombre = %s, a.estado = %s
            WHERE a.legajo = %s
            """
        cur.execute(query, (email, contrasenia, created_at, rol, nombre, estado, legajo))
        return cur.rowcount > 0
    except Exception as e:
        raise Exception(f"Error actualizando alumno: {e}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def eliminar_alumno(legajo):
    """Elimina un alumno de la base de datos."""
    if not legajo:
        raise ValueError("El legajo es obligatorio")

    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        query = """
            DELETE u, a
            FROM usuarios u
            INNER JOIN alumnos a ON u.id_usuario = a.id_usuario
            WHERE a.legajo = %s
            """
        cur.execute(query, (legajo,))
        return cur.rowcount > 0
    except Exception as e:
        raise Exception(f"Error eliminando alumno: {e}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def get_profesor(nombre, contrasenia):
    """Obtiene un profesor por su nombre y contraseña."""
    if not nombre or not contrasenia:
        raise ValueError("Todos los campos son obligatorios")

    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        query = """
            SELECT *
            FROM usuarios u
            INNER JOIN profesores p
                ON u.id_usuario = p.id_usuario
            WHERE u.email = %s
            AND u.contrasenia = %s
            """
        cur.execute(query, (nombre, contrasenia))
        return cur.fetchone()
    except Exception as e:
        raise Exception(f"Error obteniendo profesor: {e}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def get_all_users():
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users")
        users = cur.fetchall()
    except Exception as e:
        raise Exception(f"Error obteniendo usuarios: {e}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
    return users


def get_evaluacion(id):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM evaluaciones WHERE id = %s", (id))
        evaluacion = cursor.fetchone()
        cursor.close()
        connection.close()
        return evaluacion
    except Exception as e:
        print(e)
        return jsonify({"error": "Error interno del servidor"}), 500


def crear_evaluacion(nombre, tipo, fecha, curso_id):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        query = """INSERT INTO evaluaciones (nombre, tipo, fecha, curso_id) 
                VALUES (%s, %s, %s, %s)"""
        cursor.execute(query, (nombre, tipo, fecha, curso_id))
        evaluacion = cursor.fetchone()
        cursor.close()
        connection.close()
        return evaluacion
    except Exception as e:
        print(e)
        return jsonify({"error": "Error interno del servidor"}), 500


def cambiar_evaluacion(id, nombre, tipo, fecha, curso_id):
    try:
        connection = get_connection()
        cursor = connection.cursor()

        query_esta = """SELECT * FROM evaluaciones WHERE id = %s"""
        cursor.execute(query_esta, (id))
        esta = cursor.fetchall()
        if cursor.rowcount == 0:
            cursor.close()
            connection.close()
            return jsonify({"error": "No existe ese id"})
        query_insertar = """UPDATE evaluaciones
            SET nombre = %s,
                tipo = %s,
                fecha = %s,
                curso_id = %s
            WHERE id = %s"""
        cursor.execute(query_insertar, (nombre, tipo, fecha, curso_id, id))
        evaluacion = cursor.fetchone()
        cursor.close()
        connection.close()
        return evaluacion
    except Exception as e:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
        print(e)
        return jsonify({"error": "Error interno del servidor"}), 500


def eliminar_evaluacion(id):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        query_esta = """SELECT * FROM evaluaciones WHERE id = %s"""
        cursor.execute(query_esta, (id))
        esta = cursor.fetchall()
        if cursor.rowcount == 0:
            cursor.close()
            connection.close()
            return jsonify({"error": "No existe ese id"}), 404
        query = """DELETE FROM evaluaciones WHERE id = %s"""
        cursor.execute(query, (id))
        connection.commit()
        query = """SELECT * FROM evaluaciones WHERE id = %s"""
        cursor.execute(query, (id))
        resultado = cursor.fetchall()
        filas = cursor.rowcount
        cursor.close()
        connection.close()
        if filas != 0:
            return False, 400
        return True, 200
    except Exception as e:
        print(e)
        return jsonify({"error": "Error interno del servidor"}), 500

def get_user_by_id(user_id):
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        query = "SELECT id_usuario, email, rol FROM usuarios WHERE id_usuario = %s"
        cur.execute(query, (user_id,))

        user = cur.fetchone()
        return user

    except Exception as e:
        print(f"Error en MySQL get_user_by_id: {e}")
        return None
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def get_alumno_por_usuario_id(usuario_id):
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT legajo, nombre, id_usuario FROM alumnos WHERE id_usuario = %s", (usuario_id,))
        return cur.fetchone()
    except Exception as e:
        print(f"Error obteniendo alumno por usuario: {e}")
        return None
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def get_nota(alumno_id, evaluacion_id):
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT n.*, a.nombre AS alumno, e.nombre AS evaluacion
            FROM notas n
            JOIN alumnos a ON a.legajo = n.alumno_id
            JOIN evaluaciones e ON e.id_evaluacion = n.evaluacion_id
            WHERE n.alumno_id = %s AND n.evaluacion_id = %s
            """,
            (alumno_id, evaluacion_id),
        )
        return cur.fetchone()
    except Exception as e:
        print(f"Error obteniendo nota: {e}")
        return None
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def upsert_nota(alumno_id, evaluacion_id, calificacion):
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id FROM notas WHERE alumno_id = %s AND evaluacion_id = %s", (alumno_id, evaluacion_id))
        existing = cur.fetchone()

        if existing:
            cur.execute(
                "UPDATE notas SET calificacion = %s, fecha = CURDATE() WHERE id = %s",
                (calificacion, existing["id"]),
            )
            accion = "actualizada"
            nota_id = existing["id"]
        else:
            cur.execute(
                "INSERT INTO notas (alumno_id, evaluacion_id, calificacion, fecha) VALUES (%s, %s, %s, CURDATE())",
                (alumno_id, evaluacion_id, calificacion),
            )
            nota_id = cur.lastrowid
            accion = "creada"

        conn.commit()
        return {"id": nota_id, "accion": accion, "alumno_id": alumno_id, "evaluacion_id": evaluacion_id, "calificacion": calificacion}
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error guardando nota: {e}")
        raise
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def get_notas(alumno_id=None, evaluacion_id=None, page=1, per_page=10):
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        condiciones = []
        parametros = []
        if alumno_id is not None:
            condiciones.append("n.alumno_id = %s")
            parametros.append(alumno_id)
        if evaluacion_id is not None:
            condiciones.append("n.evaluacion_id = %s")
            parametros.append(evaluacion_id)

        where_clause = " WHERE " + " AND ".join(condiciones) if condiciones else ""
        count_query = "SELECT COUNT(*) AS total FROM notas n" + where_clause
        cur.execute(count_query, parametros)
        total = cur.fetchone()["total"]

        page = max(1, int(page))
        per_page = max(1, int(per_page))
        offset = (page - 1) * per_page

        query = """
            SELECT n.id, n.alumno_id, n.evaluacion_id, n.calificacion, n.fecha,
                   a.nombre AS alumno, e.nombre AS evaluacion
            FROM notas n
            JOIN alumnos a ON a.legajo = n.alumno_id
            JOIN evaluaciones e ON e.id_evaluacion = n.evaluacion_id
        """ + where_clause + " ORDER BY n.fecha DESC, n.id DESC LIMIT %s OFFSET %s"
        cur.execute(query, parametros + [per_page, offset])
        items = cur.fetchall()

        pages = (total + per_page - 1) // per_page if total else 0
        return {"items": items, "page": page, "per_page": per_page, "total": total, "pages": pages}
    except Exception as e:
        print(f"Error listando notas: {e}")
        raise
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def get_equipos_filtrados(id_equipo=None, nombre_equipo=None, id_curso=None):
    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        query = "SELECT * FROM equipos"
        parametros = []
        condiciones = []

        if id_equipo:
            condiciones.append("id_equipo = %s")
            parametros.append(id_equipo)

        if nombre_equipo:
            condiciones.append("nombre_equipo = %s")
            parametros.append(nombre_equipo)  

        if id_curso:
            condiciones.append("id_curso = %s")
            parametros.append(id_curso)
            
        if condiciones:
            query += " WHERE " + " AND ".join(condiciones)

        cursor.execute(query, parametros)
        equipos = cursor.fetchall()

        return equipos
    
    except Exception as e:
        print(f"Error en la obtención del equipo: {e}")
        raise e
    
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


def get_equipo_id(id_equipo):
    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("SELECT * FROM equipos WHERE id_equipo = %s", (id_equipo,))
        equipo = cursor.fetchone()

        return equipo

    except Exception as e:
        print(f"Error en la obtención del equipo: {e}")
        raise e

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


def insertar_equipo(nombre_equipo, id_curso):
    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)
        
        cursor.execute("INSERT INTO equipos (nombre_equipo, id_curso) VALUES (%s, %s)", (nombre_equipo, id_curso))
        conexion.commit()
    
    except Exception as e:
        print(f"Error en la creación del equipo {e}")
        raise e

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


def actualizar_equipo(id_equipo, nombre_equipo, id_curso):
    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        query_update = "UPDATE equipos SET nombre_equipo = %s, id_curso = %s WHERE id_equipo = %s"
        cursor.execute(query_update, (nombre_equipo, id_curso, id_equipo))
        conexion.commit()

    except Exception as e:
        if conexion:
            conexion.rollback()
        print(f"Error en la actualización del equipo {e}")
        raise e

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


def delete_equipo(id_equipo):
    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("DELETE FROM equipos WHERE id_equipo = %s", (id_equipo,))
        conexion.commit()

    except Exception as e:
        if conexion:
            conexion.rollback()
        print(f"Error al intentar eliminar el equipo {e}")
        raise e

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


def crear_alumno(alumno):

    conn = None
    cur = None

    try:

        conn = get_connection()
        cur = conn.cursor()

        query_usuario = """
            INSERT INTO usuarios (
                email,
                contrasenia,
                rol
            )
            VALUES (%s, %s, %s)
        """

        cur.execute(
            query_usuario,
            (
                alumno["email"],
                alumno["password"],
                "alumno"
            )
        )

        id_usuario = cur.lastrowid

        query_alumno = """
            INSERT INTO alumnos (
                nombre,
                estado,
                id_usuario
            )
            VALUES (%s, %s, %s)
        """

        cur.execute(
            query_alumno,
            (
                alumno["nombre"],
                "activo",
                id_usuario
            )
        )

        conn.commit()

        return cur.lastrowid

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

            
def get_miembros_equipo(id_miembro=None, id_equipo=None, legajo_alumno=None):
    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        query = "SELECT * FROM miembros_equipo"
        parametros = []
        condiciones = []

        if id_miembro:
            condiciones.append("id_miembro = %s")
            parametros.append(id_miembro)

        if id_equipo:
            condiciones.append("id_equipo = %s")
            parametros.append(id_equipo)  

        if legajo_alumno:
            condiciones.append("legajo_alumno = %s")
            parametros.append(legajo_alumno)

        if condiciones:
            query += " WHERE " + " AND ".join(condiciones)

        cursor.execute(query, parametros)
        equipo = cursor.fetchall()

        return equipo
    
    except Exception as e:
        print(f"Error en la obtención del equipo: {e}")
        raise e
    
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()
        

def insertar_miembro(id_equipo, legajo_alumno):
    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)
        
        cursor.execute("INSERT INTO miembros_equipo (id_equipo, legajo_alumno) VALUES (%s, %s)", (id_equipo, legajo_alumno))
        conexion.commit()
    
    except Exception as e:
        print(f"Error al agregar un alumno al equipo {e}")
        raise e

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


def delete_miembro(id_miembro):
    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("DELETE FROM miembros_equipo WHERE id_miembro = %s", (id_miembro,))
        conexion.commit()

    except Exception as e:
        if conexion:
            conexion.rollback()
        print(f"Error al intentar eliminar el miembro{e}")
        raise e

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()
