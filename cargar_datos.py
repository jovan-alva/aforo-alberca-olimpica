import sqlite3

DB_FILE = "aforo_alberca.db"

def insertar_horario_sabado_06am():
    conexion = sqlite3.connect(DB_FILE)
    cursor = conexion.cursor()
    
    # 1. Lista de tuplas con la información oficial del documento (Sábado 06:00 AM)
    # Estructura: (dia, espacio, carril, hora_inicio, hora_fin, profesor, nivel)
    datos_sabado_06am = [
        ('SABADO', 'OLIMPICA', '1', '06:00', 'DAVID', 'APB'),
        ('SABADO', 'OLIMPICA', '2',  '06:00', 'ELIBETH', 'AIA'),
        ('SABADO', 'OLIMPICA', '3',  '06:00', 'JOVANY', 'AIB'),
        ('SABADO', 'OLIMPICA', '4',  '06:00', 'JOVANY', 'AIB'),
        ('SABADO', 'OLIMPICA', '5',  '06:00', 'RAUL', 'AAB'),
        ('SABADO', 'OLIMPICA', '6',  '06:00', 'RAUL', 'AAB'),
        ('SABADO', 'OLIMPICA', '7',  '06:00', 'CHE', 'AAA'),
        ('SABADO', 'OLIMPICA', '8', '06:00', 'TERE', 'APA'),
        ('SABADO', 'OLIMPICA', '8', '06:00', 'FANY', 'APA')
    ]
    
    # 2. Sentencia SQL para insertar múltiples filas a la vez
    query = '''
        INSERT INTO horario_oficial (dia, espacio, carril, hora, profesor, nivel)
        VALUES (?, ?, ?, ?, ?, ?)
    '''
    
    # 3. executemany inserta toda la lista de una sola vez
    cursor.executemany(query, datos_sabado_06am)
    
    # 4. Confirmamos los cambios y cerramos
    conexion.commit()
    conexion.close()
    print("💾 ¡Información del Sábado 06:00 AM guardada con éxito en la base de datos!")

if __name__ == "__main__":
    insertar_horario_sabado_06am()

def consultar_sabado_06am():
    conexion = sqlite3.connect(DB_FILE)
    cursor = conexion.cursor()
    
    # Consulta para obtener todos los registros del Sábado 06:00 AM
    query = '''
        SELECT * FROM horario_oficial
        WHERE dia = 'SABADO' AND hora = '06:00'
    '''
    
    cursor.execute(query)
    resultados = cursor.fetchall()
    conexion.close()
    
    print("📋 Registros encontrados en el catálogo:")
    for fila in resultados:
        print(fila)

if __name__ == "__main__":
    consultar_sabado_06am()