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
            """SELECT p.id_profesor as id, p.nombre, u.email, u.contrasenia as password 
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

CAMPOS_PERMITIDOS_UPDATE = {
    'titulo', 'descripcion', 'tema', 'fecha_material',
    'estado', 'orden_material', 'es_libre', 'tipo_material'
}
ESTADOS_VALIDOS = {'borrador', 'publicado', 'archivado'}

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
    estado='publicado'
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
        cursor.execute(query, (
            id_curso, id_profesor, titulo, descripcion, tipo_material,
            tema, orden_material, archivo_ruta, es_externo, tipo_archivo,
            tamano_bytes, fecha_material, es_libre, estado
        ))
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        conn.rollback()
        print(f"Error inserting material: {e}")
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
    limite=20
):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        where_clauses = []
        params = []
        if activo is not None:
            where_clauses.append("activo = %s")
            params.append(activo)
        if id_curso:
            where_clauses.append("id_curso = %s")
            params.append(id_curso)
        if id_profesor:
            where_clauses.append("id_profesor = %s")
            params.append(id_profesor)
        if tipo_material:
            where_clauses.append("tipo_material = %s")
            params.append(tipo_material)
        if tema:
            where_clauses.append("tema = %s")
            params.append(tema)
        if estado:
            where_clauses.append("estado = %s")
            params.append(estado)
        if es_libre is not None:
            where_clauses.append("es_libre = %s")
            params.append(es_libre)
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        cursor.execute(f"SELECT COUNT(*) as total FROM materiales WHERE {where_sql}", params)
        total = cursor.fetchone()['total']
        offset = (pagina - 1) * limite
        query = f"""
            SELECT * FROM materiales
            WHERE {where_sql}
            ORDER BY fecha_subida DESC
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

def get_material(id_material):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM materiales WHERE id_material = %s AND activo = TRUE",
            (id_material,)
        )
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
    if 'estado' in updates and updates['estado'] not in ESTADOS_VALIDOS:
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
        cursor.execute(
            "UPDATE materiales SET activo = FALSE WHERE id_material = %s AND activo = TRUE",
            (id_material,)
        )
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        print(f"Error deleting material: {e}")
        return False
    finally:
        conn.close()

