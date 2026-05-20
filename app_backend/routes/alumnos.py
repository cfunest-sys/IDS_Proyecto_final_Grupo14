from flask import Flask, jsonify, render_template
from flask import Blueprint
from database.db import get_connection

alumnos_bp = Blueprint('alumnos', __name__)

@alumnos_bp.route('/login', methods=['POST'])
def login():
    # Hace falta agregar la lógica para el inicio de sesión
    return 'Inicio de sesión exitoso'

@alumnos_bp.route('/register', methods=['POST'])
def register():
    # Hace falta agregar la lógica para el registro de usuarios
    return 'Registro exitoso'

@alumnos_bp.route('/equipos', methods=['GET'])
def obtener_todos_equipos():
    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("SELECT * FROM equipos")
        equipos = cursor.fetchall()

        if equipos:
            return render_template('equipos.html', lista_equipos=equipos), 200
        return render_template('equipos.html', mensaje_error="No hay equipos aún"), 404
    
    except Exception as e:
        print(e)
        return render_template('error_500.html'), 500
    
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()    

