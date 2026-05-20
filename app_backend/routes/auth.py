from flask import Blueprint, request, jsonify
from database.db import get_connection
import random
import string

auth_bp = Blueprint("auth", __name__)

def generar_token(longitud=32):
    caracteres = string.ascii_letters + string.digits
    token = ""
    for _ in range(longitud):
        token += random.choice(caracteres)
    return token

def simular_envio_email(destinatario, token):
    print("=" * 60)
    print("SIMULACIÓN DE ENVIO DE EMAIL")
    print("Para:", destinatario)
    print("Asunto: Recuperación de contraseña")
    print("Token:", token)
    print("=" * 60)


@auth_bp.route("/api/auth/forgot-credentials", methods=["POST"])
def forgot_credentials():
    conn = None
    cur = None

    try:
        datos = request.get_json()

        if not datos or "email" not in datos:
            return jsonify({"error": "Debe enviar el email."}), 400

        email = datos["email"]

        conn = get_connection()
        cur = conn.cur(dictionary=True)

        cur.execute("""
            SELECT id_usuario
            FROM usuarios
            WHERE email = %s
        """, (email,))
        usuario = cur.fetchone()

        if not usuario:
            return jsonify({"error": "No existe un usuario con ese email."}), 404

        token = generar_token()

        cur.execute("""
            INSERT INTO password_reset_tokens (id_usuario, token, usado)
            VALUES (%s, %s, FALSE)
        """, (usuario["id_usuario"], token))

        conn.commit()

        # SIMULA EL ENVÍO DEL MAIL, A REVISAR CON EL PROFE
        simular_envio_email(email, token)

        return jsonify({
            "mensaje": "Se generó el token y se simuló el envío del correo."
        }), 200

    except Exception as e:
        print(e)
        return jsonify({"error": "Error interno del servidor."}), 500

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@auth_bp.route("/api/auth/reset-password-with-token", methods=["PATCH"])
def reset_password_with_token():
    conn = None
    cur = None

    try:
        datos = request.get_json()

        if not datos:
            return jsonify({"error": "Body vacío."}), 400

        if "token" not in datos or "nueva_password" not in datos:
            return jsonify({"error": "Faltan campos obligatorios."}), 400

        token = datos["token"]
        nueva_password = datos["nueva_password"]

        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        cur.execute("""
            SELECT id_usuario
            FROM password_reset_tokens
            WHERE token = %s AND usado = FALSE
        """, (token,))
        registro = cur.fetchone()

        if not registro:
            return jsonify({"error": "Token inválido o ya utilizado."}), 404

        cur.execute("""
            UPDATE usuarios
            SET contraseña = %s
            WHERE id_usuario = %s
        """, (nueva_password, registro["id_usuario"]))

        cur.execute("""
            UPDATE password_reset_tokens
            SET usado = TRUE
            WHERE token = %s
        """, (token,))

        conn.commit()

        return jsonify({
            "mensaje": "Contraseña actualizada correctamente."
        }), 200

    except Exception as e:
        print(e)
        return jsonify({"error": "Error interno del servidor"}), 500

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
