from flask import Blueprint, flash, render_template, session, redirect
import requests

perfil_bp = Blueprint("perfil", __name__)


@perfil_bp.route("/perfil/alumno")
def perfil_alumno():
    if session.get("rol") != "alumno":
        flash("Solo los alumnos tienen acceso a esta funcionalidad.", "warning")
        return redirect("/")

    datos_perfil = {}
    try:
        response = requests.get(
            "http://127.0.0.1:5001/perfil",
            timeout=5
        )
        if response.ok:
            datos_perfil = response.json()
    except Exception:
        pass

    return render_template(
        "perfil_alumno.html",
        usuario=datos_perfil,
        detalle=datos_perfil.get("detalles", {})
    )


@perfil_bp.route("/perfil/profesor")
def perfil_profesor():
    if session.get("rol") != "profesor":
        flash("Solo los profesores tienen acceso a esta funcionalidad.", "warning")
        return redirect("/")

    datos_perfil = {}
    try:
        response = requests.get(
            "http://127.0.0.1:5001/perfil",
            timeout=5
        )
        if response.ok:
            datos_perfil = response.json()
    except Exception:
        pass

    return render_template(
        "perfil_profesor.html",
        usuario=datos_perfil,
        detalle=datos_perfil.get("detalles", {})
    )