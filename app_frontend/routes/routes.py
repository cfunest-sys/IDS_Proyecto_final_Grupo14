from flask import Blueprint, jsonify, redirect, render_template, request, flash, session, current_app
import requests

inicio = Blueprint("inicio", __name__)


@inicio.route("/")
def index():
    return render_template("inicio.html")


@inicio.route("/asistencia", methods=["GET", "POST"])
def asistencia():
    # LOGICA SOLO PARA LA GENERACION DE QR
    qr_generado = None
    mensaje = None
    rol = session.get("rol")
    if request.method == "POST":
        if rol == "profesor":
            try:

                respuesta = requests.post(f"{current_app.config['BACKEND_URL']}/api/asistencia/generar-qr")
                data = respuesta.json()
                if respuesta.status_code == 200:
                    codigo = data.get("qr_code")
                    qr_generado = f"http://localhost:8080/" f"registrar-asistencia?qr={codigo}"
                else:
                    mensaje = data.get("error")
            except Exception as e:
                mensaje = str(e)

    return render_template("asistencia.html", rol=rol, qr_generado=qr_generado, mensaje=mensaje)


@inicio.route("/reportes")
def reportes():
    return render_template("reportes.html")


@inicio.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        nombre = request.form.get("nombre")
        email = request.form.get("email")
        password = request.form.get("password")
        departamento = request.form.get("departamento")

        data = {"nombre": nombre, "email": email, "password": password, "departamento": departamento}

        response = requests.post(f"{current_app.config['BACKEND_URL']}/api/profesores/register", json=data, timeout=5)

        if response.status_code == 201:
            flash(
                "Usuario registrado correctamente",
                "success"
            )
            return redirect("/")

        elif response.status_code == 409:

            return render_template(
                "registro.html",
                error="Ya existe una cuenta con ese email"
            )

        return render_template(
            "registro.html",
            error="No se pudo registrar el profesor"
        )

    return render_template("registro.html")


@inicio.route("/material")
def material():
    materiales = []
    token = ""
    return render_template("materiales_profesor.html", materiales=materiales, token=token)


@inicio.route("/material/alumno")
def material_alumno():
    materiales = [
        {
            "id_material": 1,
            "titulo": "Apunte Clase 1 - Introducción",
            "descripcion": "Primer apunte del curso con conceptos básicos",
            "tipo_material": "apunte",
            "tema": "Introducción",
            "fecha_material": "2026-05-20",
            "estado": "publicado",
            "es_libre": False,
        },
        {
            "id_material": 2,
            "titulo": "Guía de Ejercicios N°1",
            "descripcion": "Ejercicios resueltos de la primera semana",
            "tipo_material": "guia",
            "tema": "Ejercicios",
            "fecha_material": "2026-05-22",
            "estado": "publicado",
            "es_libre": False,
        },
        {
            "id_material": 3,
            "titulo": "Video - Clase Grabada 1",
            "descripcion": "Grabación de la primera clase del curso",
            "tipo_material": "video",
            "tema": "Introducción",
            "fecha_material": "2026-05-20",
            "estado": "publicado",
            "es_libre": False,
        },
        {
            "id_material": 4,
            "titulo": "Guía de Python Básico",
            "descripcion": "Recopilación de conceptos de Python para principiantes",
            "tipo_material": "bibliografia",
            "tema": "Python",
            "fecha_material": "2026-05-25",
            "estado": "publicado",
            "es_libre": True,
        },
    ]
    return render_template("materiales_alumno.html", materiales=materiales, token="")


@inicio.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        data = {"email": email, "password": password}

        response = requests.post(f"{current_app.config['BACKEND_URL']}/api/login", json=data, timeout=5)

        if response.ok:

            resultado = response.json()
            usuario = resultado["usuario"]

            session["user_id"] = usuario["id"]
            session["email"] = usuario["email"]
            session["rol"] = usuario["rol"]
            session["token"] = resultado.get("token", "") 

            if usuario.get("perfil"):
                session["nombre"] = usuario["perfil"].get("nombre")

            flash("Login exitoso", "success")

            if usuario["rol"] == "profesor":
                return redirect("/dashboard/profesor")

            return redirect("/")

        return render_template("login.html", error="No se pudo iniciar sesión")

    return render_template("login.html")


@inicio.route("/sesion")
def ver_sesion():

    return {
        "user_id": session.get("user_id"),
        "email": session.get("email"),
        "rol": session.get("rol"),
        "nombre": session.get("nombre"),
    }


@inicio.route("/logout", methods=["GET"])
def logout():

    if not session.get("user_id"):
        flash("No hay una sesión iniciada.", "warning")
        return redirect("/")

    session.clear()

    flash("Sesión cerrada correctamente.", "success")

    return redirect("/")


@inicio.route("/alumnos/cargar-csv", methods=["POST"])
def cargar_csv():
    archivo = request.files.get("archivo")
    if not archivo:
        flash("No se envió archivo", "danger")
        return redirect("/alumnos")
    resp = requests.post(
        f"{current_app.config['BACKEND_URL']}/api/alumnos/cargar-csv",
        files={"archivo": (archivo.filename, archivo.stream, archivo.content_type)},
        timeout=30,
    )
    if resp.ok:
        data = resp.json()
        exitosos = data.get("exitosos", 0)
        errores = data.get("errores", [])
        flash(f"Se cargaron {exitosos} alumnos correctamente", "success")
        if errores:
            for e in errores:
                flash(f"Fila {e['fila']}: {e['motivo']}", "danger")
    else:
        flash("Error al cargar el archivo", "danger")
    return redirect("/alumnos")


@inicio.route("/registrar-asistencia", methods=["GET", "POST"])
def registrar_asistencia():
    # LOGICA PARA REGISTRAR QR
    mensaje = None

    qr_code = request.args.get("qr")

    if request.method == "POST":

        legajo = request.form.get("legajo")
        qr_code = request.form.get("qr_code")

        try:

            respuesta = requests.post(
                f"{current_app.config['BACKEND_URL']}/api/asistencia/registrar",
                json={"legajo": legajo, "qr_code": qr_code},
            )

            data = respuesta.json()

            mensaje = data.get("message") or data.get("error")

        except Exception as e:

            mensaje = str(e)

    return render_template("registrar_asistencia.html", qr_code=qr_code, mensaje=mensaje)

