from database.db import get_connection
from flask import jsonify

def get_alumno(nombre, contrasenia):
    """Obtiene un alumno por su nombre y contraseña."""
    if not nombre or not contrasenia:
        raise ValueError("Todos los campos son obligatorios")
    
    cur = None
    try:
        cur = get_connection().cursor()
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

def get_alumnos():
    """Obtiene todos los alumnos."""
    cur = None
    try:
        cur = get_connection().cursor()
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

def cargar_alumno(nombre, contrasenia, email, created_at, estado, rol):
    """Carga un nuevo alumno en la base de datos."""
    if not nombre or not contrasenia or not email or not created_at or estado is None or not rol:
        raise ValueError("Todos los campos son obligatorios")
    
    cur = None
    try:
        cur = get_connection().cursor()
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

def actualizar_alumno(legajo, nombre, contrasenia, email, created_at, estado, rol):
    """Actualiza un alumno existente en la base de datos."""
    if not legajo or not nombre or not contrasenia or not email or not created_at or estado is None or not rol:
        raise ValueError("Todos los campos son obligatorios")
    
    cur = None
    try:
        cur = get_connection().cursor()
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

def eliminar_alumno(legajo):
    """Elimina un alumno de la base de datos."""
    if not legajo:
        raise ValueError("El legajo es obligatorio")
    
    cur = None
    try:
        cur = get_connection().cursor()
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

def get_profesor(nombre, contrasenia):
    """Obtiene un profesor por su nombre y contraseña."""
    if not nombre or not contrasenia:
        raise ValueError("Todos los campos son obligatorios")
    
    cur = None
    try:
        cur = get_connection().cursor()
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

def get_all_users():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    cursor.close()
    connection.close()
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
