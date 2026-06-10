from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from data.queries import crear_profesor, existe_usuario_por_email, registrar_login

profesores_bp = Blueprint("profesores", __name__)


"""@profesores_bp.route("/login", methods=["POST"])
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
        registrar_login(
        None,
        email,
        "fallido",
        request.remote_addr
    )
        return jsonify({"error": "Email o contraseña inválidos"}), 401
    registrar_login(
        profesor["profesor"]["id"],
        email,
        "exitoso",
        request.remote_addr
    )

    access_token = create_access_token(identity=str(profesor["token"]))

    return (
        jsonify(
            {
                "success": True,
                "message": "Login exitoso",
                "token": access_token,
                "profesor": {"id": profesor["profesor"]["id"], "nombre": profesor["profesor"]["nombre"], "email": profesor["profesor"]["email"]},
            }
        ),
        200,
    )"""


@profesores_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_profesor():
    profesor_id = get_jwt_identity()
    return jsonify({"profesor_id": profesor_id}), 200


@profesores_bp.route('/register', methods=['POST'])
def register():

    try:

        data = request.json


        nombre = data.get("nombre")
        email = data.get("email")
        password = data.get("password")
        departamento = data.get("departamento")


        if not nombre or not email or not password:

            return jsonify({
                "error": "Faltan datos obligatorios"
            }), 400

        profesor = {
            "nombre": nombre,
            "email": email,
            "password": password,
            "departamento": departamento
        }
        
        if existe_usuario_por_email(email):
            return jsonify({
                "error": "Ya existe una cuenta con ese email"
            }), 409

        id_profesor = crear_profesor(profesor)

        return jsonify({
            "mensaje": "Profesor registrado correctamente",
            "id": id_profesor
        }), 201

    except Exception as e:
        
        print(e)

        return jsonify({
            "error": str(e)
        }), 500
    
