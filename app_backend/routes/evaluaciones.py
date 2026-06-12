from flask import Blueprint, request, jsonify
from datetime import datetime
from data.queries import get_connection
from data.queries import (
    get_connection,
    get_user_profile,
    get_evaluacion_profesor,
    get_evaluacion_todas,
    get_evaluacion,
    get_evaluacion_por_curso,
    crear_evaluacion,
    cambiar_evaluacion,
    eliminar_evaluacion
)

evaluaciones_bp = Blueprint('evaluaciones', __name__)

@evaluaciones_bp.route('/<int:id>', methods=['GET'])
def obtener_eva(id):
    evaluacion = get_evaluacion(id)
    return evaluacion

@evaluaciones_bp.route('/curso/<int:id_curso>', methods=['GET'])
def obtener_evas_curso(id_curso):
    evaluacion = get_evaluacion_por_curso(id_curso)
    if not evaluacion or len(evaluacion) <= 0:
        return evaluacion
    return evaluacion

@evaluaciones_bp.route('/usuario', methods=['GET', 'POST'])
def obtener_eva_usuario():
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

    evaluacion = get_evaluacion_profesor(perfil["id_profesor"])
    if not evaluacion or len(evaluacion) <= 0:
        return jsonify({"body": []}), 204

    evaluacion_formateada = []
    for eva in evaluacion:
        lista = list(eva)
        lista[3] = eva[3].strftime("%Y-%m-%d")
        evaluacion_formateada.append(lista)

    return jsonify({"body": evaluacion_formateada}), 200

@evaluaciones_bp.route('/todas', methods=['GET'])
def obtener_evas_todas():
    evaluacion = get_evaluacion_todas()
    if (len(evaluacion) <= 0 or evaluacion == None):
        return jsonify({"body":[], "status":204})
    evaluacion_formateada = []
    for eva in evaluacion:
        lista = list(eva)
        lista[3] = eva[3].strftime("%Y-%m-%d")
        evaluacion_formateada.append(lista)
    return jsonify({"body": evaluacion_formateada, "status": 200})


@evaluaciones_bp.route('/crear', methods=['POST'])
def crear_eva():
    data = request.get_json()
    campos = ["nombre", "tipo", "fecha", "curso_id"]
    if not data:
        return jsonify({"error": "Body vacío"}), 400
    for c in campos:
        if c not in data or data.get(c) is None:
            return jsonify({"error": f"Campo obligatorio faltante: {c}"}), 400
    resultado = crear_evaluacion(data.get("nombre"),data.get("tipo"),data.get("fecha"),data.get("curso_id"))
    return resultado

@evaluaciones_bp.route('/actualizar/', methods=['PUT'])
def actualizar_eva():                              # ← typo corregido: "actualiar" → "actualizar"
    data = request.get_json()
    campos = ["id", "nombre", "tipo", "fecha", "curso_id"]
    if not data:
        return jsonify({"error": "Body vacío"}), 400
    for c in campos:
        if c not in data or data.get(c) is None:
            return jsonify({"error": f"Campo obligatorio faltante: {c}"}), 400
    resultado = cambiar_evaluacion(data["id"], data["nombre"], data["tipo"], data["fecha"], data["curso_id"])
    return resultado

@evaluaciones_bp.route('/destruir/<int:id>', methods=['DELETE'])
def destruir_eva(id):
    resultado = eliminar_evaluacion(id)
    if (resultado == False):
        return jsonify({"body": {"estado": resultado}, "status": 400})
    return jsonify({"body": {"estado": resultado}, "status": 200})
