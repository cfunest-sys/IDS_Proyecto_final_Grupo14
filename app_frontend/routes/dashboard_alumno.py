from flask import Blueprint, flash, render_template, session, redirect, url_for, current_app
import requests
dashboard_alumno_bp = Blueprint("dashboard_alumno", __name__)

@dashboard_alumno_bp.route("/dashboard/alumno")
def dashboard_alumno():
    if session.get("rol") != "alumno":
        flash(
            "Solo los alumnos tienen acceso a esta funcionalidad.",
            "warning"
        )
        return redirect("/")

    resumen = {}

    try:
        legajo = session.get("legajo")

        response = requests.get(
            f"{current_app.config['BACKEND_URL']}/api/dashboard/alumno/{legajo}", timeout=5)

        if response.ok:
            resumen = response.json()
    except Exception:
        pass

    return render_template("dashboard_alumno.html", nombre=session.get("nombre"), resumen=resumen)
    