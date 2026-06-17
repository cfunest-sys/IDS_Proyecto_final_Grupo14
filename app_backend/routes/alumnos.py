from flask import Blueprint, request, jsonify
from data.queries import (
    get_alumnos,
    cargar_alumnos_csv,
    desactivar_alumno_query,
)
from utils.auth import token_required, rol_required

alumnos_bp = Blueprint("alumnos", __name__)




@alumnos_bp.route("/", methods=["GET"])
def obtener_alumnos():
    alumnos = get_alumnos()
    return jsonify(alumnos)




@alumnos_bp.route("/actualizar/desactivar", methods=["PUT"])
def desactivar_alumno():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Body vacío"}), 400

        legajo = data.get("legajo", "")
        estado = data.get("estado", "")

        resultado = desactivar_alumno_query(legajo, estado)
    except Exception as e:
        print(f"Error en desactivar alumno: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500
    if not resultado:
        return jsonify({"message": "No se pudo actualizar el alumno"}), 500
    return jsonify({"message": "Alumno actualizado exitosamente"}), 200



@alumnos_bp.route("/cargar-csv", methods=["POST"])
@token_required
@rol_required("profesor")
def cargar_alumnos(current_user):
    if "archivo" not in request.files:
        return jsonify({"error": "No se envio archivo"}), 400
    archivo = request.files["archivo"]

    if not archivo.filename.endswith(".csv"):
        return jsonify({"error": "El formato de archivo no es .csv"}), 400
    contenido = archivo.read().decode("utf-8")
    resultado = cargar_alumnos_csv(contenido)

    return (
        jsonify(
            {
                "mensaje": f"Se cargaron {resultado['exitosos']} alumnos",
                "exitosos": resultado["exitosos"],
                "errores": resultado["errores"],
            }
        ),
        200,
    )
