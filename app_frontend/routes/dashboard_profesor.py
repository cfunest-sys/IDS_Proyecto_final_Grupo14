from flask import Blueprint, flash, render_template, session, redirect, url_for, current_app
import requests

dashboard_bp = Blueprint(
    "dashboard",
    __name__
)

@dashboard_bp.route("/dashboard/profesor")
def dashboard_profesor():

    if session.get("rol") != "profesor":
        flash(
        "Solo los profesores tienen acceso a esta funcionalidad.",
        "warning"
        )

        return redirect("/")

    resumen = {}

    try:

        response = requests.get(
            f"{current_app.config['BACKEND_URL']}/api/dashboard/resumen",
            timeout=5
        )

        if response.ok:
            resumen = response.json()

    except Exception:
        pass

    return render_template(
        "dashboard_profesor.html",
        nombre=session.get("nombre"),
        resumen=resumen
    )