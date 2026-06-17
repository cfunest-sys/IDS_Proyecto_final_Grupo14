from flask import Blueprint, request, jsonify
from utils.auth import token_required, rol_required
from data.queries import (
    get_alumnos,
    cargar_alumnos_csv,
    desactivar_alumno_query,
)
from utils.auth import token_required, rol_required

alumnos_bp = Blueprint("alumnos", __name__)


<<<<<<< HEAD
=======
@alumnos_bp.route("/login", methods=["POST"])
def login():
    # Hace falta agregar la lógica para el inicio de sesión
    return "Inicio de sesión exitoso"


@alumnos_bp.route("/register", methods=["POST"])
def register():

    try:

        data = request.json

        print(data)

        nombre = data.get("nombre")
        email = data.get("email")
        password = data.get("password")

        print(nombre, email)

        if not nombre or not email or not password:

            return jsonify({"error": "Faltan datos obligatorios"}), 400

        alumno = {"nombre": nombre, "email": email, "password": password}

        legajo = crear_alumno(alumno)

        return jsonify({"mensaje": "Alumno registrado correctamente", "legajo": legajo}), 201

    except Exception as e:

        print(e)

        return jsonify({"error": str(e)}), 500


@alumnos_bp.route("/<int:id>", methods=["GET"])
@token_required
def obtener_alumno(current_user, id):
    alumno = get_alumno(id)
    return jsonify(alumno)
>>>>>>> ff6f1ba090701136fca0269f599318abe0c4b988


@alumnos_bp.route("/", methods=["GET"])
@token_required
def obtener_alumnos(current_user):
    alumnos = get_alumnos()
    return jsonify(alumnos)


<<<<<<< HEAD


=======
@alumnos_bp.route("/cargar", methods=["POST"])
@token_required
def cargar_alumno_route(current_user):
    data = request.get_json()
    campo = ["nombre", "contrasenia", "email", "created_at", "estado", "rol"]
    if not data:
        return jsonify({"error": "Body vacío"}), 400
    for c in campo:
        if c not in data or data.get(c) is None:
            return jsonify({"error": "Body incompleto"}), 400
    resultado = cargar_alumno(
        data["nombre"], data["contrasenia"], data["email"], data["created_at"], data["estado"], data["rol"]
    )
    return jsonify({"message": "Alumno cargado exitosamente", "id": resultado})


@alumnos_bp.route("/actualizar/<int:id>", methods=["PUT"])
@token_required
def actualizar_alumno(current_user, id):
    data = request.get_json()
    campo = ["nombre", "contrasenia", "email", "created_at", "estado", "rol"]
    if not data:
        return jsonify({"error": "Body vacío"}), 400
    for c in campo:
        if c not in data or data.get(c) is None:
            return jsonify({"error": "Body incompleto"}), 400
    resultado = actualizar_alumno(
        id, data["nombre"], data["contrasenia"], data["email"], data["created_at"], data["estado"], data["rol"]
    )
    return jsonify({"message": "Alumno actualizado exitosamente", "id": resultado})

>>>>>>> ff6f1ba090701136fca0269f599318abe0c4b988
@alumnos_bp.route("/actualizar/desactivar", methods=["PUT"])
@token_required
def desactivar_alumno(current_user):
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


<<<<<<< HEAD
=======
@alumnos_bp.route("/eliminar/<int:id>", methods=["DELETE"])
@token_required
def eliminar_alumno(current_user, id):
    resultado = eliminar_alumno(id)
    return jsonify({"message": "Alumno eliminado exitosamente", "id": resultado})

>>>>>>> ff6f1ba090701136fca0269f599318abe0c4b988

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
