from werkzeug.security import generate_password_hash

from utils.mail_service import enviar_mail_bienvenida
from database.db import get_connection
from flask import jsonify
import csv
import io
import traceback

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
            WHERE email = %s;
        """

        cursor.execute(query, (email,))
        usuario = cursor.fetchone()
        cursor.reset()
        return usuario

    except Exception as e:
        print(f"Error al obtener usuario: {e}")
        return None

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_user_profile(usuario):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        rol = usuario.get("rol", "")

        if rol == "profesor":
            query = """
                SELECT
                    p.id_profesor,
                    p.nombre,
                    p.departamento
                FROM profesores p
                WHERE p.id_usuario = %s
            """
        elif rol == "alumno":
            query = """
                SELECT
                    a.curso,
                    a.nombre,
                    a.legajo
                FROM alumnos a
                WHERE a.id_usuario = %s
            """
        else:
            return None

        cursor.execute(query, (usuario.get("id_usuario"),))
        return cursor.fetchone()

    except Exception as e:
        print(f"Error en get_user_profile: {e}")
        return None
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def crear_alumno(alumno_data):

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

        password_hash = generate_password_hash(alumno_data["password"])

        cur.execute(query_usuario, (alumno_data["email"], password_hash, "alumno"))

        id_usuario = cur.lastrowid

        query_alumno = """
            INSERT INTO alumnos (
                nombre,
                id_usuario
            )
            VALUES (%s, %s)
        """

        cur.execute(query_alumno, (alumno_data["nombre"], id_usuario))

        conn.commit()

        return cur.lastrowid

    finally:

        if cur:
            cur.close()

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
        cur.execute("SELECT * FROM usuarios")
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
        cursor.execute("SELECT * FROM evaluaciones WHERE id = %s", (id,))
        evaluacion = cursor.fetchone()
        rowcount = cursor.rowcount
        cursor.close()
        connection.close()
        if rowcount == 0:
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

def get_categorias_evaluacion_por_curso(id_curso):
    """
    Devuelve las categorías de evaluación que existen en un curso específico.
    Las categorías se derivan del campo 'tipo' de la tabla evaluaciones.
    """
    conn = None
    cur  = None
    try:
        conn = get_connection()
        cur  = conn.cursor()
        
        cur.execute("""
            SELECT DISTINCT LOWER(e.tipo) AS categoria
            FROM evaluaciones e
            WHERE e.id_curso = %s
            ORDER BY categoria
        """, (id_curso,))
        
        categorias = cur.fetchall()
        # Devuelve una lista: [('tp',), ('parcial',), ...] → ['tp', 'parcial', ...]
        return [cat[0] for cat in categorias]

    except Exception as e:
        print(f"Error en get_categorias_evaluacion_por_curso: {e}")
        return []
    finally:
        if cur: cur.close()
        if conn: conn.close()

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
        query = """INSERT INTO evaluaciones (nombre, tipo, fecha, id_curso) 
                VALUES (%s, %s, %s, %s)"""
        cursor.execute(query, (nombre, tipo, fecha, curso_id))
        connection.commit()
        evaluacion = cursor.lastrowid
        cursor.close()
        connection.close()
        return jsonify({"id": evaluacion}), 201
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Error interno del servidor"}), 500


def cambiar_evaluacion(id, nombre, tipo, fecha, curso_id):
    try:
        connection = get_connection()
        cursor = connection.cursor()

        query_esta = """SELECT * FROM evaluaciones WHERE id_evaluacion = %s"""
        cursor.execute(query_esta, (id,))
        esta = cursor.fetchall()
        if cursor.rowcount == 0:
            cursor.close()
            connection.close()
            return jsonify({"error": "No existe ese id"}), 404
        query_insertar = """UPDATE evaluaciones
            SET nombre = %s,
                tipo = %s,
                fecha = %s,
                id_curso = %s
            WHERE id_evaluacion = %s"""
        cursor.execute(query_insertar, (nombre, tipo, fecha, curso_id, id))
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({"message": "Evaluación actualizada"}), 200
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
        query_esta = """SELECT * FROM evaluaciones WHERE id_evaluacion = %s"""
        cursor.execute(query_esta, (id,))
        esta = cursor.fetchall()
        if cursor.rowcount == 0:
            cursor.close()
            connection.close()
            return jsonify({"error": "No existe ese id"}), 404
        query = """DELETE FROM evaluaciones WHERE id_evaluacion = %s"""
        cursor.execute(query, (id,))
        connection.commit()
        query = """SELECT * FROM evaluaciones WHERE id_evaluacion = %s"""
        cursor.execute(query, (id,))
        resultado = cursor.fetchall()
        filas = cursor.rowcount
        cursor.close()
        connection.close()
        if filas != 0:
            return False
        return True
    except Exception as e:
        print(e)
        return jsonify({"error": "Error interno del servidor"}), 500


def get_equipos_filtrados(id_equipo=None, nombre_equipo=None, id_curso=None, pag = None, por_pag = None):
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
            condiciones.append("nombre_equipo LIKE %s")
            parametros.append(f"%{nombre_equipo}%")

        if id_curso:
            condiciones.append("id_curso = %s")
            parametros.append(id_curso)

        if condiciones:
            query += " WHERE " + " AND ".join(condiciones)

        if pag and por_pag:
            offset = (pag - 1) * por_pag
            query += " LIMIT %s OFFSET %s"
            parametros.append(por_pag)
            parametros.append(offset)

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

        cur.execute(query_usuario, (profesor["email"], password_hash, "profesor"))

        id_usuario = cur.lastrowid

        query_profesor = """
            INSERT INTO profesores (
                nombre,
                departamento,
                id_usuario
            )
            VALUES (%s, %s, %s)
        """

        cur.execute(query_profesor, (profesor["nombre"], profesor["departamento"], id_usuario))

        conn.commit()
        print(profesor)
        enviar_mail_bienvenida(profesor["email"], profesor["nombre"], profesor["password"])

        return cur.lastrowid

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

def existe_usuario_por_email(email):

    conn = None
    cur = None

    try:

        conn = get_connection()
        cur = conn.cursor()

        query_usuario = """
            SELECT id_usuario
            FROM usuarios
            WHERE email = %s
        """

        cur.execute(query_usuario, (email,))

        return cur.fetchone() is not None

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

        cursor.execute(
            "INSERT INTO miembros_equipo (id_equipo, legajo_alumno) VALUES (%s, %s)", (id_equipo, legajo_alumno)
        )
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


# <------------------- MATERIALES  ----------------------------->
CAMPOS_PERMITIDOS_UPDATE = {
    "titulo",
    "descripcion",
    "tema",
    "fecha_material",
    "estado",
    "orden_material",
    "es_libre",
    "tipo_material",
}
ESTADOS_VALIDOS = {"borrador", "publicado", "archivado", "programado"}


def insertar_material(
    id_curso,
    id_profesor,
    titulo,
    descripcion,
    tipo_material,
    tema=None,
    orden_material=0,
    archivo_ruta=None,
    es_externo=False,
    tipo_archivo=None,
    tamano_bytes=None,
    fecha_material=None,
    es_libre=False,
    estado="publicado",
):
    if estado not in ESTADOS_VALIDOS:
        raise ValueError(f"Estado inválido: {estado}")
    if not id_curso or not id_profesor or not titulo:
        raise ValueError("id_curso, id_profesor y titulo son obligatorios")
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO materiales
            (id_curso, id_profesor, titulo, descripcion, tipo_material,
             tema, orden_material, archivo_ruta, es_externo, tipo_archivo,
             tamano_bytes, fecha_material, es_libre, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(
            query,
            (
                id_curso,
                id_profesor,
                titulo,
                descripcion,
                tipo_material,
                tema,
                orden_material,
                archivo_ruta,
                es_externo,
                tipo_archivo,
                tamano_bytes,
                fecha_material,
                es_libre,
                estado,
            ),
        )
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        conn.rollback()
        traceback.print_exc()
        return None
    finally:
        conn.close()


def get_materiales(
    id_curso=None,
    id_profesor=None,
    tipo_material=None,
    tema=None,
    estado=None,
    es_libre=None,
    activo=True,
    pagina=1,
    limite=20,
    order_by="fecha_subida",
    order_dir="DESC",
):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        where_clauses = []
        params = []
        if activo is not None:
            where_clauses.append("m.activo = %s")
            params.append(activo)
        if id_curso:
            where_clauses.append("m.id_curso = %s")
            params.append(id_curso)
        if id_profesor:
            where_clauses.append("m.id_profesor = %s")
            params.append(id_profesor)
        if tipo_material:
            where_clauses.append("m.tipo_material = %s")
            params.append(tipo_material)
        if tema:
            where_clauses.append("m.tema = %s")
            params.append(tema)
        if estado:
            where_clauses.append("m.estado = %s")
            params.append(estado)
        if es_libre is not None:
            where_clauses.append("m.es_libre = %s")
            params.append(es_libre)
        order_by_whitelist = {"titulo", "tipo_material", "tema", "fecha_material", "estado", "fecha_subida"}
        sort_col = order_by if order_by in order_by_whitelist else "fecha_subida"
        sort_dir = "ASC" if order_dir.upper() == "ASC" else "DESC"
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        cursor.execute(f"SELECT COUNT(*) as total FROM materiales m WHERE {where_sql}", params)
        total = cursor.fetchone()["total"]
        offset = (pagina - 1) * limite
        query = f"""
            SELECT m.*, p.nombre AS profesor_nombre
            FROM materiales m
            LEFT JOIN profesores p ON m.id_profesor = p.id_profesor
            WHERE {where_sql}
            ORDER BY m.{sort_col} {sort_dir}
            LIMIT %s OFFSET %s
        """
        params.extend([limite, offset])
        cursor.execute(query, params)
        materiales = cursor.fetchall()
        return total, materiales
    except Exception as e:
        print(f"Error getting materiales: {e}")
        return 0, []
    finally:
        conn.close()


def get_estadisticas_materiales(id_curso=None, id_profesor=None):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        where_clauses = ["activo = TRUE"]
        params = []
        if id_curso:
            where_clauses.append("id_curso = %s")
            params.append(id_curso)
        if id_profesor:
            where_clauses.append("id_profesor = %s")
            params.append(id_profesor)
        where_sql = " AND ".join(where_clauses)
        cursor.execute(f"SELECT COUNT(*) as total FROM materiales WHERE {where_sql}", params)
        total = cursor.fetchone()["total"]
        cursor.execute(f"SELECT tipo_material, COUNT(*) as cant FROM materiales WHERE {where_sql} GROUP BY tipo_material", params)
        por_tipo = {r["tipo_material"]: r["cant"] for r in cursor.fetchall()}
        cursor.execute(f"SELECT estado, COUNT(*) as cant FROM materiales WHERE {where_sql} GROUP BY estado", params)
        por_estado = {r["estado"]: r["cant"] for r in cursor.fetchall()}
        return {
            "total": total,
            "pdfs": por_tipo.get("documento", 0) + por_tipo.get("apunte", 0) + por_tipo.get("guia", 0) + por_tipo.get("bibliografia", 0),
            "videos": por_tipo.get("video", 0),
            "imagenes": por_tipo.get("imagen", 0),
            "borradores": por_estado.get("borrador", 0),
            "publicados": por_estado.get("publicado", 0),
            "archivados": por_estado.get("archivado", 0),
            "programados": por_estado.get("programado", 0),
            "por_tipo": por_tipo,
            "por_estado": por_estado,
        }
    except Exception as e:
        print(f"Error getting estadisticas: {e}")
        return {"total": 0, "pdfs": 0, "videos": 0, "imagenes": 0, "borradores": 0, "publicados": 0, "archivados": 0, "programados": 0, "por_tipo": {}, "por_estado": {}}
    finally:
        conn.close()


def get_material(id_material):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT m.*, p.nombre AS profesor_nombre FROM materiales m LEFT JOIN profesores p ON m.id_profesor = p.id_profesor WHERE m.id_material = %s AND m.activo = TRUE", (id_material,))
        return cursor.fetchone()
    except Exception as e:
        print(f"Error getting material: {e}")
        return None
    finally:
        conn.close()


def actualizar_material(id_material, **kwargs):
    updates = {k: v for k, v in kwargs.items() if k in CAMPOS_PERMITIDOS_UPDATE}
    if not updates:
        return False
    if "estado" in updates and updates["estado"] not in ESTADOS_VALIDOS:
        raise ValueError(f"Estado inválido: {updates['estado']}")
    conn = get_connection()
    try:
        cursor = conn.cursor()
        set_clauses = [f"{campo} = %s" for campo in updates.keys()]
        set_sql = ", ".join(set_clauses)
        query = f"""
            UPDATE materiales
            SET {set_sql}, fecha_actualizacion = NOW()
            WHERE id_material = %s AND activo = TRUE
        """
        values = list(updates.values())
        values.append(id_material)
        cursor.execute(query, values)
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        print(f"Error updating material: {e}")
        return False
    finally:
        conn.close()


def eliminar_material(id_material):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE materiales SET activo = FALSE WHERE id_material = %s AND activo = TRUE", (id_material,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        print(f"Error deleting material: {e}")
        return False
    finally:
        conn.close()


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
        if cur:
            cur.close()
        if conn:
            conn.close()


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

        if resultado and resultado["promedio"] is not None:
            return round(float(resultado["promedio"]), 2)
        return 0.0

    except Exception as e:
        print(f"Error en queries.get_promedio_notas: {e}")
        raise e
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


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
        if cur:
            cur.close()
        if conn:
            conn.close()


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

        cur.execute(
            """
            SELECT legajo_alumno, id_evaluacion, calificacion, fecha
            FROM notas
            WHERE legajo_alumno = %s AND id_evaluacion = %s
        """,
            (legajo_alumno, id_evaluacion),
        )

        return cur.fetchone()

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error guardar/actualizar nota: {e}")
        raise e
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


# <===================== CARGAR ALUMNOS COMO USUARIOS =========================>


def cargar_alumnos_csv(archivo_csv):
    """
    CSV ejemplo:
    legajo,nombre,apellido,dni,email,curso,anio,cuatrimestre
    112111,pepe,gonzlez,50100200,pGonza@gmail.com,analisis I,2026,1
    """
    from utils.auth import hash_password

    exitosos = 0
    errores = []

    def agregar_error(fila, motivo):
        errores.append({"fila": fila, "motivo": motivo})

    conn = get_connection()
    cur = None
    try:
        cur = conn.cursor()
        lector = csv.DictReader(io.StringIO(archivo_csv))
        columnas_requeridas = {"legajo", "nombre", "apellido", "dni", "email", "curso", "anio", "cuatrimestre"}

        if not lector.fieldnames:
            raise ValueError("El archivo CSV está vacío")
        faltantes = columnas_requeridas - set(lector.fieldnames)

        if faltantes:
            raise ValueError(f"Faltan columnas: {', '.join(sorted(faltantes))}")

        for numero_fila, fila in enumerate(lector, start=2):
            try:
                if not any(fila.values()):
                    continue
                legajo = int(fila["legajo"])
                nombre = fila["nombre"].strip()
                apellido = fila["apellido"].strip()
                dni = fila["dni"].strip()
                email = fila["email"].strip()
                curso = fila["curso"].strip()
                anio = int(fila["anio"])
                cuatrimestre = int(fila["cuatrimestre"])

                # Verificar legajo existente

                cur.execute("SELECT 1 FROM alumnos WHERE legajo = %s", (legajo,))

                if cur.fetchone():
                    agregar_error(numero_fila, f"Legajo {legajo} ya existe")
                    continue

                # Verificar DNI existente
                cur.execute("SELECT 1 FROM alumnos WHERE dni = %s", (dni,))

                if cur.fetchone():
                    agregar_error(numero_fila, f"DNI {dni} ya registrado")
                    continue
                # Verificar email existente
                cur.execute("SELECT 1 FROM usuarios WHERE email = %s", (email,))

                if cur.fetchone():
                    agregar_error(numero_fila, f"Email {email} ya registrado")
                    continue
                # Crear usuario

                cur.execute(
                    """
                    INSERT INTO usuarios
                    (email, contrasenia, rol)
                    VALUES (%s, %s, 'alumno')
                    """,
                    (email, hash_password(dni)),
                )

                id_usuario = cur.lastrowid
                # Crear alumnos

                cur.execute(
                    """
                    INSERT INTO alumnos (
                        legajo,
                        nombre,
                        apellido,
                        dni,
                        email,
                        curso,
                        anio,
                        cuatrimestre,
                        estado,
                        id_usuario
                    )
                    VALUES (
                        %s, %s, %s, %s,
                        %s, %s, %s, %s,
                        'activo',
                        %s
                    )
                    """,
                    (legajo, nombre, apellido, dni, email, curso, anio, cuatrimestre, id_usuario),
                )

                exitosos += 1

            except ValueError:
                agregar_error(numero_fila, "Error de formato en campos numéricos")

            except Exception as e:
                agregar_error(numero_fila, str(e))

        conn.commit()

        return {"exitosos": exitosos, "errores": errores}

    except Exception as e:

        conn.rollback()
        raise Exception(f"Error procesando CSV: {e}")

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


# -------------------Perfil-------------------------#


def obtener_usuario_por_id(id_usuario):
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        query = "SELECT id_usuario, email, rol, contrasenia FROM usuarios WHERE id_usuario = %s"
        cur.execute(query, (id_usuario,))
        return cur.fetchone()
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def obtener_detalles_alumno(id_usuario):
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        query_alumno = """
            SELECT legajo, nombre, apellido, dni, curso, anio, cuatrimestre, estado 
            FROM alumnos 
            WHERE id_usuario = %s
        """
        cur.execute(query_alumno, (id_usuario,))
        alumno = cur.fetchone()

        if alumno:
            query_notas = """
                SELECT notas.calificacion, evaluaciones.nombre AS evaluacion_nombre, evaluaciones.tipo AS evaluacion_tipo
                FROM notas
                INNER JOIN evaluaciones ON notas.id_evaluacion = evaluaciones.id_evaluacion
                WHERE notas.legajo_alumno = %s
            """
            cur.execute(query_notas, (alumno["legajo"],))
            alumno["evaluaciones"] = cur.fetchall()

            query_equipos = """
                SELECT eq.nombre_equipo, c.anio, c.cuatrimestre
                FROM miembros_equipo me
                INNER JOIN equipos eq ON me.id_equipo = eq.id_equipo
                INNER JOIN cursos c ON eq.id_curso = c.id_curso
                WHERE me.legajo_alumno = %s
            """
        cur.execute(query_equipos, (alumno["legajo"],))
        alumno["equipos"] = cur.fetchall()

        return alumno
    except Exception as e:
        print(f"Error en alumno: {e}")
        return None
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def obtener_detalles_profesor(id_usuario):
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        query_prof = "SELECT id_profesor, nombre, departamento FROM profesores WHERE id_usuario = %s"
        cur.execute(query_prof, (id_usuario,))
        profesor = cur.fetchone()

        if profesor:

            query_cursos = """
                SELECT cursos.id_curso, CONCAT(cursos.anio, ' ', cursos.cuatrimestre) AS nombre_curso, cursos.anio, cursos.cuatrimestre AS cuatrimestre
                FROM profesor_curso
                INNER JOIN cursos ON profesor_curso.id_curso = cursos.id_curso
                WHERE profesor_curso.id_profesor = %s
            """
            cur.execute(query_cursos, (profesor["id_profesor"],))
            profesor["cursos_asignados"] = cur.fetchall()
            query_evaluaciones = """
                SELECT 
                    e.nombre AS evaluacion_nombre,
                    e.tipo AS evaluacion_tipo,
                    e.fecha,
                    CASE 
                        WHEN COUNT(n.id) > 0 THEN 'corregida'
                        ELSE 'pendiente'
                    END AS estado_evaluacion
                FROM evaluaciones e
                INNER JOIN cursos c ON e.id_curso = c.id_curso
                INNER JOIN profesor_curso pc ON c.id_curso = pc.id_curso
                LEFT JOIN notas n ON e.id_evaluacion = n.id_evaluacion
                WHERE pc.id_profesor = %s
                GROUP BY e.id_evaluacion
            """
            cur.execute(query_evaluaciones, (profesor["id_profesor"],))
            profesor["evaluaciones"] = cur.fetchall()

        return profesor
    except Exception as e:
        print(f"Error en profesor: {e}")
        return None
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def registrar_login(id_usuario, email, resultado, ip):
    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO logs_login
            (id_usuario, email, resultado, ip)
            VALUES (%s, %s, %s, %s)
            """,
            (id_usuario, email, resultado, ip),
        )
        conn.commit()
    except Exception as e:
        print(f"Error al registrar el login: {e}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def crear_alumno(alumno):
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        password_hash = generate_password_hash(alumno["password"])
        query_usuario = """
            INSERT INTO usuarios (email, contrasenia, rol)
            VALUES (%s, %s, 'alumno')
        """
        cur.execute(query_usuario, (alumno["email"], password_hash))
        id_usuario = cur.lastrowid
        query_alumno = """
            INSERT INTO alumnos (id_usuario, nombre, estado)
            VALUES (%s, %s, 'activo')
        """
        cur.execute(query_alumno, (id_usuario, alumno["nombre"]))
        conn.commit()
        return cur.lastrowid  # legajo
    except Exception as e:
        if conn:
            conn.rollback()
        raise Exception(f"Error creando alumno: {e}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def get_curso_profesor(id_profesor, pag, por_pag):
    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        offset = (pag - 1) * por_pag

        query = """
            SELECT c.* FROM cursos c
            JOIN profesor_curso pc ON c.id_curso = pc.id_curso
            WHERE pc.id_profesor = %s
            LIMIT %s OFFSET %s
        """
        cursor.execute(query, (id_profesor, por_pag, offset))
        lista_cursos = cursor.fetchall()  
        
        return lista_cursos

    except Exception as e:
        print(f"Error en la obtención de los cursos: {e}")
        raise e

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


def get_cursos_filtrados(id_curso=None, nombre_curso=None, anio=None, cuatrimestre=None, id_profesor=None, pag = None, por_pag = None):
    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        query = """
            SELECT DISTINCT c.* FROM cursos c
            JOIN profesor_curso pc ON c.id_curso = pc.id_curso
        """
        parametros = []
        condiciones = []

        if id_curso:
            condiciones.append("c.id_curso = %s")
            parametros.append(id_curso)

        if nombre_curso:
            condiciones.append("c.nombre_curso LIKE %s")
            parametros.append(f"%{nombre_curso}%")

        if anio:
            condiciones.append("c.anio = %s")
            parametros.append(anio)

        if cuatrimestre:
            condiciones.append("c.cuatrimestre = %s")
            parametros.append(cuatrimestre)

        if id_profesor:
            condiciones.append("pc.id_profesor = %s")
            parametros.append(id_profesor)

        if condiciones:
            query += " WHERE " + " AND ".join(condiciones)

        if pag and por_pag:
            offset = (pag - 1) * por_pag
            query += " LIMIT %s OFFSET %s"
            parametros.append(por_pag)
            parametros.append(offset)

        cursor.execute(query, parametros)
        cursos = cursor.fetchall()

        return cursos

    except Exception as e:
        print(f"Error en la obtención del curso: {e}")
        raise e

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


def insertar_curso(anio, cuatrimestre, id_profesor):
    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("INSERT INTO cursos (anio, cuatrimestre) VALUES (%s, %s)", (anio, cuatrimestre))
        conexion.commit()

        id_curso = cursor.lastrowid

        cursor.execute("INSERT INTO profesor_curso (id_profesor, id_curso) VALUES (%s, %s)", (id_profesor, id_curso))
        conexion.commit()

    except Exception as e:
        print(f"Error en la creación del curso {e}")
        raise e

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


def delete_curso(id_curso):
    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        query_desvincular = """
            DELETE FROM profesor_curso 
            WHERE id_curso = %s
        """
        cursor.execute(query_desvincular, (id_curso,))
        
        query_curso_vinculado = """
            SELECT COUNT(*) as total FROM profesor_curso WHERE id_curso = %s
        """
        cursor.execute(query_curso_vinculado, (id_curso,))
        resultado = cursor.fetchone()

        if resultado and resultado["total"] == 0:
            query_borrar_curso = "DELETE FROM cursos WHERE id_curso = %s"
            cursor.execute(query_borrar_curso, (id_curso,))
  
        conexion.commit()
        return True
    
    except Exception as e:
        if conexion:
            conexion.rollback()
        print(f"Error al intentar eliminar el curso: {e}")
        raise e
    
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


def modificar_curso_query(cuatrimestre, anio, id_curso):
    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        query_modificar = """
            UPDATE cursos
            SET cuatrimestre = %s, anio = %s
            WHERE id_curso = %s
        """
        cursor.execute(query_modificar, (cuatrimestre, anio, id_curso,))
        conexion.commit()

        return True

    except Exception as e:
        if conexion:
            conexion.rollback()
        print(f"Error al intentar modificar el curso: {e}")
        raise e

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


def existe_equipo(nombre_equipo, id_curso):
    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        query = "SELECT id_equipo FROM equipos WHERE nombre_equipo = %s AND id_curso = %s"

        cursor.execute(query, (nombre_equipo, id_curso))
        equipos = cursor.fetchone()
        
        return equipos

    except Exception as e:
        print(f"Error al verificar duplicado de equipo: {e}")
        raise e
    finally:
        if cursor: cursor.close()
        if conexion: conexion.close()

        
def cambiar_contrasena(id_usuario, contrasena_nueva):
   conn = None
   cur = None
   try:
       conn = get_connection()
       cur = conn.cursor(dictionary=True)


       password_hash = generate_password_hash(contrasena_nueva)


       cur.execute(
           "UPDATE usuarios SET contrasenia = %s WHERE id_usuario = %s",
           (password_hash, id_usuario)
       )
       conn.commit()
       return cur.rowcount > 0


   except Exception as e:
       print(f"Error cambiando contraseña: {e}")
       return False
   finally:
       if cur: cur.close()
       if conn: conn.close()




def editar_perfil_alumno(id_usuario, nombre, apellido, email):
   conn = None
   cur = None
   try:
       conn = get_connection()
       cur = conn.cursor(dictionary=True)


       cur.execute(
           "UPDATE alumnos SET nombre = %s, apellido = %s WHERE id_usuario = %s",
           (nombre, apellido, id_usuario)
       )
       cur.execute(
           "UPDATE usuarios SET email = %s WHERE id_usuario = %s",
           (email, id_usuario)
       )
       conn.commit()
       return True


   except Exception as e:
       print(f"Error editando perfil alumno: {e}")
       return False
   finally:
       if cur: cur.close()
       if conn: conn.close()




def editar_perfil_profesor(id_usuario, nombre, departamento, email):
   conn = None
   cur = None
   try:
       conn = get_connection()
       cur = conn.cursor(dictionary=True)


       cur.execute(
           "UPDATE profesores SET nombre = %s, departamento = %s WHERE id_usuario = %s",
           (nombre, departamento, id_usuario)
       )
       cur.execute(
           "UPDATE usuarios SET email = %s WHERE id_usuario = %s",
           (email, id_usuario)
       )
       conn.commit()
       return True


   except Exception as e:
       print(f"Error editando perfil profesor: {e}")
       return False
   finally:
       if cur: cur.close()
       if conn: conn.close()


def obtener_historial_alumno(id_usuario):
   conn = None
   cur = None
   try:
       conn = get_connection()
       cur = conn.cursor(dictionary=True)


       cur.execute(
           "SELECT legajo FROM alumnos WHERE id_usuario = %s",
           (id_usuario,)
       )
       alumno = cur.fetchone()


       if not alumno:
           return None


       cur.execute(
           """
           SELECT e.nombre AS evaluacion, e.tipo, n.calificacion, n.fecha
           FROM notas n
           INNER JOIN evaluaciones e ON n.id_evaluacion = e.id_evaluacion
           WHERE n.legajo_alumno = %s
           ORDER BY n.fecha ASC
           """,
           (alumno['legajo'],)
       )
       return cur.fetchall()


   except Exception as e:
       print(f"Error obteniendo historial: {e}")
       return None
   finally:
       if cur: cur.close()
       if conn: conn.close()
