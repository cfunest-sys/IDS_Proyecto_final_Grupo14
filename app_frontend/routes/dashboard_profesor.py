from flask import Blueprint, flash, render_template, session, redirect, url_for
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
            "http://127.0.0.1:5001/api/dashboard/resumen",
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