from flask import Blueprint, request, jsonify
from utils.auth import token_required
from data.queries import (
    get_user_profile,
    get_evaluacion_profesor,
    get_evaluacion_por_curso,
    get_cursos_profesor,  # <-- Agregado
    crear_evaluacion,
    cambiar_evaluacion,
    eliminar_evaluacion
)
from datetime import date, datetime # Aseguramos la importación para el formateo de fechas

evaluaciones_bp = Blueprint('evaluaciones', __name__)

@evaluaciones_bp.route('/usuario', methods=['GET', 'POST'])
@token_required
def obtener_eva_usuario(current_user):
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "No se enviaron datos"}), 400

    usuario = {
        "rol": data.get("rol", ""),
        "id_usuario": data.get("user_id", "")
    }

    perfil = get_user_profile(usuario)
    if perfil is None:
        return jsonify({"error": "Usuario no encontrado"}), 404

    rol = data.get("rol", "")
    if rol == "profesor":
        evaluacion = get_evaluacion_profesor(perfil["id_profesor"])
    elif rol == "alumno":
        evaluacion = get_evaluacion_por_curso(perfil["curso"])
    else:
        return jsonify({"error": "Rol no válido"}), 400
        
    if not evaluacion or len(evaluacion) <= 0:
        return jsonify({"body": []}), 204

    evaluacion_formateada = []
    for eva in evaluacion:
        if isinstance(eva, dict):
            # Formato Diccionario (Profesor)
            f = eva.get("fecha")
            fecha_str = f.strftime("%Y-%m-%d") if isinstance(f, (date, datetime)) else str(f)
            evaluacion_formateada.append({
                "id_evaluacion": eva.get("id_evaluacion"),
                "nombre": eva.get("nombre"),
                "tipo": eva.get("tipo"),
                "fecha": fecha_str,
                "id_curso": eva.get("id_curso"),
                "curso_nombre": eva.get("curso_nombre", f"Curso {eva.get('id_curso')}"),
                "cuatrimestre": eva.get("cuatrimestre"), # <-- AGREGADO
                "anio": eva.get("anio")                  # <-- AGREGADO
            })
        else:
            # Formato Tupla/Lista Tradicional (Alumno)
            lista = list(eva)
            fecha_str = lista[3].strftime("%Y-%m-%d") if isinstance(lista[3], (date, datetime)) else str(lista[3])
            
            # Calculamos cuatri y año a partir de la fecha por si la tupla no los trae
            dt = datetime.strptime(fecha_str, "%Y-%m-%d") if isinstance(fecha_str, str) and "-" in fecha_str else None

            evaluacion_formateada.append({
                "id_evaluacion": lista[0],
                "nombre": lista[1],
                "tipo": lista[2],
                "fecha": fecha_str,
                "id_curso": lista[4] if len(lista) > 4 else "",
                "curso_nombre": f"Curso {lista[4]}" if len(lista) > 4 else "N/A",
                "cuatrimestre": 1 if dt and dt.month <= 6 else 2, # <-- AGREGADO
                "anio": dt.year if dt else ""                     # <-- AGREGADO
            })

    return jsonify({"body": evaluacion_formateada}), 200


@evaluaciones_bp.route('/cursos', methods=['POST'])
@token_required
def obtener_cursos_profesor_route(current_user):
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "No se enviaron datos"}), 400

    usuario = {
        "rol": data.get("rol", ""),
        "id_usuario": data.get("user_id", "")
    }

    perfil = get_user_profile(usuario)
    if perfil is None:
        return jsonify({"error": "Usuario no encontrado"}), 404

    cursos = get_cursos_profesor(perfil["id_profesor"])
    return jsonify({"body": cursos}), 200

@evaluaciones_bp.route("/crear", methods=["POST"])
@token_required
def crear_eva(current_user):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Body vacío"}), 400
    for campo in ["nombre", "tipo", "fecha", "curso_id"]:
        if not data.get(campo):
            return jsonify({"error": f"Campo obligatorio faltante: {campo}"}), 400
    return crear_evaluacion(
        data["nombre"], data["tipo"], data["fecha"], data["curso_id"]
    )


@evaluaciones_bp.route("/actualizar/", methods=["PUT"])
@token_required
def actualizar_eva(current_user):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Body vacío"}), 400
    for campo in ["id", "nombre", "tipo", "fecha", "curso_id"]:
        if not data.get(campo):
            return jsonify({"error": f"Campo obligatorio faltante: {campo}"}), 400
    return cambiar_evaluacion(
        data["id"], data["nombre"], data["tipo"], data["fecha"], data["curso_id"]
    )


@evaluaciones_bp.route("/destruir/<int:id>", methods=["DELETE"])
@token_required
def destruir_eva(current_user, id):
    resultado = eliminar_evaluacion(id)
    estado_http = 200 if resultado else 400
    return jsonify({"body": {"estado": resultado}}), estado_http
