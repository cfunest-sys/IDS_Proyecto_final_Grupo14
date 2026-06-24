from flask import Blueprint, flash, render_template, session, redirect, current_app, request
import requests

perfil_bp = Blueprint("perfil", __name__)



@perfil_bp.route("/perfil/profesor")
def perfil_profesor():
   if session.get("rol") != "profesor":
       flash("Solo los profesores tienen acceso a esta funcionalidad.", "warning")
       return redirect("/")

   token = session.get("token", "")
   headers = {"Authorization": f"Bearer {token}"}
   datos_perfil = {}

   try:
       response = requests.get(f"{current_app.config['BACKEND_URL']}/api/perfil/", headers=headers, timeout=5)
       if response.ok:
                    datos_perfil = response.json()
                    MESES = {
                        'Jan':'01','Feb':'02','Mar':'03','Apr':'04','May':'05','Jun':'06',
                        'Jul':'07','Aug':'08','Sep':'09','Oct':'10','Nov':'11','Dec':'12'
                    }
           
                    detalles = datos_perfil.get("detalles", {})
                    for ev in detalles.get("evaluaciones", []):
                        if isinstance(ev.get("fecha"), str):
                            partes = ev["fecha"].split(' ')   # ['Mon,', '23', 'Jun', '2025', '00:00:00', 'GMT']
                            dia = partes[1]
                            mes = MESES.get(partes[2], '??')
                            anio = partes[3]
                            ev["fecha"] = f"{dia}/{mes}/{anio}"
       else:
           flash("Error al cargar el perfil", "danger")
           return redirect("/")
   except requests.exceptions.RequestException:
       flash("Error de conexión con el servidor", "danger")
       return redirect("/")

   return render_template(
       "perfil_profesor.html",
       usuario=datos_perfil,
       detalle=datos_perfil.get("detalles", {})
   )


@perfil_bp.route("/perfil/contrasena", methods=["POST"])
def cambiar_contrasena():
   try:
       response = requests.put(
           f"{current_app.config['BACKEND_URL']}/api/perfil/contrasena/",
           headers={"Authorization": f"Bearer {session.get('token')}"},
           json={
               "contrasena_actual": request.form.get("contrasena_actual"),
               "contrasena_nueva": request.form.get("contrasena_nueva")
           },
           timeout=5
       )
       if response.ok:
           flash("Contraseña actualizada correctamente.", "success")
       else:
           flash(response.json().get("error", "Error al actualizar."), "danger")
   except Exception as e:
       flash(str(e), "danger")
   return redirect(request.referrer)


@perfil_bp.route("/perfil/editar", methods=["POST"])
def editar_perfil():
   try:
       rol = session.get("rol")
       body = {
           "nombre": request.form.get("nombre"),
           "email": request.form.get("email")
       }
       if rol == "alumno":
           body["apellido"] = request.form.get("apellido")
       elif rol == "profesor":
           body["departamento"] = request.form.get("departamento")

       response = requests.put(
           f"{current_app.config['BACKEND_URL']}/api/perfil/editar/",
           headers={"Authorization": f"Bearer {session.get('token')}"},
           json=body,
           timeout=5
       )
       if response.ok:
           flash("Perfil actualizado correctamente.", "success")
       else:
           flash(response.json().get("error", "Error al actualizar."), "danger")
   except Exception as e:
       flash(str(e), "danger")
   return redirect(request.referrer)


