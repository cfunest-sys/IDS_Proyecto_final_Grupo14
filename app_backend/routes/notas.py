from flask import Blueprint, request, jsonify
from utils.auth import token_required 
from data.queries import (
    get_notas_filtradas, 
    get_promedio_notas, 
    verificar_alumno_evaluacion, 
    guardar_actualizar_nota,
    get_connection,
    get_categorias_evaluacion_por_curso
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
    if current_user.get('rol') not in ['profesor', 'admin']:
        return jsonify({"error": "Acceso denegado"}), 403

    anio     = request.args.get('anio',     type=int)
    cuatrimestre = request.args.get('cuatrimestre', type=int)
    id_curso = request.args.get('id_curso', type=int)

    conn = None
    cur  = None
    try:
        conn = get_connection()
        cur  = conn.cursor(dictionary=True)

        query = """
            SELECT 
                a.legajo AS legajo,
                CONCAT(a.nombre, ' ', a.apellido) AS alumno,
                CONCAT(a.anio, ' ', a.cuatrimestre) AS nombre_curso,
                LOWER(e.tipo) AS tipo_evaluacion,
                n.calificacion AS nota,
                c.id_curso 
            FROM notas n
            INNER JOIN evaluaciones e ON n.id_evaluacion  = e.id_evaluacion
            INNER JOIN alumnos a      ON n.legajo_alumno  = a.legajo
            INNER JOIN cursos c       ON e.id_curso       = c.id_curso
        """
        condiciones = []
        parametros  = []

        if anio:
            condiciones.append("a.anio = %s")
            parametros.append(anio)

        if cuatrimestre:
            condiciones.append("a.cuatrimestre = %s")
            parametros.append(cuatrimestre)

        if id_curso:
            condiciones.append("c.id_curso = %s")
            parametros.append(id_curso)

        if condiciones:
            query += " WHERE " + " AND ".join(condiciones)

        cur.execute(query, parametros)
        notas_crudas = cur.fetchall()

        # Diccionario para agrupar por (legajo, id_curso)
        alumnos_dict = {}
        cursos_visto = set()  # Para saber qué cursos hay

        for fila in notas_crudas:
            legajo        = fila["legajo"]
            id_curso_fila = fila["id_curso"]
            clave         = (legajo, id_curso_fila)
            cursos_visto.add(id_curso_fila)

            if clave not in alumnos_dict:
                alumnos_dict[clave] = {
                    "legajo":       legajo,
                    "nombre":       fila["alumno"],
                    "curso":        fila["nombre_curso"],
                    "id_curso":     id_curso_fila,
                    "categorias":   {}  # ← dinámico: {categoria: [notas]}
                }

            tipo_eval = fila["tipo_evaluacion"].lower() if fila["tipo_evaluacion"] else "otro"
            nota = fila["nota"]

            if nota is None:
                continue

            if tipo_eval not in alumnos_dict[clave]["categorias"]:
                alumnos_dict[clave]["categorias"][tipo_eval] = []

            alumnos_dict[clave]["categorias"][tipo_eval].append(float(nota))

        # Ahora, para cada curso, consultar qué categorías existen realmente
        categorias_por_curso = {}
        for id_curso_check in cursos_visto:
            categorias_por_curso[id_curso_check] = get_categorias_evaluacion_por_curso(id_curso_check)

        resultado = []
        for clave, datos in alumnos_dict.items():
            legajo         = datos["legajo"]
            id_curso_fila  = datos["id_curso"]
            categorias_req = categorias_por_curso.get(id_curso_fila, [])

            # Calcular promedios dinámicamente
            promedios = {}
            for cat in categorias_req:
                notas_cat = datos["categorias"].get(cat, [])
                if notas_cat:
                    promedios[cat] = sum(notas_cat) / len(notas_cat)
                else:
                    promedios[cat] = None

            # Validar: tiene notas en TODAS las categorías requeridas?
            tiene_todas = all(promedios.get(cat) is not None for cat in categorias_req)

            if tiene_todas:
                prom_final = sum(promedios[cat] for cat in categorias_req) / len(categorias_req)
                condicion  = "Aprobado" if prom_final >= 4 else "Insuficiente"
            else:
                prom_final = None
                condicion  = "Incompleto"

            # Armar respuesta con campos dinámicos
            respuesta = {
                "legajo":    legajo,
                "nombre":    datos["nombre"],
                "curso":     datos["curso"],
                "prom_final": round(prom_final, 2) if prom_final is not None else "-",
                "condicion": condicion
            }

            # Agregar cada categoría como campo: prom_tp, prom_parcial, etc.
            for cat in categorias_req:
                prom = promedios.get(cat)
                respuesta[f"prom_{cat}"] = round(prom, 2) if prom is not None else "-"

            resultado.append(respuesta)

        return jsonify(resultado), 200

    except Exception as e:
        print(f"Error en resumen-promedios: {e}")
        return jsonify({"error": "Error interno al calcular promedios"}), 500
    finally:
        if cur:  cur.close()
        if conn: conn.close()

@notas_bp.route('/periodos', methods=['GET'])
@token_required
def listar_periodos(current_user):
    """
    Devuelve los pares (anio, cuatrimestre) de cursos que tienen
    al menos una evaluación con notas cargadas.
    Sirve para poblar el filtro de cuatrimestre en el front.
    """
    if current_user.get('rol') not in ['profesor', 'admin']:
        return jsonify({"error": "Acceso denegado"}), 403

    conn = None
    cur = None
    try:
        conn = get_connection()
        cur  = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT DISTINCT c.anio, c.cuatrimestre
            FROM cursos c
            INNER JOIN evaluaciones e ON e.id_curso = c.id_curso
            INNER JOIN notas n ON n.id_evaluacion = e.id_evaluacion
            ORDER BY c.anio DESC, c.cuatrimestre ASC
        """)
        return jsonify(cur.fetchall()), 200
    except Exception as e:
        print(f"Error en GET /periodos: {e}")
        return jsonify({"error": "Error interno"}), 500
    finally:
        if cur:  cur.close()
        if conn: conn.close()
