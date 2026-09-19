import sqlite3

DB_FILE = "aforo_alberca.db"

def crear_tabla_horario_oficial():
    conexion = sqlite3.connect(DB_FILE)
    cursor = conexion.cursor()
    
    # Creamos la tabla para almacenar el horario oficial
    query_crear_tabla = '''
    CREATE TABLE IF NOT EXISTS horario_oficial (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dia TEXT NOT NULL,                 -- 'SABADO' o 'DOMINGO'
        espacio TEXT NOT NULL,             -- 'OLIMPICA', 'CALENTAMIENTO', 'FOSA'
        carril TEXT NOT NULL,              -- '1A', '2', '3', etc.
        hora TEXT NOT NULL,                -- '06:00', '07:00', etc.
        profesor TEXT NOT NULL,            -- 'JOVANY', 'DAVID', etc.
        nivel TEXT NOT NULL                -- 'AIB', 'AIA', etc.
    );
    '''
    cursor.execute(query_crear_tabla)
    conexion.commit()
    conexion.close()
    print("✅ Tabla 'horario_oficial' creada con éxito.")

if __name__ == "__main__":
     crear_tabla_horario_oficial()