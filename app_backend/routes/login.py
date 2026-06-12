from flask import Blueprint, request, jsonify, session
from flask_jwt_extended import create_access_token
from utils.auth import validate_user_credentials
from data.queries import registrar_login, get_user_profile

login_bp = Blueprint("login", __name__)


@login_bp.route("/", methods=["POST"])
def login():

    data = request.get_json()

    if not data:
        return jsonify({"error": "No se enviaron datos"}), 400

    email = data.get("email", "").strip()
    password = data.get("password", "")

    usuario = validate_user_credentials(email, password)

    if not usuario:

        registrar_login(None, email, "fallido", request.remote_addr)

        return jsonify({"error": "Email o contraseña inválidos"}), 401

    session["user_id"] = usuario["id_usuario"]
    session["email"] = usuario["email"]
    session["rol"] = usuario["rol"]

    perfil = get_user_profile(usuario)

    registrar_login(usuario["id_usuario"], email, "exitoso", request.remote_addr)

    access_token = create_access_token(identity=str(usuario["id_usuario"]), additional_claims={"rol": usuario["rol"]})

    return (
        jsonify(
            {
                "success": True,
                "message": "Login exitoso",
                "token": access_token,
                "usuario": {
                    "id": usuario["id_usuario"],
                    "email": usuario["email"],
                    "rol": usuario["rol"],
                    "perfil": perfil,
                },
            }
        ),
        200,
    )
