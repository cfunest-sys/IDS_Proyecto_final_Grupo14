from flask import Blueprint, render_template, flash
import requests

notas_blueprint = Blueprint("notas_blueprint", __name__)

BACKEND_URL = "http://127.0.0.1:5001/api/notas"

@notas_blueprint.route("/", methods=["GET"])
def ver_notas():
    resumen_promedios = []
    try:
        response = requests.get(f"{BACKEND_URL}/resumen-promedios", timeout=5)
        if response.ok:
            resumen_promedios = response.json()
        else:
            flash("No se pudieron procesar las actas académicas", "warning")
    except requests.exceptions.RequestException:
        flash("El servidor de datos (Backend) no responde", "danger")

    return render_template("notas.html", resumen=resumen_promedios)
