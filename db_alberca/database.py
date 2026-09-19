import sqlite3
import pandas as pd

DB_FILE = "aforo_alberca.db"

def obtener_conexion():
    """Establece una conexión con la base de datos SQLite."""
    return sqlite3.connect(DB_FILE)

def obtener_plantilla(dia,hora,espacio):
    """obtiene la plantilla oficial de instructores y carriles"""
    conexion = obtener_conexion()
    query = """
    SELECT id, carril, profesor, nivel
    FROM horario_oficial
    WHERE dia = ? AND hora = ? AND espacio = ?;
    """
    df = pd.read_sql_query(query, conexion, params=(dia, hora, espacio))
    conexion.close()
    return df

def guardar_lecturas(guardavidas, lecturas_list):
    """guarda los registros de conteo de aforo en la base de datos """
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    query = """
    INSERT INTO registro_aforo (guardavidas_registro, horario_id, asistentes, espacio, espacio_id)
    VALUES (?, ?, ?, ?, ?); """
    for item in lecturas_list:
        cursor.execute(query, (guardavidas, item['horario_id'], item['asistentes'], item['espacio'], item['espacio_id']))
    conexion.commit()
    conexion.close()

def obtener_historial():
    """Consulta todo el historial de registros realizados con JOIN."""
    conexion = obtener_conexion()
    query = """
        SELECT 
            r.id AS folio,
            r.fecha_hora AS "Fecha/Hora",
            h.dia AS "Día",
            h.hora AS "Hora Clase",
            h.espacio AS "Espacio",
            h.carril AS "Carril",
            h.profesor AS "Profesor",
            r.asistentes AS "Asistentes",
            r.guardavidas_registro AS "Guardavidas"
        FROM registro_aforo r
        JOIN horario_oficial h ON r.horario_id = h.id
        ORDER BY r.id DESC;
    """
    df = pd.read_sql_query(query, conexion)
    conexion.close()
    return df

def obtener_resumen_dashboard(dia):
    """Obtiene el aforo agrupado por hora y espacio para un día específico."""
    conexion = obtener_conexion()
    query = """
        SELECT 
            h.hora,
            SUM(CASE WHEN e.espacio = 'OLIMPICA' THEN r.asistentes ELSE 0 END) AS olimpica,
            SUM(CASE WHEN e.espacio = 'CALENTAMIENTO' THEN r.asistentes ELSE 0 END) AS calentamiento,
            SUM(CASE WHEN e.espacio = 'FOSA' THEN r.asistentes ELSE 0 END) AS fosa,
            SUM(r.asistentes) AS total_hora
        FROM registro_aforo r
        JOIN horario_oficial h ON r.horario_id = h.id
        JOIN espacios e ON r.espacio_id = e.id
        WHERE h.dia = ?
        GROUP BY h.hora
        ORDER BY h.hora ASC;
    """
    df = pd.read_sql_query(query, conexion, params=(dia,))
    conexion.close()
    return df