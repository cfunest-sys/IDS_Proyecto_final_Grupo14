from urllib import response
from datetime import datetime
from flask import Blueprint, redirect, render_template, request, flash, session, current_app
import requests

evaluaciones_blueprint = Blueprint("evaluaciones", __name__)


# 1. RUTA PRINCIPAL: http://127.0.0.1:8080/evaluaciones
# Acá se muestra el listado/gestión de evaluaciones
@evaluaciones_blueprint.route("/", methods=["GET"])
def listar_evaluaciones():
    response = requests.get(f"{current_app.config['BACKEND_URL']}/api/evaluaciones/todas")
    evaluaciones = []
    if response.status_code != 204:
        json_data = response.json()
        if json_data.get("body", None) != None:
            for evento in json_data.get("body", ""):
                d = datetime.strptime(evento[3][5:-4], "%d %b %Y %H:%M:%S")
                evaluaciones.append({
                    "nombre": evento[1],
                    "tipo": evento[2],
                    "fecha": d.strftime("%Y-%m-%d"),
                    "curso": evento[4]
                })

    return render_template("evaluaciones.html", evaluaciones=evaluaciones)


# 2. RUTA DEL CALENDARIO: http://127.0.0.1:8080/evaluaciones/calendario
# Acá se muestra el calendario con las evaluaciones
@evaluaciones_blueprint.route("/calendario", methods=["GET"])
def calendario_evaluaciones():
    # eventos = [{"nombre":"tp1", "tipo":"TP", "fecha": "2026-05-21", "curso":1},]

    # activar esto para probar el calendario sin iniciar sesion
    # session["rol"] = "profesor"
    # session["user_id"] = 2
    if session:
        data = {"rol": session.get("rol", ""), "user_id": session.get("user_id", "")}
    else:
        data = {}
    response = requests.get(f"{current_app.config['BACKEND_URL']}/api/evaluaciones/usuario", json=data)
    eventos = []
    if response.ok and response.status_code != 204:
        json = response.json()
        if json.get("error", "") == "":
            for evento in json["body"]:
                d = datetime.strptime(evento[3][5:-4], "%d %b %Y %H:%M:%S")
                eventos.append({
                    "nombre": evento[1],
                    "tipo": evento[2],
                    "fecha": d.strftime("%Y-%m-%d"),
                    "curso": evento[4]
                })
    mes_nombre = (
        "enero",
        "febrero",
        "marzo",
        "abril",
        "mayo",
        "junio",
        "julio",
        "agosto",
        "septiembre",
        "octubre",
        "noviembre",
        "diciembre",
    )
    año_actual = 2026
    mes_actual = 5

    dias = (31, 28 + año_actual % 4, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)

    # return render_template("prueba.html", eventos=eventos)

    return render_template(
        "calendario.html",
        mes_actual=mes_actual,
        año_actual=año_actual,
        dias=dias,
        mes_nombre=mes_nombre,
        eventos=eventos,
    )
