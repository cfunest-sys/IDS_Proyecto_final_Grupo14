from flask import Flask, render_template, request, jsonify
from flask import Blueprint
from database.db import get_connection

equipos_bp = Blueprint('equipos_bp', __name__)


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
            condiciones.append("id_equipo = %s")
            parametros.append(filtro_id_equipo)

        if filtro_nombre_equipo:
            condiciones.append("nombre_equipo = %s")
            parametros.append(filtro_nombre_equipo)  

        if filtro_id_curso:
            condiciones.append("id_curso = %s")
            parametros.append(filtro_id_curso)       

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
        
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM equipos WHERE nombre_equipo = %s AND id_curso = %s", (nombre_equipo, id_curso))
        equipo_existente = cursor.fetchone()

        if equipo_existente:
            return jsonify({"error": "El equipo ya existe dentro del curso elegido"}), 409

        cursor.execute("INSERT INTO equipos (nombre_equipo, id_curso) VALUES (%s, %s)", (nombre_equipo, id_curso))

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

