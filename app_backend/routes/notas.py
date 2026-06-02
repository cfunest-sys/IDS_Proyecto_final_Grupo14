from flask import Blueprint, jsonify, request

from data.queries import get_notas, get_alumno_por_usuario_id
from utils.auth import token_required

notas_bp = Blueprint("notas", __name__)


@notas_bp.route("/", methods=["GET"])
@token_required
def listar_notas(current_user):
    """Consulta notas con filtros, paginación y promedio."""
    print(
        f"[notas] consulta usuario_id={current_user['id']} rol={current_user['rol']} "
        f"alumno_id={request.args.get('alumno_id')} evaluacion_id={request.args.get('evaluacion_id')}"
    )

    rol = current_user.get("rol", "")
    if rol not in ("profesor", "alumno", "admin"):
        return jsonify({"error": "No autorizado"}), 403

    alumno_id = request.args.get("alumno_id", type=int)
    evaluacion_id = request.args.get("evaluacion_id", type=int)
    page = request.args.get("page", default=1, type=int) or 1
    per_page = request.args.get("per_page", default=10, type=int) or 10

    if rol == "alumno":
        alumno = get_alumno_por_usuario_id(current_user["id"])
        if not alumno:
            return jsonify({"error": "No se encontró el alumno asociado al usuario"}), 404

        legajo = alumno.get("legajo")
        if alumno_id is not None and alumno_id != legajo:
            return jsonify({"error": "No autorizado para consultar otras notas"}), 403

        alumno_id = legajo

    try:
        resultado = get_notas(alumno_id=alumno_id, evaluacion_id=evaluacion_id, page=page, per_page=per_page)
    except Exception as exc:
        print(f"[notas] error al consultar notas: {exc}")
        return jsonify({"error": "Error interno del servidor"}), 500

    items = resultado.get("items", [])
    total_notas = len(items)
    promedio = 0.0
    if total_notas:
        promedio = round(sum(float(item.get("calificacion", 0) or 0) for item in items) / total_notas, 2)

    return jsonify(
        {
            "items": items,
            "promedio": promedio,
            "page": resultado.get("page", page),
            "per_page": resultado.get("per_page", per_page),
            "total": resultado.get("total", total_notas),
            "pages": resultado.get("pages", 0),
        }
    ), 200
