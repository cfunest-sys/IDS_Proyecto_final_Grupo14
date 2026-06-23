from urllib import response

from flask import Blueprint, jsonify, redirect, render_template, request, flash, session, current_app, url_for, send_file
import requests
import io
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
    cursos = []
    qr_generado = None
    mensaje = None
    rol = session.get("rol")

    if rol == "profesor":

        token = session.get("token", "")
        auth_headers = {
            "Authorization": f"Bearer {token}"
        }

        try:
            respuesta_cursos = requests.get(
                f"{current_app.config['BACKEND_URL']}/api/cursos",
                headers=auth_headers,
                timeout=10
            )

            if respuesta_cursos.status_code == 200:
                cursos = respuesta_cursos.json()
            else:
                print(f"Error al traer cursos: {respuesta_cursos.text}")

        except Exception as e:
            print(f"Error de conexión al buscar cursos: {str(e)}")

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

    return render_template("asistencia.html", rol=rol, qr_generado=qr_generado, mensaje=mensaje, cursos=cursos)




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
            if respuesta.ok:
                flash(data.get("message", "Asistencia registrada correctamente"),"success")
            else:
                flash( data.get("error", "Error al registrar asistencia"), "danger")

        except Exception as e:
            flash(f"Error de conexión: {str(e)}","danger")

        return redirect(
            url_for("asistencia.registrar_asistencia", qr=qr_code)
        )

    
    return render_template("registrar_asistencia.html", qr_code=qr_code)


@asistencia_bp.route("/reporte-asistencia", methods=["POST"])
def reporte_asistencia():
    #LOGICA PARA GENERAR EL REPORTE DE LA ASISTENCIA
    
    fecha = request.form.get("fecha")
    curso = request.form.get("curso")

    token = session.get("token", "")

    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:

        respuesta = requests.post(
            f"{current_app.config['BACKEND_URL']}/api/asistencia/generar-reporte",
            json={
                "fecha": fecha,
                "curso": curso
            },
            headers=headers,
            timeout=30
        )

        if respuesta.status_code != 200:
            try:
                err_msg = respuesta.json().get("error", "Error interno al generar el reporte")
            except:
                err_msg = "Error al intentar obtener el reporte"
            flash(err_msg, "danger")
            return redirect(url_for("asistencia.generar_qr"))

        return send_file(
            io.BytesIO(respuesta.content),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"reporte_asistencia_{fecha}.pdf"
        )

    except Exception as e:
        return f"Error al generar reporte: {str(e)}"
