import os
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file, redirect
from utils.auth import token_required, rol_required
from data.queries import (
    insertar_material,
    get_materiales,
    get_material,
    actualizar_material,
    eliminar_material,
    obtener_detalles_profesor,
    get_estadisticas_materiales,
)

materiales_bp = Blueprint("materiales", __name__)
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "..", "uploads", "materiales")
ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "xls", "xlsx", "jpg", "png", "gif", "mp4", "txt", "zip"}
MAX_FILE_SIZE = 50 * 1024 * 1024


def allowed_file(filename):
    if "." not in filename:
        return False
    extension = filename.rsplit(".", 1)[1].lower()

    return extension in ALLOWED_EXTENSIONS


# POST /api/materiales/subir
@materiales_bp.route("/subir", methods=["POST"])
@token_required
@rol_required("profesor")
def subir_material(current_user):
    profe = obtener_detalles_profesor(current_user["id"])
    if not profe:
        return jsonify({"error": "Profesor no encontrado"}), 404
    id_profesor = profe["id_profesor"]
    titulo = request.form.get("titulo", "").strip()
    descripcion = request.form.get("descripcion", "").strip()
    tipo_material = request.form.get("tipo_material", "").strip()
    id_curso = request.form.get("id_curso")
    tema = request.form.get("tema", "").strip()
    orden_material = request.form.get("orden_material", 0, type=int)
    es_externo = request.form.get("es_externo", "false").lower() in ("true", "on", "1")
    tipo_archivo = request.form.get("tipo_archivo", "").strip()
    es_libre = request.form.get("es_libre", "false").lower() in ("true", "on", "1")
    estado = request.form.get("estado", "publicado").strip()
    archivo_ruta = request.form.get("archivo_ruta", "").strip()
    fecha_material = request.form.get("fecha_material")
    tamano = None
    if not titulo or not tipo_material or not id_curso:
        return jsonify({"error": "titulo, tipo_material e id_curso son obligatorios"}), 400
    try:
        id_curso = int(id_curso)
    except (ValueError, TypeError):
        return jsonify({"error": "id_curso debe ser un número entero"}), 400
    if not es_externo:
        archivo = request.files.get("archivo")
        if archivo and archivo.filename:
            if not allowed_file(archivo.filename):
                return (
                    jsonify({"error": f"Tipo de archivo no permitido. Permitidos: {', '.join(ALLOWED_EXTENSIONS)}"}),
                    400,
                )
            # el .seek mueve el cursor al final para obtener el tamaño del archivo
            archivo.seek(0, os.SEEK_END)
            tamano = archivo.tell()
            archivo.seek(0)
            if tamano > MAX_FILE_SIZE:
                return jsonify({"error": "El archivo supera los 50MB"}), 400
            fecha_carpeta = datetime.now().strftime("%Y%m")
            carpeta = os.path.join(UPLOAD_FOLDER, fecha_carpeta)
            os.makedirs(carpeta, exist_ok=True)
            extension = archivo.filename.rsplit(".", 1)[1].lower()
            nombre_uuid = f"{uuid.uuid4().hex}.{extension}"
            archivo.save(os.path.join(carpeta, nombre_uuid))
            archivo_ruta = os.path.join("materiales", fecha_carpeta, nombre_uuid)
            tipo_archivo = extension
        elif not archivo_ruta:
            return jsonify({"error": "Debes subir un archivo o indicar una URL externa"}), 400
    id_material = insertar_material(
        id_curso=id_curso,
        id_profesor=id_profesor,
        titulo=titulo,
        descripcion=descripcion,
        tipo_material=tipo_material,
        tema=tema if tema else None,
        orden_material=orden_material,
        archivo_ruta=archivo_ruta,
        es_externo=es_externo,
        tipo_archivo=tipo_archivo if tipo_archivo else None,
        tamano_bytes=tamano if not es_externo else None,
        fecha_material=fecha_material,
        es_libre=es_libre,
        estado=estado,
    )
    if not id_material:
        return jsonify({"error": "Error al guardar el material"}), 500
    return jsonify({"success": True, "id_material": id_material, "mensaje": "Material subido correctamente"}), 201


# GET /api/materiales/estadisticas
@materiales_bp.route("/estadisticas", methods=["GET"])
@token_required
def estadisticas_materiales(current_user):
    id_curso = request.args.get("id_curso", type=int)
    id_profesor = request.args.get("id_profesor", type=int)
    if current_user["rol"] == "profesor":
        profe = obtener_detalles_profesor(current_user["id"])
        if profe and not id_profesor:
            id_profesor = profe["id_profesor"]
    stats = get_estadisticas_materiales(id_curso=id_curso, id_profesor=id_profesor)
    return jsonify(stats), 200


# GET /api/materiales/
@materiales_bp.route("/", methods=["GET"])
@token_required
def listar_materiales(current_user):
    id_curso = request.args.get("id_curso", type=int)
    id_profesor = request.args.get("id_profesor", type=int)
    tipo_material = request.args.get("tipo_material")
    tema = request.args.get("tema")
    estado = request.args.get("estado")
    es_libre = request.args.get("es_libre", type=lambda v: v.lower() == "true" if v else None)
    pagina = request.args.get("pagina", 1, type=int)
    limite = request.args.get("limite", 20, type=int)
    order_by = request.args.get("order_by", "fecha_subida")
    order_dir = request.args.get("order_dir", "DESC")
    total, materiales = get_materiales(
        id_curso=id_curso,
        id_profesor=id_profesor,
        tipo_material=tipo_material,
        tema=tema,
        estado=estado,
        es_libre=es_libre,
        pagina=pagina,
        limite=limite,
        order_by=order_by,
        order_dir=order_dir,
    )
    paginas_totales = max(1, (total + limite - 1) // limite)
    for m in materiales:
        for k, v in m.items():
            if isinstance(v, datetime):
                m[k] = v.isoformat()
    return jsonify({"total": total, "pagina": pagina, "limite": limite, "paginas_totales": paginas_totales, "materiales": materiales}), 200


# GET /api/materiales/<id>/descargar
@materiales_bp.route("/<int:id_material>/descargar", methods=["GET"])
@token_required
def descargar_material(current_user, id_material):
    material = get_material(id_material)
    if not material:
        return jsonify({"error": "Material no encontrado"}), 404
    if material["es_externo"]:
        url = material["archivo_ruta"]
        if not (url.startswith("http://") or url.startswith("https://")):
            return jsonify({"error": "URL externa inválida"}), 400
        return redirect(url)
    ruta_completa = os.path.join(UPLOAD_FOLDER, material["archivo_ruta"].replace("materiales/", ""))
    if not os.path.exists(ruta_completa):
        return jsonify({"error": "Archivo no encontrado en servidor"}), 404
    return send_file(ruta_completa, as_attachment=True, download_name=material.get("titulo", "archivo"))


# PUT /api/materiales/<id>
@materiales_bp.route("/<int:id_material>", methods=["PUT"])
@token_required
@rol_required("profesor")
def editar_material(current_user, id_material):
    material = get_material(id_material)
    if not material:
        return jsonify({"error": "Material no encontrado"}), 404
    profe = obtener_detalles_profesor(current_user["id"])
    if not profe or profe["id_profesor"] != material["id_profesor"]:
        return jsonify({"error": "No tienes permiso para editar este material"}), 403
    data = request.get_json()
    if not data:
        return jsonify({"error": "No se enviaron datos"}), 400
    allowed_fields = {
        "titulo",
        "descripcion",
        "tema",
        "fecha_material",
        "estado",
        "orden_material",
        "es_libre",
        "tipo_material",
    }
    updates = {k: v for k, v in data.items() if k in allowed_fields}
    if not updates:
        return jsonify({"error": "No hay campos válidos para actualizar"}), 400
    actualizado = actualizar_material(id_material, **updates)
    if not actualizado:
        return jsonify({"error": "No se pudo actualizar el material"}), 500
    return jsonify({"success": True, "mensaje": "Material actualizado correctamente"}), 200


# DELETE /api/materiales/<id>
@materiales_bp.route("/<int:id_material>", methods=["DELETE"])
@token_required
@rol_required("profesor")
def borrar_material(current_user, id_material):
    material = get_material(id_material)
    if not material:
        return jsonify({"error": "Material no encontrado"}), 404
    profe = obtener_detalles_profesor(current_user["id"])
    if not profe or profe["id_profesor"] != material["id_profesor"]:
        return jsonify({"error": "No tienes permiso para eliminar este material"}), 403
    eliminado = eliminar_material(id_material)
    if not eliminado:
        return jsonify({"error": "No se pudo eliminar el material"}), 500
    return jsonify({"success": True, "mensaje": "Material eliminado correctamente"}), 200


#Función auxiliar para obtener los cursos
@materiales_bp.route("/cursos-profesor", methods=["GET"])
@token_required
@rol_required("profesor")
def obtener_cursos_profesor(current_user):
    id_profesor = current_user["id"]
