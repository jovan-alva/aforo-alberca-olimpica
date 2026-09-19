import sqlite3

DB_FILE = "aforo_alberca.db"

def crear_tabla_espacios():
    conexion = sqlite3.connect(DB_FILE)
    cursor = conexion.cursor()
    
    # Creamos la tabla para almacenar el horario oficial
    query_crear_tabla = '''
    CREATE TABLE IF NOT EXISTS espacios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        espacio TEXT NOT NULL         
    );
    '''
    cursor.execute(query_crear_tabla)
    conexion.commit()
    conexion.close()
    print("✅ Tabla 'espacios' creada con éxito.")

if __name__ == "__main__":
    crear_tabla_espacios()

def insertar_espacios():
    conexion = sqlite3.connect(DB_FILE)
    cursor = conexion.cursor()

    query_insertar = '''
    INSERT INTO espacios (espacio) VALUES
        ('OLIMPICA'),
        ('CALENTAMIENTO'),
        ('FOSA');
    '''
    cursor.execute(query_insertar)
    conexion.commit()
    conexion.close() 

if __name__ == "__main__":
    insertar_espacios()