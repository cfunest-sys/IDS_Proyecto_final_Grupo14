from urllib import response
from datetime import datetime
from flask import Blueprint, redirect, render_template, request, flash
import requests

evaluaciones_blueprint = Blueprint("evaluaciones", __name__)
# 1. RUTA PRINCIPAL: http://127.0.0.1:8080/evaluaciones
# Acá se muestra el listado/gestión de evaluaciones
@evaluaciones_blueprint.route("/", methods=["GET"])
def listar_evaluaciones():
    response = requests.get('http://127.0.0.1:5001/api/evaluaciones/todas')
    evaluaciones = []
    
    if response.status_code != 204:
        json_data = response.json()
        for eva in json_data["body"]:
            # Parseamos la fecha que viene del backend
            d = datetime.strptime(eva[3][5:-4], "%d %b %Y %H:%M:%S")
            evaluaciones.append({
                "id": eva[0],
                "nombre": eva[1],
                "tipo": eva[2],
                "fecha": d,
                "curso": eva[4]
            })
            
    return render_template("evaluaciones.html", evaluaciones=evaluaciones)

# app.config["SESSION_PERMANENT"] = False     # Sessions expire when the browser is closed
# app.config["SESSION_TYPE"] = "filesystem"   # Store session data in files
# Session(app) 								# Initialize Flask-Session
# 2. RUTA DEL CALENDARIO: http://127.0.0.1:8080/evaluaciones/calendario
# Acá se muestra el calendario con las evaluaciones
@evaluaciones_blueprint.route("/calendario", methods=["GET"])
def calendario_evaluaciones():
    # eventos = [{"nombre":"tp1", "tipo":"TP", "fecha": "2026-05-21", "curso":1},
    # {"nombre":"Primer Parcial Teórico-Práctico", "tipo":"parcial", "fecha": "2027-12-20", "curso":2},
    # {"nombre":"Trabajo Práctico Integrador Final", "tipo":"TP", "fecha": "2026-05-01", "curso":2},
    # {"nombre":"Control de Lectura - Parcialito 1", "tipo":"parcialito", "fecha": "2026-05-13", "curso":1}]
    response = requests.get('http://127.0.0.1:5001/api/evaluaciones/todas')
    json = response.json()
    eventos=[]
    if (response.status_code == 204):
    	eventos = {"error":"no hay eva para ese curso"}
    else:
    	for evento in json["body"]:
    		d=datetime.strptime(evento[3][5:-4], "%d %b %Y %H:%M:%S")
    		eventos.append({"nombre":evento[1], "tipo":evento[2], 
    			"fecha": d.strftime("%Y-%m-%d"), "curso":evento[4]})
    mes_nombre = ("enero","febrero","marzo","abril","mayo","junio","julio","agosto",
                    "septiembre","octubre","noviembre","diciembre")
    año_actual = 2026 
    mes_actual = 5
    dias=(31, 28 + año_actual % 4, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
    # return render_template("prueba.html", eventos=eventos)
    return render_template("calendario.html", mes_actual=mes_actual, 
    	año_actual=año_actual, dias=dias, mes_nombre=mes_nombre,
    	eventos=eventos)
