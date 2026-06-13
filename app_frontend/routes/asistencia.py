from urllib import response

from flask import Blueprint, jsonify, redirect, render_template, request, flash, session, current_app
import requests

import socket
#FUNCION PARA OBTENER LA IP PARA EL REGISTRO DE LA ASISTENICA EN EL QR
def obtener_ip_local():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip


asistencia_bp = Blueprint("asistencia",__name__)

@asistencia_bp.route("/asistencia", methods=["GET", "POST"])
def generar_qr():
    # LOGICA SOLO PARA LA GENERACION DE QR
    qr_generado = None
    mensaje = None
    rol = session.get("rol")
    if request.method == "POST":
        if rol == "profesor":
            try:
                respuesta = requests.post(f"{current_app.config['BACKEND_URL']}/api/asistencia/generar-qr", timeout=15)
                data = respuesta.json()
                if respuesta.status_code == 200:
                    codigo = data.get("qr_code")
                    ip = obtener_ip_local()
                    qr_generado = (f"http://{ip}:8080/" f"registrar-asistencia?qr={codigo}")
                else:
                    mensaje = data.get("error")
            except Exception as e:
                mensaje = str(e)

    return render_template("asistencia.html", rol=rol, qr_generado=qr_generado, mensaje=mensaje)





@asistencia_bp.route("/registrar-asistencia", methods=["GET", "POST"])
def registrar_asistencia():
# LOGICA PARA REGISTRAR QR
    mensaje = None
    qr_code = request.args.get("qr")
    if request.method == "POST":

        legajo = request.form.get("legajo")
        qr_code = request.form.get("qr_code")

        try:
            respuesta = requests.post( f"{current_app.config['BACKEND_URL']}/api/asistencia/registrar", json={"legajo": legajo, "qr_code": qr_code}, timeout=15)

            data = respuesta.json()

            mensaje = data.get("message") or data.get("error")

        except Exception as e:
            mensaje = str(e)
    
    return render_template("registrar_asistencia.html", qr_code=qr_code, mensaje=mensaje)