import sqlite3

DB_FILE = "aforo_alberca.db"

def recrear_tabla_registro():
    conexion = sqlite3.connect(DB_FILE)
    cursor = conexion.cursor()
    
    # 1. Borramos la tabla anterior si existe para limpiar datos viejos
    cursor.execute("DROP TABLE IF EXISTS registro_aforo;")
    
    # 2. Creamos la estructura ligera optimizada
    cursor.execute("""
    CREATE TABLE registro_aforo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
        guardavidas_registro TEXT NOT NULL,
        horario_id INTEGER NOT NULL,
        asistentes INTEGER NOT NULL,
        FOREIGN KEY (horario_id) REFERENCES horario_oficial (id)
    );
    """)
    
    conexion.commit()
    conexion.close()
    print("🧹 ¡Tabla 'registro_aforo' anterior eliminada y recreada con éxito en su versión ligera!")

if __name__ == "__main__":
    recrear_tabla_registro()