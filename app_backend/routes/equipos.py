from flask import Flask, request, jsonify
from flask import Blueprint
from database.db import get_connection

equipos_bp = Blueprint('equipos', __name__)


@equipos_bp.route('/', methods=['GET'])
def obtener_equipos():
    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        filtro_id_equipo = request.args.get('id_equipo')
        filtro_nombre_equipo = request.args.get('nombre_equipo')
        filtro_id_curso = request.args.get('id_curso')

        query = "SELECT * FROM equipos"
        parametros = []
        condiciones = []

        if filtro_id_equipo:
            try:
                id_equipo_int = int(filtro_id_equipo)
                if id_equipo_int <= 0:
                    return jsonify({"error": "El ID debe ser un número positivo"}), 400
                
                condiciones.append("id_equipo = %s")
                parametros.append(id_equipo_int)

            except ValueError:
                return jsonify({"error":"El ID del equipo debe ser un número válido"}), 400

        if filtro_nombre_equipo:
            condiciones.append("nombre_equipo = %s")
            parametros.append(filtro_nombre_equipo)  

        if filtro_id_curso:
            try:
                id_curso_int = int(filtro_id_curso)
                if id_curso_int <= 0:
                    return jsonify({"error": "El ID debe ser un número positivo"}), 400
                
                condiciones.append("id_curso = %s")
                parametros.append(id_curso_int)  

            except ValueError:
                return jsonify({"error":"El ID del curso debe ser un número válido"}), 400

        if condiciones:
            query += " WHERE " + " AND ".join(condiciones)

        cursor.execute(query, parametros)
        equipos = cursor.fetchall()

        return jsonify(equipos), 200
    
    except Exception as e:
        print(e)
        return jsonify({"error": "Error interno del servidor"}), 500
    
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()    


@equipos_bp.route('/<int:id_equipo>', methods=['GET'])
def obtener_equipo_id(id_equipo):
     
    if id_equipo <= 0:
        return jsonify({"error": "El ID debe ser un número positivo"}), 400

    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("SELECT * FROM equipos WHERE id_equipo = %s", (id_equipo,))
        equipo = cursor.fetchone()

        if equipo:
            return jsonify(equipo), 200
        return jsonify({"error": "Equipo no encontrado"}), 404

    except Exception as e:
        print(e)
        return jsonify({"error": "Error interno del servidor"}), 500

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


@equipos_bp.route('/', methods=['POST'])
def crear_equipo():
    conexion = None
    cursor = None

    try:
        datos = request.get_json()
        
        if not datos:
            return jsonify({"error": "Body vacío"}), 400
        
        if "nombre_equipo" not in datos or "id_curso" not in datos:
            return jsonify({"error": "Faltan campos obligatorios"}), 400
        
        nombre_equipo = datos.get("nombre_equipo")
        id_curso = datos.get("id_curso")

        if not nombre_equipo or not id_curso:
            return jsonify({"error": "Campos obligatorios vacios"}), 400
        
        if len(nombre_equipo) > 255:
            return jsonify({"error": "El nombre del equipo no puede superar los 255 caracteres"}), 400
        
        try:
            id_curso_int = int(id_curso)
            if id_curso_int <= 0:
                return jsonify({"error": "El ID del curso debe ser un número positivo"}), 400
            
        except (ValueError, TypeError):
            return jsonify({"error": "El ID del curso debe ser un número entero válido"}), 400

        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM equipos WHERE nombre_equipo = %s AND id_curso = %s", (nombre_equipo, id_curso_int))
        equipo_existente = cursor.fetchone()

        if equipo_existente:
            return jsonify({"error": "El equipo ya existe dentro del curso elegido"}), 409

        cursor.execute("INSERT INTO equipos (nombre_equipo, id_curso) VALUES (%s, %s)", (nombre_equipo, id_curso_int))

        conexion.commit()

        return jsonify({"mensaje": "Equipo creado con éxito"}), 201
   
    except Exception as e:
        print(e)
        return jsonify({"error": "Error interno del servidor"}), 500

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


@equipos_bp.route('/<int:id_equipo>', methods=['PUT'])
def reemplazar_equipo(id_equipo):

    if id_equipo <= 0:
        return jsonify({"error": "El ID debe ser un número positivo"}), 400

    conexion = None
    cursor = None

    try:
        datos = request.get_json()

        if not datos:
            return jsonify({"error": "Body vacío"}), 400
        
        if "nombre_equipo" not in datos or "id_curso" not in datos:
            return jsonify({"error": "Faltan campos obligatorios"}), 400
        
        nombre_equipo = datos.get("nombre_equipo")
        id_curso = datos.get("id_curso")

        if not nombre_equipo or not id_curso:
            return jsonify({"error": "Campos obligatorios vacios"}), 400
        
        if len(nombre_equipo) > 255:
            return jsonify({"error": "El nombre del equipo no puede superar los 255 caracteres"}), 400
        
        try:
            id_curso_int = int(id_curso)
            if id_curso_int <= 0:
                return jsonify({"error": "El ID del curso debe ser un número positivo"}), 400
            
        except (ValueError, TypeError):
            return jsonify({"error": "El ID del curso debe ser un número entero válido"}), 400
        
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM equipos WHERE id_equipo = %s", (id_equipo,))
        equipo_existente = cursor.fetchone()

        if equipo_existente:
            query_update = "UPDATE equipos SET nombre_equipo = %s, id_curso = %s WHERE id_equipo = %s"
            cursor.execute(query_update, (nombre_equipo, id_curso_int, id_equipo))
            mensaje = "Equipo modificado con éxito"
            status_code = 200
        else:
            query_insert = "INSERT INTO equipos (nombre_equipo, id_curso) VALUES (%s, %s)"
            cursor.execute(query_insert, (nombre_equipo, id_curso_int))
            id_nuevo = cursor.lastrowid
            mensaje = f"Equipo creado con éxito con el ID {id_nuevo}"
            status_code = 201

        conexion.commit()
        return jsonify({"mensaje": mensaje}), status_code
    
    except Exception as e:
        if conexion:
            conexion.rollback()
        print(e)
        return jsonify({"error": "Error interno del servidor"}), 500

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()
        
        
@equipos_bp.route('/<int:id_equipo>', methods=['DELETE'])
def eliminar_equipo(id_equipo):

    if id_equipo <= 0:
        return jsonify({"error": "El ID debe ser un número positivo"}), 400
    
    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("SELECT * FROM equipos WHERE id_equipo = %s", (id_equipo,))
        equipo_existente = cursor.fetchone()

        if not equipo_existente:
            return jsonify({"error":"Equipo no encontrado"}), 404
    
        cursor.execute("DELETE FROM equipos WHERE id_equipo = %s", (id_equipo,))
        conexion.commit()
        return "", 204
        
    except Exception as e:
        if conexion:
            conexion.rollback()
        print(e)
        return jsonify({"error": "Error interno del servidor"}), 500

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()