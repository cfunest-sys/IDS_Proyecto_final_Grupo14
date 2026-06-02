from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.auth import generate_token, validate_profesor_credentials

profesores_bp = Blueprint("profesores", __name__)


@profesores_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    if not data:
        return jsonify({"error": "No se enviaron datos"}), 400

    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email y contraseña son obligatorios"}), 400

    profesor = validate_profesor_credentials(email, password)

    if not profesor:
        return jsonify({"error": "Email o contraseña inválidos"}), 401

    access_token = generate_token(usuario_id=profesor["id"], rol=profesor["rol"])

    return (
        jsonify(
            {
                "success": True,
                "message": "Login exitoso",
                "token": access_token,
                "profesor": {"id": profesor["id"], "nombre": profesor["nombre"], "email": profesor["email"], "rol": profesor["rol"]},
            }
        ),
        200,
    )


@profesores_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_profesor():
    profesor_id = get_jwt_identity()
    return jsonify({"profesor_id": profesor_id}), 200
