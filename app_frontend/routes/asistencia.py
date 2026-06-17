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
                token = session.get("token", "")
                auth_headers = {"Authorization": "Bearer " + token}
                respuesta = requests.post(f"{current_app.config['BACKEND_URL']}/api/asistencia/generar-qr", 
                    timeout=15, headers=auth_headers)
                data = respuesta.json()
                if respuesta.status_code == 200:
                    codigo = data.get("qr_code")
                    public_url = current_app.config["PUBLIC_URL"]
                    if public_url:
                           base_url = public_url.rstrip("/")
                    else:
                           #EN CASO DE QUE NO HAYA UNA URL PUBLICA GENERAMOS LA RUTA CON LA IP
                           ip = obtener_ip_local()
                           base_url = f"http://{ip}:8080"
                    qr_generado = f"{base_url}/registrar-asistencia?qr={codigo}"
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