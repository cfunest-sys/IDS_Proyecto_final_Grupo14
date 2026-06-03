from functools import wraps
from flask import jsonify
from flask_jwt_extended import create_access_token, verify_jwt_in_request, get_jwt_identity, get_jwt
from flask_jwt_extended.exceptions import JWTExtendedException
from werkzeug.security import check_password_hash, generate_password_hash

from data.queries import get_profesor_by_email

# Genera los tokens JWT para los usuarios autenticados


def generate_token(usuario_id, rol):
    return create_access_token(identity=str(usuario_id), additional_claims={"rol": rol})


# Valida las credenciales del profesor y genera un token JWT si son correctas


def validate_profesor_credentials(email, password):
    profesor = get_profesor_by_email(email)
    if not profesor:
        return None
    if not check_password_hash(profesor["password"], password):
        return None

    token = generate_token(usuario_id=profesor["id"], rol=profesor["rol"])
    return {"profesor": profesor, "token": token}


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
