from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from flask_jwt_extended.exceptions import JWTExtendedException
from werkzeug.security import check_password_hash, generate_password_hash
from config import JWT_SECRET_KEY, JWT_ACCESS_TOKEN_EXPIRES

from data.queries import get_usuario_by_email

# Valida las credenciales del profesor y genera un token JWT si son correctas


def validate_user_credentials(email, password):
    usuario = get_usuario_by_email(email)
    if not usuario:
        return None
    if not check_password_hash(usuario["password"], password):
        return None
    return usuario


# Decorador para proteger rutas que requieren autenticación
def token_required(f):

    @wraps(f)
    def decorated(*args, **kwargs):

        try:
            verify_jwt_in_request()

            user_id = get_jwt_identity()
            claims = get_jwt()

            current_user = {"id": int(user_id), "rol": claims.get("rol")}
        except JWTExtendedException:
            return jsonify({"message": "Token inválido o expirado"}), 401

        return f(current_user, *args, **kwargs)

    return decorated


# Decorador para proteger rutas que requieren un rol específico


def rol_required(expected_role):
    def decorator(f):
        @wraps(f)
        def decorated(current_user, *args, **kwargs):

            if current_user["rol"] != expected_role:

                return jsonify({"message": "Forbidden"}), 403

            return f(current_user, *args, **kwargs)

        return decorated

    return decorator


# Función para hashear contraseñas
def hash_password(password):
    return generate_password_hash(password)
