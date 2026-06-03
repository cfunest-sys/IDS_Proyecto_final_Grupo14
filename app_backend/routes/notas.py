from flask import Blueprint, jsonify
from database.db import get_connection

notas_bp = Blueprint('notas', __name__)

@notas_bp.route('/resumen-promedios', methods=['GET'])
def resumen_promedios():
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT 
                a.legajo AS padron, 
                a.nombre AS alumno, 
                e.tipo AS tipo_evaluacion, 
                n.nota AS nota
            FROM notas n
            JOIN alumnos a ON n.legajo_alumno = a.legajo
            JOIN evaluaciones e ON n.id_evaluacion = e.id_evaluacion
        """)
        notas_crudas = cur.fetchall()
        
        alumnos_dict = {}
        for fila in notas_crudas:
            padron, alumno, tipo, nota = fila
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
            
            tipo_lower = tipo.lower()
            if "tp" in tipo_lower or "trabajo" in tipo_lower:
                alumnos_dict[padron]["tps"].append(float(nota))
            elif "parcialito" in tipo_lower:
                alumnos_dict[padron]["parcialitos"].append(float(nota))
            elif "parcial" in tipo_lower:
                alumnos_dict[padron]["parciales"].append(float(nota))

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
