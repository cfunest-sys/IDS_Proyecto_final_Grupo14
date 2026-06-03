import jwt
from flask import request, jsonify
from functools import wraps
from datetime import datetime, timezone
from werkzeug.security import check_password_hash, generate_password_hash
from data.queries import get_usuario_by_email
from config import JWT_SECRET_KEY, JWT_ACCESS_TOKEN_EXPIRES


# Genera los tokens JWT para los usuarios autenticados

def generate_token(usuario_id, rol):

    now = datetime.now(timezone.utc)

    payload = {
        "sub": usuario_id,
        "rol": rol,
        "iat": now,
        "exp": now + JWT_ACCESS_TOKEN_EXPIRES
    }

    token = jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm="HS256"
    )

    return token


# Valida las credenciales del profesor y genera un token JWT si son correctas

def validate_user_credentials(email, password):

    usuario = get_usuario_by_email(email)

    if not usuario:
        return None

    if check_password_hash(usuario["password"], password):

        token = generate_token(
            usuario_id=usuario["id_usuario"],
            rol=usuario["rol"]
        )

        return {
            "usuario": usuario,
            "token": token
        }

    return None




# Decorador para proteger rutas que requieren autenticación

def token_required(f):

    @wraps(f)
    def decorated(*args, **kwargs):

        auth_header = request.headers.get("Authorization")
        # Si no se proporciona el token en el encabezado de autorización, se devuelve un error 401
        if not auth_header:
            return jsonify({
                "message": "Token faltante"
            }), 401

        parts = auth_header.split()
        # Verifica formato: Bearer <token>
        if len(parts) != 2 or parts[0] != "Bearer":
            return jsonify({
                "message": "Formato de token inválido"
            }), 401

        token = parts[1]

        try:

            # Se recupera el payload del token para obtener la información del usuario autenticado
            payload = jwt.decode(
                token,
                JWT_SECRET_KEY,
                algorithms=["HS256"]
            )

            current_user = {
                "id": payload["sub"],
                "rol": payload["rol"]
            }
        # Si el token ha expirado, se devuelve un error 401 indicando que el token ha expirado
        except jwt.ExpiredSignatureError:
            return jsonify({
                "message": "Token expirado"
            }), 401
        # Si el token es inválido por cualquier otra razón, se devuelve un error 401 indicando que el token es inválido
        except jwt.InvalidTokenError:
            return jsonify({
                "message": "Token inválido"
            }), 401
        # Si el token es válido, se llama a la función decorada pasando la información del usuario autenticado como argumento
        return f(current_user, *args, **kwargs)

    return decorated



# Decorador para proteger rutas que requieren un rol específico

def rol_required(expected_role):
    def decorator(f):
        @wraps(f)
        def decorated(current_user, *args, **kwargs):

            if current_user["rol"] != expected_role:

                return jsonify({
                    "message": "Forbidden"
                }), 403

            return f(current_user, *args, **kwargs)

        return decorated

    return decorator


# Función para hashear contraseñas

def hash_password(password):
    return generate_password_hash(password)
