from flask import Flask, request, jsonify
from flask import Blueprint
from database.db import get_connection
from data.queries import (
    get_equipos_filtrados,
    get_equipo_id,
    insertar_equipo,
    actualizar_equipo,
    delete_equipo
)

equipos_bp = Blueprint('equipos', __name__)


@equipos_bp.route('/', methods=['GET'])
def obtener_equipos():
    try:
        filtro_id_equipo = request.args.get('id_equipo')
        filtro_nombre_equipo = request.args.get('nombre_equipo')
        filtro_id_curso = request.args.get('id_curso')

        id_equipo_int = None
        id_curso_int = None

        if filtro_id_equipo:
            try:
                id_equipo_int = int(filtro_id_equipo)
                if id_equipo_int <= 0:
                    return jsonify({"error": "El ID debe ser un número positivo"}), 400
                
            except ValueError:
                return jsonify({"error":"El ID del equipo debe ser un número válido"}), 400

        if filtro_id_curso:
            try:
                id_curso_int = int(filtro_id_curso)
                if id_curso_int <= 0:
                    return jsonify({"error": "El ID debe ser un número positivo"}), 400
                
            except ValueError:
                return jsonify({"error":"El ID del curso debe ser un número válido"}), 400

        lista_equipos = get_equipos_filtrados(id_equipo_int, filtro_nombre_equipo, id_curso_int)

        return jsonify(lista_equipos), 200
    
    except Exception as e:
        print(e)
        return jsonify({"error": "Error interno del servidor"}), 500 


@equipos_bp.route('/<int:id_equipo>', methods=['GET'])
def obtener_equipo_id(id_equipo):
     
    if id_equipo <= 0:
        return jsonify({"error": "El ID debe ser un número positivo"}), 400

    try:
        equipo = get_equipo_id(id_equipo)

        if equipo:
            return jsonify(equipo), 200
        return jsonify({"error": "Equipo no encontrado"}), 404

    except Exception as e:
        print(e)
        return jsonify({"error": "Error interno del servidor"}), 500


@equipos_bp.route('/', methods=['POST'])
def crear_equipo():
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

        equipo_existente = get_equipos_filtrados(None, nombre_equipo, id_curso_int)

        if equipo_existente:
            return jsonify({"error": "El equipo ya existe dentro del curso elegido"}), 409

        insertar_equipo(nombre_equipo, id_curso_int)
        return jsonify({"mensaje": "Equipo creado con éxito"}), 201
   
    except Exception as e:
        print(e)
        return jsonify({"error": "Error interno del servidor"}), 500


@equipos_bp.route('/<int:id_equipo>', methods=['PUT'])
def reemplazar_equipo(id_equipo):

    if id_equipo <= 0:
        return jsonify({"error": "El ID debe ser un número positivo"}), 400

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
        
        equipo_existente = get_equipo_id(id_equipo)

        if equipo_existente:
            actualizar_equipo(id_equipo, nombre_equipo, id_curso_int)
            return jsonify({"mensaje": "Equipo actualizado con éxito"}), 200

        else:
            insertar_equipo(nombre_equipo, id_curso_int)
            return jsonify({"mensaje": "Equipo creado con éxito"}), 201

    except Exception as e:
        print(e)
        return jsonify({"error": "Error interno del servidor"}), 500
        
        
@equipos_bp.route('/<int:id_equipo>', methods=['DELETE'])
def eliminar_equipo(id_equipo):

    if id_equipo <= 0:
        return jsonify({"error": "El ID debe ser un número positivo"}), 400

    try:
        equipo_existente = get_equipo_id(id_equipo)

        if not equipo_existente:
            return jsonify({"error":"Equipo no encontrado"}), 404
    
        delete_equipo(id_equipo)
        return "", 204
        
    except Exception as e:
        print(e)
        return jsonify({"error": "Error interno del servidor"}), 500