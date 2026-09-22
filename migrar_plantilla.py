import sqlite3
import pandas as pd
import numpy as np
from supabase import create_client

# 🔑 REEMPLAZA ESTOS DOS VALORES CON TUS DATOS DE SUPABASE
SUPABASE_URL = "https://kpcbglsvubwgposajgpa.supabase.co"
SUPABASE_KEY = "sb_publishable_su6oLMMZwNuIXDwKfU6UbA_86edqxLT"

# 1. Conectar a Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 2. Leer la plantilla desde tu archivo SQLite local
conn = sqlite3.connect("aforo_alberca.db")
df_horario = pd.read_sql_query("SELECT id, dia, espacio, carril, hora, profesor, nivel FROM horario_oficial", conn)
conn.close()

# 3. Limpiar los valores NaN/vacíos para evitar errores de JSON
# Convertir la columna carril a entero de forma segura
df_horario['carril'] = pd.to_numeric(df_horario['carril'], errors='coerce').astype('Int64')
df_horario = df_horario.where(pd.notnull(df_horario), None)

# 4. Convertir DataFrame a lista de diccionarios
registros = df_horario.to_dict(orient="records")

print(f"📦 Subiendo {len(registros)} registros a Supabase...")

# 5. Insertar registros en Supabase
response = supabase.table("horario_oficial").insert(registros).execute()

print("✅ ¡Plantilla de horarios migrada exitosamente a Supabase!")


