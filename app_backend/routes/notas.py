from flask import Blueprint, request, jsonify
from utils.auth import token_required 
from data.queries import (
    get_notas_filtradas, 
    get_promedio_notas, 
    verificar_alumno_evaluacion, 
    guardar_actualizar_nota,
    get_connection
)

notas_bp = Blueprint('notas', __name__)

@notas_bp.route('/notas', methods=['GET'])
@token_required
def listar_notas(current_user): 
    try:
        usuario_id = current_user.get('id')
        rol = current_user.get('rol')

        legajo_alumno = request.args.get('legajo_alumno', type=int)
        id_evaluacion = request.args.get('id_evaluacion', type=int)
        id_curso = request.args.get('id_curso', type=int)

        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=10, type=int)
        
        if page < 1: page = 1
        if per_page < 1: per_page = 10
        offset = (page - 1) * per_page

        notas = get_notas_filtradas(rol, usuario_id, legajo_alumno, id_evaluacion, id_curso, per_page, offset)
        promedio = get_promedio_notas(rol, usuario_id, legajo_alumno, id_evaluacion, id_curso)

        for nota in notas:
            if nota['fecha']:
                nota['fecha'] = nota['fecha'].strftime('%Y-%m-%d') if hasattr(nota['fecha'], 'strftime') else str(nota['fecha'])

        return jsonify({
            "page": page,
            "per_page": per_page,
            "promedio": promedio,
            "notas": notas
        }), 200

    except Exception as e:
        print(f"Error en GET /notas: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500

@notas_bp.route('/notas', methods=['POST'])
@token_required
def cargar_nota(current_user):
    try:
        if current_user.get('rol') != 'profesor':
            return jsonify({"error": "Acceso denegado. Solo profesores."}), 403

        data = request.get_json()
        if not data:
            return jsonify({"error": "Body vacío"}), 400

        legajo_alumno = data.get('legajo_alumno')
        id_evaluacion = data.get('id_evaluacion')
        calificacion = data.get('calificacion')

        if legajo_alumno is None or id_evaluacion is None or calificacion is None:
            return jsonify({"error": "Faltan campos obligatorios"}), 400

        try:
            calificacion = float(calificacion)
            if calificacion < 0 or calificacion > 10:
                return jsonify({"error": "Calificación debe ser 0 a 10"}), 400
        except (ValueError, TypeError):
            return jsonify({"error": "Calificación inválida"}), 400

        if not verificar_alumno_evaluacion(legajo_alumno, id_evaluacion):
            return jsonify({"error": "Alumno o evaluación no existe"}), 404

        nota = guardar_actualizar_nota(legajo_alumno, id_evaluacion, calificacion)

        fecha_respuesta = None
        if nota and nota.get('fecha'):
            fecha_respuesta = nota['fecha'].strftime('%Y-%m-%d') if hasattr(nota['fecha'], 'strftime') else str(nota['fecha'])

        print(f"LOG - [{fecha_respuesta}] Profesor {current_user.get('id')} actualizó nota alumno {legajo_alumno}")
        print(f"NOTIFICACIÓN - Alumno {legajo_alumno}: nota registrada")

        return jsonify({
            "mensaje": "Nota guardada correctamente",
            "nota": {
                "legajo_alumno": nota.get("legajo_alumno"),
                "id_evaluacion": nota.get("id_evaluacion"),
                "calificacion": nota.get("calificacion"),
                "fecha": fecha_respuesta
            }
        }), 201

    except Exception as e:
        print(f"Error en cargar-nota: {e}")
        return jsonify({"error": "Error interno"}), 500

@notas_bp.route('/resumen-promedios', methods=['GET'])
@token_required
def resumen_promedios(current_user):
    # Solo profesores o administradores
    if current_user.get('rol') not in ['profesor', 'admin']:
        return jsonify({"error": "Acceso denegado. Solo para personal docente o administración."}), 403

    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        
        # Consulta que trae todas las notas junto con el nombre del alumno y el tipo de evaluación
        cur.execute("""
            SELECT 
                a.legajo AS padron, 
                a.nombre AS alumno, 
                e.tipo AS tipo_evaluacion, 
                n.calificacion AS nota
            FROM notas n
            INNER JOIN alumnos a ON n.legajo_alumno = a.legajo
            INNER JOIN evaluaciones e ON n.id_evaluacion = e.id_evaluacion
        """)
        notas_crudas = cur.fetchall()
        
        # Procesamos las notas para calcular promedios por alumno y categoría
        alumnos_dict = {}
        for fila in notas_crudas:
            padron = fila["padron"]
            alumno = fila["alumno"]
            tipo = fila["tipo_evaluacion"]
            nota = fila["nota"]
            
            if nota is None:
                continue
                
            if padron not in alumnos_dict:
                alumnos_dict[padron] = {
                    "padron": padron,
                    "nombre": alumno,
                    "tps": [],
                    "parciales": [],
                    "parcialitos": []
                }
            
            tipo_lower = tipo.lower() if tipo else ""
            if "tp" in tipo_lower or "trabajo" in tipo_lower:
                alumnos_dict[padron]["tps"].append(float(nota))
            elif "parcialito" in tipo_lower:
                alumnos_dict[padron]["parcialitos"].append(float(nota))
            elif "parcial" in tipo_lower:
                alumnos_dict[padron]["parciales"].append(float(nota))
                
        # Calculamos promedios y condición final para cada alumno        
        resultado = []
        for padron, datos in alumnos_dict.items():
            prom_tp = sum(datos["tps"]) / len(datos["tps"]) if datos["tps"] else None
            prom_parcial = sum(datos["parciales"]) / len(datos["parciales"]) if datos["parciales"] else None
            prom_parcialito = sum(datos["parcialitos"]) / len(datos["parcialitos"]) if datos["parcialitos"] else None
            
            categorias_validas = [p for p in [prom_tp, prom_parcial, prom_parcialito] if p is not None]
            prom_final = sum(categorias_validas) / len(categorias_validas) if categorias_validas else 0.0

            resultado.append({
                "padron": padron,
                "nombre": datos["nombre"],
                "prom_tp": round(prom_tp, 2) if prom_tp is not None else "-",
                "prom_parcial": round(prom_parcial, 2) if prom_parcial is not None else "-",
                "prom_parcialito": round(prom_parcialito, 2) if prom_parcialito is not None else "-",
                "prom_final": round(prom_final, 2),
                "condicion": "Aprobado" if prom_final >= 4 else "Insuficiente"
            })
            
        return jsonify(resultado), 200

    except Exception as e:
        print(f"Error en resumen-promedios: {e}")
        return jsonify({"error": "Error interno al calcular promedios"}), 500
    finally:
        if cur: cur.close()
        if conn: conn.close()