import sqlite3
import pandas as pd
import os

DB_FILE = "aforo_alberca.db"
CSV_FILE = r"c:\Users\USER\OneDrive\Documentos\Primer proyecto analisis de datos\db_alberca\GRUPOS_ESPECIFICOS.csv"

df= pd.read_csv(CSV_FILE)

conexion = sqlite3.connect(DB_FILE)

df.to_sql('horario_oficial', conexion, if_exists='replace', index=True, index_label='id')

conexion.close()

print("💾 ¡Información del horario oficial guardada con éxito en la base de datos!")
