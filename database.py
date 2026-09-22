import os
import streamlit as st
import pandas as pd
from supabase import create_client
import datetime as dt

# 🔑 Endpoint y Clave de API de Supabase
SUPABASE_URL = "https://kpcbglsvubwgposajgpa.supabase.co"
SUPABASE_KEY = "sb_publishable_su6oLMMZwNuIXDwKfU6UbA_86edqxLT"

@st.cache_resource
def obtener_conexion():
    """Crea y devuelve la conexión con el cliente de Supabase."""
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def obtener_plantilla(dia, hora, espacio):
    """Obtiene la plantilla oficial desde Supabase."""
    supabase = obtener_conexion()
    response = (
        supabase.table("horario_oficial")
        .select("id, carril, profesor, nivel")
        .eq("dia", dia)
        .eq("hora", hora)
        .eq("espacio", espacio)
        .execute()
    )
    return pd.DataFrame(response.data)

def guardar_lecturas(guardavidas, lecturas_list):
    """Guarda los registros de conteo en Supabase."""
    supabase = obtener_conexion()
    fecha_actual = str(dt.datetime.now().date())
    registros = []
    for item in lecturas_list:
        registros.append({
            "guardavidas_registro": guardavidas,
            "horario_id": int(item['horario_id']),
            "asistentes": int(item['asistentes']),
            "espacio_id": int(item['espacio_id']),
            "fecha": fecha_actual
        })
        
    response = supabase.table("registro_aforo").insert(registros).execute()
    return response

def obtener_historial():
    """Consulta el historial de aforos registrados en Supabase."""
    supabase = obtener_conexion()
    response = (
        supabase.table("registro_aforo")
        .select("""
            id,
            fecha,
            asistentes,
            guardavidas_registro,
            horario_oficial (
                dia,
                hora,
                espacio,
                carril,
                profesor
            )
        """)
        .order("id", desc=True)
        .execute()
    )
    
    data = response.data
    if not data:
        return pd.DataFrame()

    filas = []
    for r in data:
        ho = r.get("horario_oficial") or {}
        filas.append({
            "folio": r.get("id"),
            "Fecha": r.get("fecha"),
            "Día": ho.get("dia"),
            "Hora Clase": ho.get("hora"),
            "Espacio": ho.get("espacio"),
            "Carril": ho.get("carril"),
            "Profesor": ho.get("profesor"),
            "Asistentes": r.get("asistentes"),
            "Guardavidas": r.get("guardavidas_registro")
        })
        
    return pd.DataFrame(filas)

def obtener_resumen_dashboard(dia):
    """Obtiene el aforo de Supabase para generar el resumen por hora y espacio."""
    supabase = obtener_conexion()
    
    response = (
        supabase.table("registro_aforo")
        .select("""
            asistentes,
            horario_oficial!inner (
                dia,
                hora
            ),
            espacios (
                espacio
            )
        """)
        .eq("horario_oficial.dia", dia)
        .execute()
    )
    
    data = response.data
    if not data:
        return pd.DataFrame()
        
    filas = []
    for r in data:
        ho = r.get("horario_oficial") or {}
        esp = r.get("espacios") or {}
        filas.append({
            "hora": ho.get("hora"),
            "espacio": esp.get("espacio"),
            "asistentes": r.get("asistentes", 0)
        })
        
    df = pd.DataFrame(filas)
    if df.empty:
        return pd.DataFrame()
        
    pivote = df.pivot_table(
        index="hora", 
        columns="espacio", 
        values="asistentes", 
        aggfunc="sum", 
        fill_value=0
    ).reset_index()
    
    for col in ['OLIMPICA', 'CALENTAMIENTO', 'FOSA']:
        if col not in pivote.columns:
            pivote[col] = 0
            
    pivote.rename(columns={
        'OLIMPICA': 'olimpica',
        'CALENTAMIENTO': 'calentamiento',
        'FOSA': 'fosa'
    }, inplace=True)
    
    pivote['total_hora'] = pivote['olimpica'] + pivote['calentamiento'] + pivote['fosa']
    pivote.sort_values(by="hora", inplace=True)
    
    return pivote