from werkzeug.security import generate_password_hash

from database.db import get_connection
from flask import jsonify

# def crear_base_datos():
#     connection = get_connection()
#     cursor = connection.cursor()
#     f = open("data/db_init.sql", 'r')
#     lineas = f.readlines()
#     f.close()
#     for linea in lineas:
#         if (linea != "" and linea != None):
#             cursor.execute(linea)
#             connection.commit()
#     cursor.close()
#     connection.close()

def get_usuario_by_email(email):

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT
                id_usuario,
                email,
                contrasenia AS password,
                rol
            FROM usuarios
            WHERE email = %s
        """

        cursor.execute(query, (email,))
        return cursor.fetchone()

    except Exception as e:
        print(f"Error al obtener usuario: {e}")
        return None

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def get_user_profile(usuario):

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        if usuario["rol"] == "profesor":

            query = """
                SELECT
                    p.id_profesor,
                    p.nombre,
                    p.departamento
                FROM profesores p
                WHERE p.id_usuario = %s
            """

        elif usuario["rol"] == "alumno":

            query = """
                SELECT
                    a.id_alumno,
                    a.nombre,
                    a.legajo
                FROM alumnos a
                WHERE a.id_usuario = %s
            """

        else:
            return None

        cursor.execute(query, (usuario["id_usuario"],))
        return cursor.fetchone()

    finally:
        cursor.close()
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
        if cursor.rowcount == 0:
            return evaluacion, 204
        return evaluacion, 200
    except Exception as e:
        print(e)
        return jsonify({"error": "Error interno del servidor"}), 500

def get_evaluacion_por_curso(curso_id):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM evaluaciones WHERE id_curso = %s", (curso_id,))
        # cursor.execute("SELECT * FROM evaluaciones")
        evaluacion = cursor.fetchall()
        cursor.close()
        connection.close()
        return evaluacion
    except Exception as e:
        print(e)
        return jsonify({"error": "Error interno del servidor"}), 500

def get_evaluacion_profesor(id_profesor):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        query = """select evaluaciones.* from evaluaciones  
                   inner join profesor_curso pc on pc.id_curso = evaluaciones.id_curso 
                   where pc.id_profesor=%s;"""
        cursor.execute(query, (id_profesor,))
        evaluacion = cursor.fetchall()
        cursor.close()
        connection.close()
        return evaluacion
    except Exception as e:
        print(e)
        return jsonify({"error": "Error interno del servidor"}), 500

# select evaluaciones.* from evaluaciones  
# inner join profesor_curso pc on pc.id_curso = evaluaciones.id_curso 
# where pc.id_profesor=2;

def get_evaluacion_todas():
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM evaluaciones")
        evaluacion = cursor.fetchall()
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


def crear_profesor(profesor):

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

        password_hash = generate_password_hash(profesor["password"])

        cur.execute(
            query_usuario,
            (
                profesor["email"],
                password_hash,
                "profesor"
            )
        )

        id_usuario = cur.lastrowid

        query_profesor = """
            INSERT INTO profesores (
                nombre,
                departamento,
                id_usuario
            )
            VALUES (%s, %s, %s)
        """

        cur.execute(
            query_profesor,
            (
                profesor["nombre"],
                profesor["departamento"],
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

def get_notas_filtradas(rol, usuario_id, legajo_alumno=None, id_evaluacion=None, id_curso=None, limit=10, offset=0):
    """Obtiene el listado de notas aplicando paginación y seguridad estricta por rol."""
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        query = """
            SELECT a.nombre AS alumno, e.nombre AS evaluacion, n.calificacion, n.fecha
            FROM notas n
            INNER JOIN alumnos a ON n.legajo_alumno = a.legajo
            INNER JOIN evaluaciones e ON n.id_evaluacion = e.id_evaluacion
            INNER JOIN cursos c ON e.id_curso = c.id_curso
        """
        condiciones = []
        parametros = []

        # alumno: Solo ve sus propias notas
        if rol == "alumno":
            condiciones.append("a.id_usuario = %s")
            parametros.append(usuario_id)

        # profesor: Solo ve notas de los cursos que dicta
        elif rol == "profesor":
            query += """
                INNER JOIN profesor_curso pc ON c.id_curso = pc.id_curso
                INNER JOIN profesores p ON pc.id_profesor = p.id_profesor
            """
            condiciones.append("p.id_usuario = %s")
            parametros.append(usuario_id)

        # Filtros opcionales de búsqueda
        if legajo_alumno:
            condiciones.append("n.legajo_alumno = %s")
            parametros.append(legajo_alumno)

        if id_evaluacion:
            condiciones.append("n.id_evaluacion = %s")
            parametros.append(id_evaluacion)

        if id_curso:
            condiciones.append("e.id_curso = %s")
            parametros.append(id_curso)

        if condiciones:
            query += " WHERE " + " AND ".join(condiciones)

        query += " LIMIT %s OFFSET %s"
        parametros.extend([limit, offset])

        cur.execute(query, parametros)
        return cur.fetchall()

    except Exception as e:
        print(f"Error en queries.get_notas_filtradas: {e}")
        raise e
    finally:
        if cur: cur.close()
        if conn: conn.close()


def get_promedio_notas(rol, usuario_id, legajo_alumno=None, id_evaluacion=None, id_curso=None):
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        query = """
            SELECT AVG(n.calificacion) AS promedio
            FROM notas n
            INNER JOIN alumnos a ON n.legajo_alumno = a.legajo
            INNER JOIN evaluaciones e ON n.id_evaluacion = e.id_evaluacion
            INNER JOIN cursos c ON e.id_curso = c.id_curso
        """
        condiciones = []
        parametros = []

        if rol == "alumno":
            condiciones.append("a.id_usuario = %s")
            parametros.append(usuario_id)
            
        elif rol == "profesor":
            query += """
                INNER JOIN profesor_curso pc ON c.id_curso = pc.id_curso
                INNER JOIN profesores p ON pc.id_profesor = p.id_profesor
            """
            condiciones.append("p.id_usuario = %s")
            parametros.append(usuario_id)

        if legajo_alumno:
            condiciones.append("n.legajo_alumno = %s")
            parametros.append(legajo_alumno)

        if id_evaluacion:
            condiciones.append("n.id_evaluacion = %s")
            parametros.append(id_evaluacion)

        if id_curso:
            condiciones.append("e.id_curso = %s")
            parametros.append(id_curso)

        if condiciones:
            query += " WHERE " + " AND ".join(condiciones)

        cur.execute(query, parametros)
        resultado = cur.fetchone()
        
        if resultado and resultado['promedio'] is not None:
            return round(float(resultado['promedio']), 2)
        return 0.0

    except Exception as e:
        print(f"Error en queries.get_promedio_notas: {e}")
        raise e
    finally:
        if cur: cur.close()
        if conn: conn.close()


def verificar_alumno_evaluacion(legajo_alumno, id_evaluacion):
    # Verifica la existencia del alumno y la evaluación antes de insertar o actualizar una nota
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        
        cur.execute("SELECT legajo FROM alumnos WHERE legajo = %s", (legajo_alumno,))
        alumno = cur.fetchone()
        
        cur.execute("SELECT id_evaluacion FROM evaluaciones WHERE id_evaluacion = %s", (id_evaluacion,))
        evaluacion = cur.fetchone()
        
        return (alumno is not None) and (evaluacion is not None)
    except Exception as e:
        print(f"Error en verificar_alumno_evaluacion: {e}")
        return False
    finally:
        if cur: cur.close()
        if conn: conn.close()


def guardar_actualizar_nota(legajo_alumno, id_evaluacion, calificacion):
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        query = """
            INSERT INTO notas (legajo_alumno, id_evaluacion, calificacion, fecha)
            VALUES (%s, %s, %s, CURDATE())
            ON DUPLICATE KEY UPDATE
                calificacion = VALUES(calificacion),
                fecha = CURDATE()
        """
        cur.execute(query, (legajo_alumno, id_evaluacion, calificacion))
        conn.commit()

        cur.execute("""
            SELECT legajo_alumno, id_evaluacion, calificacion, fecha
            FROM notas
            WHERE legajo_alumno = %s AND id_evaluacion = %s
        """, (legajo_alumno, id_evaluacion))

        return cur.fetchone()

    except Exception as e:
        if conn: conn.rollback()
        print(f"Error guardar/actualizar nota: {e}")
        raise e
    finally:
        if cur: cur.close()
        if conn: conn.close()
        
def registrar_login(id_usuario, email, resultado, ip):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO logs_login
        (id_usuario, email, resultado, ip)
        VALUES (%s, %s, %s, %s)
        """,
        (id_usuario, email, resultado, ip)
    )

    conn.commit()
    cur.close()
    conn.close()
