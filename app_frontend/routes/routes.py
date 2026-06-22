from flask import Blueprint, jsonify, redirect, render_template, request, flash, session, current_app
import requests

inicio = Blueprint("inicio", __name__)


@inicio.route("/")
def index():
    rol = session.get("rol")
    return render_template("inicio.html", rol=rol)


@inicio.route("/reportes")
def reportes():
    token = session.get("token", "")

    headers = {
        "Authorization": f"Bearer {token}"
    }

    id_curso = request.args.get("id_curso")
    cursos = []

    try:
        response = requests.get(
            f"{current_app.config['BACKEND_URL']}/api/cursos",
            headers=headers,
            timeout=5
        )
        if response.ok:
            cursos = response.json()

    except requests.exceptions.RequestException:
        pass

    return render_template(
        "reportes.html",
        cursos=cursos,
        id_curso=id_curso
    )


@inicio.route("/reportes/<tipo>")
def descargar_reporte(tipo):
    try:
        token = session.get("token", "")
        auth_headers = {
            "Authorization": "Bearer " + token
        }
        id_curso = request.args.get("id_curso")
        url = f"{current_app.config['BACKEND_URL']}/api/reportes/{tipo}"
        params = {}
        if id_curso:
            params["id_curso"] = id_curso

        resp = requests.get(
            url,
            params=params,
            timeout=30,
            headers=auth_headers
        )

        return (
            resp.content,
            resp.status_code,
            {
                "Content-Type": resp.headers.get(
                    "Content-Type",
                    "application/pdf"
                )
            }
        )

    except requests.exceptions.RequestException:

        flash(
            "Error al descargar el reporte",
            "danger"
        )

        return redirect("/reportes")


@inicio.route("/register", methods=["GET", "POST"])
def register():
    if session.get("rol") != "admin":
        return redirect("/")

    if request.method == "POST":

        nombre = request.form.get("nombre")
        email = request.form.get("email")
        password = request.form.get("password")
        departamento = request.form.get("departamento")

        data = {"nombre": nombre, "email": email, "password": password, "departamento": departamento}

        try:
            response = requests.post(f"{current_app.config['BACKEND_URL']}/api/profesores/register", json=data, timeout=5)
        except requests.exceptions.RequestException:
            return render_template("registro.html", error="Error de conexión con el servidor")

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
    token = session.get("token", "")
    headers = {"Authorization": f"Bearer {token}"}
    pagina = request.args.get("pagina", 1, type=int)
    limite = request.args.get("limite", 12, type=int)
    order_by = request.args.get("order_by", "fecha_subida")
    order_dir = request.args.get("order_dir", "DESC")
    id_curso = request.args.get("id_curso", type=int)
    materiales = []
    total = 0
    paginas_totales = 1
    try:
        params = {"pagina": pagina, "limite": limite, "order_by": order_by, "order_dir": order_dir}
        if id_curso:
            params["id_curso"] = id_curso
        response = requests.get(f"{current_app.config['BACKEND_URL']}/api/materiales", headers=headers, params=params, timeout=5)
        if response.ok:
            data = response.json()
            materiales = data.get("materiales", [])
            total = data.get("total", 0)
            paginas_totales = data.get("paginas_totales", 1)
    except requests.exceptions.RequestException:
        flash("Error al cargar materiales", "danger")
    cursos = []
    try:
        resp_curso = requests.get(f"{current_app.config['BACKEND_URL']}/api/perfil/", headers=headers, timeout=5)
        if resp_curso.ok:
            data = resp_curso.json()
            detalle = data.get("detalles", {})
            if detalle:
                cursos = detalle.get("cursos_asignados", [])
    except requests.exceptions.RequestException:
        pass
    stats = {}
    try:
        resp_stats = requests.get(f"{current_app.config['BACKEND_URL']}/api/materiales/estadisticas", headers=headers, timeout=5)
        if resp_stats.ok:
            stats = resp_stats.json()
    except requests.exceptions.RequestException:
        pass
    return render_template("materiales_profesor.html", materiales=materiales, token=token, cursos=cursos, stats=stats, pagina=pagina, limite=limite, total=total, paginas_totales=paginas_totales, order_by=order_by, order_dir=order_dir, id_curso=id_curso)


@inicio.route("/material/subir", methods=["POST"])
def subir_material():
    token = session.get("token", "")
    if not token:
        flash("Debe iniciar sesión", "danger")
        return redirect("/material")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        files = {}
        for key in request.files:
            f = request.files[key]
            if f.filename:
                files[key] = (f.filename, f.stream, f.content_type)
        resp = requests.post(
            f"{current_app.config['BACKEND_URL']}/api/materiales/subir",
            headers=headers,
            data=request.form,
            files=files,
            timeout=30,
        )
        if resp.ok:
            flash("Material subido correctamente", "success")
        else:
            error_msg = resp.json().get("error", "Error al subir material")
            flash(error_msg, "danger")
    except requests.exceptions.RequestException:
        flash("Error de conexión con el servidor", "danger")
    return redirect("/material")


@inicio.route("/material/<int:id_material>/descargar")
def descargar_material(id_material):
    token = session.get("token", "")
    if not token:
        flash("Debe iniciar sesión", "danger")
        return redirect("/material")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = requests.get(
            f"{current_app.config['BACKEND_URL']}/api/materiales/{id_material}/descargar",
            headers=headers,
            timeout=30,
            stream=True,
        )
        if resp.ok:
            return resp.content, resp.status_code, {"Content-Type": resp.headers.get("Content-Type", "application/octet-stream")}
        flash("Error al descargar el material", "danger")
    except requests.exceptions.RequestException:
        flash("Error de conexión con el servidor", "danger")
    return redirect("/material")


@inicio.route("/material/<int:id_material>/editar", methods=["POST"])
def editar_material(id_material):
    token = session.get("token", "")
    if not token:
        flash("Debe iniciar sesión", "danger")
        return redirect("/material")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    es_libre = request.form.get("es_libre", "false").lower() in ("true", "on", "1")
    payload = {
        "titulo": request.form.get("titulo", "").strip(),
        "descripcion": request.form.get("descripcion", "").strip(),
        "tipo_material": request.form.get("tipo_material", "").strip(),
        "tema": request.form.get("tema", "").strip(),
        "estado": request.form.get("estado", "publicado").strip(),
        "es_libre": es_libre,
    }
    try:
        resp = requests.put(
            f"{current_app.config['BACKEND_URL']}/api/materiales/{id_material}",
            headers=headers,
            json=payload,
            timeout=30,
        )
        if resp.ok:
            flash("Material actualizado correctamente", "success")
        else:
            error_msg = resp.json().get("error", "Error al actualizar material")
            flash(error_msg, "danger")
    except requests.exceptions.RequestException:
        flash("Error de conexión con el servidor", "danger")
    return redirect("/material")


@inicio.route("/material/<int:id_material>/eliminar")
def eliminar_material(id_material):
    token = session.get("token", "")
    if not token:
        flash("Debe iniciar sesión", "danger")
        return redirect("/material")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = requests.delete(
            f"{current_app.config['BACKEND_URL']}/api/materiales/{id_material}",
            headers=headers,
            timeout=30,
        )
        if resp.ok:
            flash("Material eliminado correctamente", "success")
        else:
            error_msg = resp.json().get("error", "Error al eliminar material")
            flash(error_msg, "danger")
    except requests.exceptions.RequestException:
        flash("Error de conexión con el servidor", "danger")
    return redirect("/material")




@inicio.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        data = {"email": email, "password": password}

        try:
            response = requests.post(f"{current_app.config['BACKEND_URL']}/api/login", json=data, timeout=5)
        except requests.exceptions.RequestException:
            return render_template("login.html", error="Error de conexión con el servidor")

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
        flash("Email o contraseña incorrectos", "warning")
        return render_template("login.html", error="No se pudo iniciar sesión")

    return render_template("login.html")




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
    try:
        token = session.get("token", "")
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.post(
            f"{current_app.config['BACKEND_URL']}/api/alumnos/cargar-csv",
            headers=headers,
            files={"archivo": (archivo.filename, archivo.stream, archivo.content_type)},
            timeout=30,
        )
    except requests.exceptions.RequestException:
        flash("Error de conexión con el servidor", "danger")
        return redirect("/alumnos")
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


@inicio.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")
        data = {"email": email}

        try:
            
            response = requests.post(
                f"{current_app.config['BACKEND_URL']}/api/auth/forgot-credentials", 
                json=data, 
                timeout=5
            )
        except requests.exceptions.RequestException:
            return render_template("olvido_contraseña.html", error="Error de conexión con el servidor")

        if response.status_code == 200:
            flash("Token generado. Revise su correo electrónico.", "success")
            # Redirigimos al formulario donde pondra el token y la nueva contraseña
            return redirect("/reset-password")
        
        elif response.status_code == 404:
            return render_template("olvido_contraseña.html", error="No existe un usuario con ese email")

        return render_template("olvido_contraseña.html", error="Ocurrió un error inesperado")

    return render_template("olvido_contraseña.html")


@inicio.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        token = request.form.get("token")
        nueva_password = request.form.get("nueva_password")
        
        data = {
            "token": token,
            "nueva_password": nueva_password
        }

        try:
            
            response = requests.patch(
                f"{current_app.config['BACKEND_URL']}/api/auth/reset-password-with-token", 
                json=data, 
                timeout=5
            )
        except requests.exceptions.RequestException:
            return render_template("reset_contraseña.html", error="Error de conexión con el servidor")

        if response.status_code == 200:
            flash("Contraseña actualizada correctamente. Ya puede iniciar sesión.", "success")
            return redirect("/login")
        
        elif response.status_code == 404:
            return render_template("reset_contraseña.html", error="Token inválido o ya utilizado")

        return render_template("reset_contraseña.html", error="No se pudo actualizar la contraseña")

    return render_template("reset_contraseña.html")
