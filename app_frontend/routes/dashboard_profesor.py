from flask import Blueprint, flash, render_template, session, redirect, url_for, current_app, request
import requests

dashboard_bp = Blueprint("dashboard_profesor", __name__)


@dashboard_bp.route("/dashboard/profesor")
def dashboard_profesor():

    if session.get("rol") != "profesor":
        flash("Solo los profesores tienen acceso a esta funcionalidad.", "warning")

        return redirect("/")

    resumen = {}

    try:
        token = session.get("token", "")
        auth_headers = {"Authorization": "Bearer " + token}
        curso = request.args.get("curso")

        params = {}

        if curso:
            params["curso"] = curso

        response = requests.get(
            f"{current_app.config['BACKEND_URL']}/api/dashboard/resumen",
            headers=auth_headers,
            params=params,
            timeout=5
        )

        if response.ok:
            resumen = response.json()
        response_cursos = requests.get(
        f"{current_app.config['BACKEND_URL']}/api/cursos",
        headers=auth_headers,
        timeout=5
        )

        cursos = response_cursos.json() if response_cursos.ok else []
    except Exception:
        pass

    return render_template(
        "dashboard_profesor.html",
        nombre=session.get("nombre"),
        resumen=resumen,
        cursos=cursos,
        curso_seleccionado=curso
    )
    
  

