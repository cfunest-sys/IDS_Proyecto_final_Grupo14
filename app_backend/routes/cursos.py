from flask import Flask, request, jsonify
from flask import Blueprint
from utils.auth import token_required, rol_required
from data.queries import (
    get_curso_profesor,
    get_cursos_filtrados,
    insertar_curso,
    delete_curso,
)

cursos_bp = Blueprint('cursos', __name__)

@cursos_bp.route('/', methods=['GET'])
@token_required
@rol_required("profesor")
def listar_cursos(current_user):
    try:
        id_profesor = current_user["id"]
        pag = request.args.get('pag', default=1, type=int)
        por_pag = 15 
        
        if pag <= 0:
            return jsonify({"error": "La página debe ser un número positivo"}), 400
        
        cursos = get_curso_profesor(id_profesor, pag, por_pag)

        if not cursos:
            return jsonify({"error": "No tiene cursos asignados"}), 200

        return jsonify(cursos), 200

    except Exception as e:
        print(e)
        return jsonify({"error": "Error interno del servidor"}), 500
    

@cursos_bp.route('/filtros/', methods=['GET'])
@token_required
@rol_required("profesor")
def listar_cursos_filtrados(current_user):
    try:
        pag = request.args.get('pag', default=1, type=int)
        por_pag = 15 

        if pag <= 0:
            return jsonify({"error": "La página debe ser un número positivo"}), 400
        
        id_profesor = current_user["id"]
        filtro_id_curso = request.args.get('id_curso')
        filtro_nombre_curso = request.args.get('nombre_curso')
        filtro_anio = request.args.get('anio')
        filtro_cuatrimestre = request.args.get('cuatrimestre')

        if filtro_id_curso == "": 
            filtro_id_curso = None
        if filtro_nombre_curso == "": 
            filtro_nombre_curso = None
        if filtro_anio == "": 
            filtro_anio = None
        if filtro_cuatrimestre == "": 
            filtro_cuatrimestre = None

        id_curso_int = None
        anio_int = None
        cuatrimestre_int = None

        if filtro_id_curso:
            try:
                id_curso_int = int(filtro_id_curso)
                if id_curso_int <= 0:
                    return jsonify({"error": "El ID debe ser un número positivo"}), 400
                
            except ValueError:
                return jsonify({"error":"El ID del curso debe ser un número válido"}), 400

        if filtro_anio:
            try:
                anio_int = int(filtro_anio)
                if anio_int <= 0:
                    return jsonify({"error": "El año debe ser un número positivo"}), 400
                
            except ValueError:
                return jsonify({"error":"El año debe ser un número válido"}), 400
            
        if filtro_cuatrimestre:
            try:
                cuatrimestre_int = int(filtro_cuatrimestre)
                if cuatrimestre_int <= 0:
                    return jsonify({"error": "El cuatrimestre debe ser un número positivo"}), 400
        
            except (ValueError, TypeError):
                return jsonify({"error": "El cuatrimestre debe ser un número entero válido"}), 400
            

        lista_cursos = get_cursos_filtrados(id_curso_int, filtro_nombre_curso, anio_int, cuatrimestre_int, id_profesor, pag, por_pag)

        return jsonify(lista_cursos), 200
        

    except Exception as e:
        print(e)
        return jsonify({"error": "Error interno del servidor"}), 500


@cursos_bp.route('/', methods=['POST'])
@token_required
@rol_required("profesor")
def crear_cursos(current_user):
    try:
        datos = request.get_json()
        id_profesor = current_user["id"]

        if not datos:
            return jsonify({"error": "Body vacío"}), 400
        
        if "nombre_curso" not in datos or "anio" not in datos or "cuatrimestre" not in datos:
            return jsonify({"error": "Faltan campos obligatorios"}), 400
        
        nombre_curso = datos.get("nombre_curso")
        anio = datos.get("anio")
        cuatrimestre = datos.get("cuatrimestre")

        if not nombre_curso or not anio or not cuatrimestre:
            return jsonify({"error": "Campos obligatorios vacios"}), 400
        
        try:
            anio_int = int(anio)
            if anio_int <= 0:
                return jsonify({"error": "El año debe ser un número positivo"}), 400
            
        except (ValueError, TypeError):
            return jsonify({"error": "El año debe ser un número entero válido"}), 400
        
        try:
            cuatrimestre_int = int(cuatrimestre)
            if cuatrimestre_int <= 0:
                return jsonify({"error": "El cuatrimestre debe ser un número positivo"}), 400
        
        except (ValueError, TypeError):
            return jsonify({"error": "El cuatrimestre debe ser un número entero válido"}), 400

        curso_existente = get_cursos_filtrados(nombre_curso=nombre_curso, anio=anio_int, cuatrimestre=cuatrimestre_int, id_profesor=id_profesor)

        if curso_existente:
            return jsonify({"error": "El curso ya existe dentro del cuatrimestre elegido"}), 409

        insertar_curso(nombre_curso, anio_int, cuatrimestre_int, id_profesor)
        return jsonify({"mensaje": "Curso creado con éxito"}), 201
   
    except Exception as e:
        print(e)
        return jsonify({"error": "Error interno del servidor"}), 500


@cursos_bp.route('/<int:id_curso>', methods=['DELETE'])
@token_required
@rol_required("profesor")
def borrar_cursos(current_user, id_curso):
    if id_curso <= 0:
        return jsonify({"error": "El ID debe ser un número positivo"}), 400
        
    id_profesor = current_user["id"]

    try:
        curso_existente = get_cursos_filtrados(id_curso, id_profesor=id_profesor)

        if not curso_existente:
            return jsonify({"error":"Curso no encontrado"}), 404
    
        delete_curso(id_curso, id_profesor)
        return "", 204
        
    except Exception as e:
        print(e)
        return jsonify({"error": "Error interno del servidor"}), 500