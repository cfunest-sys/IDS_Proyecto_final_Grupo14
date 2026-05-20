from flask import Blueprint, request, jsonify

from data.queries import get_connection

from data.queries import (
    get_evaluacion,
    crear_evaluacion,
    cambiar_evaluacion,
    eliminar_evaluacion
)

evaluaciones_bp = Blueprint('evaluaciones', __name__)

@evaluaciones_bp.route('/<int:id>', methods=['GET'])
def obtener_eva(id):
    evaluacion = get_evaluacion(id)
    return evaluacion

@evaluaciones_bp.route('/crear', methods=['POST'])
def crear_eva():
    data = request.get_json()
    campo = ["nombre", "tipo", "fecha", "curso_id"]
    if not data:
        return jsonify({"error": "Body vacío"}), 400
    for c in campo:
        if c not in data or data.get(c) is None:
            return jsonify({"error": "Body incompleto"}), 400
    resultado = crear_evaluacion(data["nombre"],data["tipo"],data["fecha"],data["curso_id"])
    return resultado

@evaluaciones_bp.route('/actualizar/', methods=['PUT'])
def actualiar_eva():
    data = request.get_json()
    campo = ["id", "nombre", "tipo", "fecha", "curso_id"]
    if not data:
        return jsonify({"error": "Body vacío"}), 400
    for c in campo:
        if c not in data or data.get(c) is None:
            return jsonify({"error": "Body incompleto"}), 400
    resultado = cambiar_evaluacion(data["id"], data["nombre"],data["tipo"],data["fecha"],data["curso_id"])
    return resultado

@evaluaciones_bp.route('/destruir/<int:id>', methods=['DELETE'])
def destruir_eva(id):
    resultado = eliminar_evaluacion(id)
    return resultado
