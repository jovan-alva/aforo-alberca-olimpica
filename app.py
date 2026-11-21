import streamlit as st
import database as db
import analytics as an

st.set_page_config(page_title="Control de Aforo - Alberca Olímpica", page_icon=":shark:", layout="wide")
st.title("Control de Aforo - Alberca Olímpica Francisco Márquez")

seccion=st.sidebar.radio("Navegación:", ["Registro de Aforo", "Dashboard en Vivo", "Tendencias Mensuales e Histórico", "Grupos Específicos"])
st.sidebar.divider()
# ==========================================
# PESTAÑA 1: REGISTRO DE AFORO
# ==========================================
if seccion == "Registro de Aforo":
    st.title("Registro de Aforo")

    st.sidebar.subheader("Filtros de Registro")
    dia_sel = st.sidebar.selectbox("📅 Día:", ["SABADO", "DOMINGO"], key="dia_reg")
    horarios_disponibles = ["06:00", "07:00", "08:00", "09:00", "10:00", "12:00", "13:00"]
    hora_sel = st.sidebar.selectbox("⏰ Hora:", horarios_disponibles, key="hora_reg")
    espacio_sel = st.sidebar.selectbox("🏊‍♂️ Espacio:", ["OLIMPICA", "CALENTAMIENTO", "FOSA"], key="esp_reg")
    st.header(f"Aforo actual en {espacio_sel} ({dia_sel} - {hora_sel})")
    df_plantilla = db.obtener_plantilla(dia_sel, hora_sel, espacio_sel)

    st.header("Captura de Aforo")

    capacidad_max = 20 if espacio_sel == "OLIMPICA" else 15 if espacio_sel == "CALENTAMIENTO" else 60
    conteos_previos= db.cargar_formulario()
    with st.form(key="form_aforo", clear_on_submit=False):
        st.write(f"📏 **Capacidad máxima para {espacio_sel}:** {capacidad_max} usuarios {'por carril' if espacio_sel != 'FOSA' else 'en área general'}.")
        guardavidas = st.text_input("🪪 Guardavidas en turno:", value="JOVAN")
            
        lecturas = []
        for index, fila in df_plantilla.iterrows():
            col_carril, col_info, col_asistentes = st.columns([1, 3, 2])
            with col_carril:
                st.markdown(f"#### Carril {fila['carril']}")
            with col_info:
                st.caption(f"👨‍🏫 Profesor: **{fila['profesor']}** | Nivel: **{fila['nivel']}**")
            with col_asistentes:
                num_asistentes = st.number_input(
                    label=f"Asistentes (Carril {fila['carril']}):",
                    min_value=0, max_value=capacidad_max, value=conteos_previos.get(fila['id'], None), step=1,
                    key=f"input_{fila['id']}"
                    )
                
                asistentes_limpio= num_asistentes if num_asistentes is not None else 0

                lecturas.append({
                    'horario_id': fila['id'],
                    'asistentes': asistentes_limpio,
                    'espacio_id': 1 if espacio_sel == "OLIMPICA" else 2 if espacio_sel == "CALENTAMIENTO" else 3
                    })
                    
        boton_guardar = st.form_submit_button(label="💾 Guardar Aforo del Turno", use_container_width=True)

    if boton_guardar:
        if guardavidas.strip() == "":
            st.error("⚠️ Por favor ingresa el nombre del guardavidas.")
        else:
            total_asistentes = sum(lectura['asistentes'] for lectura in lecturas)
            db.guardar_lecturas(guardavidas, lecturas)
            st.success(f"✅ ¡Aforo guardado exitosamente por **{guardavidas}**! Total de asistentes registrados: **{total_asistentes}**.")

    st.divider()
    st.subheader("Historial de Aforos Registrados")
    df_hist = db.obtener_historial()
    if df_hist.empty:
        st.info("ℹ️ Aún no hay registros almacenados.")
    else:
        st.dataframe(df_hist, use_container_width=True)

# ==========================================
# PESTAÑA 2: DASHBOARD EN VIVO
# ==========================================

elif seccion == "Dashboard en Vivo":
    st.title("Dashboard en Vivo")
    st.sidebar.subheader("Filtros de Consulta")
    dia_dash = st.sidebar.selectbox("📅 Día:", ["SABADO", "DOMINGO"], key="dia_dash")

    horarios_disponibles = ["Todos","06:00:00", "07:00:00", "08:00:00", "09:00:00", "10:00:00", "12:00:00", "13:00:00"]
    hora_dash = st.sidebar.selectbox("⏰ Hora:", horarios_disponibles, key="hora_dash")

    fechas_disponibles = db.obtener_fechas_disponibles(dia_dash)
    if fechas_disponibles:
        fecha_sel = st.sidebar.selectbox("🗓️ Fecha:", fechas_disponibles, key="fecha_dash")
    else:
        fecha_sel = None
        st.sidebar.warning("No hay fechas registradas para este día.")

    st.subheader("📊 Dashboard en Vivo")
    
        
    if fecha_sel:
        try:
            df_dash = db.obtener_resumen_dashboard_por_fecha(fecha_sel)
            df_dash = an.calcular_saturacion_horaria(df_dash)
            df_hora= df_dash[df_dash['hora'] == hora_dash] if hora_dash != "Todos" else df_dash
            
            if not df_dash.empty and df_dash['total_hora'].sum() > 0:
                st.subheader(f"⏰ Aforo de Usuarios el {dia_dash} ({fecha_sel}) horario: {hora_dash}")
                if not df_hora.empty:
                    for index, row in df_hora.iterrows():
                        st.write(f"#### 🕒 Horario: {row['hora']}")
                        c1, c2, c3, c4 = st.columns(4)
                        c1.metric(label="Olímpica", value=f"{int(row['olimpica'])}", delta=f"{row['pct_olimpica']}% ocupación", delta_color="inverse" if row['pct_olimpica'] >= 80 else "normal")
                        c2.metric(label="Calentamiento", value=f"{int(row['calentamiento'])}", delta=f"{row['pct_calentamiento']}% ocupación", delta_color="inverse" if row['pct_calentamiento'] >= 80 else "normal")
                        c3.metric(label="Fosa", value=f"{int(row['fosa'])}", delta=f"{row['pct_fosa']}% ocupación", delta_color="inverse" if row['pct_fosa'] >= 80 else "normal")
                        c4.metric(label="Total Hora", value=f"{int(row['total_hora'])}", delta=f"{row['pct_total']}% ocupación", delta_color="inverse" if row['pct_total'] >= 80 else "normal")
                        st.caption("---")
                else:
                    st.info(f"ℹ️ No hay registros ingresados para la fecha {fecha_sel} y hora {hora_dash}.")    
                
                tot_olimpica, tot_calentamiento, tot_fosa, tot_general = an.calcular_kpis_dashboard(df_dash)
                st.subheader(f"📈 Resumen Acumulado del {dia_dash} ({fecha_sel})")
                    
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("🏊 Olímpica", f"{tot_olimpica:,}")
                m2.metric("🔥 Calentamiento", f"{tot_calentamiento:,}")
                m3.metric("🪨 Fosa", f"{tot_fosa:,}")
                m4.metric("👥 TOTAL TRES ÁREAS", f"{tot_general:,}")
            else:
                st.info(f"ℹ️ No hay registros ingresados para la fecha {fecha_sel}.")
        except Exception as e:
            st.error(f"❌ Error al cargar el dashboard: {e}")

# ==========================================
# PESTAÑA 3: HISTÓRICO Y RESPALDO
# ==========================================

elif seccion == "Tendencias Mensuales e Histórico":
    st.title("📈 Tendencias Mensuales e Histórico")

    df_tendencias = db.obtener_tendencias_mensuales()
    df_tendencias = an.calcular_saturacion(df_tendencias)
    df_criticos= df_tendencias[df_tendencias['porcentaje_saturacion'] >= 80]
    st.subheader("🚨 Turnos en Alerta o Saturados (≥ 80%)")
    if df_criticos.empty:
        st.info("ℹ️ No hay turnos en alerta o saturados.")
    else:
        st.dataframe(df_criticos[['fecha', 'hora', 'espacio','carril','profesor', 'asistentes',  'porcentaje_saturacion', 'estado_saturacion']], use_container_width=True)

    if df_tendencias.empty:
        st.info("ℹ️ No hay datos históricos disponibles para mostrar.")
    else:
        st.subheader("📊 Resumen Histórico de Aforos por Fecha")

        df_por_fecha = df_tendencias.groupby('fecha')["asistentes"].sum().reset_index()

        st.subheader("Evolución de Aforo por Fecha")
        st.line_chart(df_por_fecha, x='fecha', y='asistentes')

    st.divider()

    st.subheader("📊 Resumen de Aforos por Espacio")
    df_por_espacio = df_tendencias.groupby('espacio')["asistentes"].sum().reset_index()
    st.bar_chart(df_por_espacio, x='espacio', y='asistentes')

    st.download_button(
        label="💾 Descargar Datos Históricos",
        data=df_tendencias.to_csv(index=False).encode('utf-8'),
        file_name='historico_aforos.csv',
        mime='text/csv'
    )
# ==========================================
# PESTAÑA 4: GRUPOS ESPECÍFICOS
# ==========================================

elif seccion == "Grupos Específicos":
    st.title("Grupos Específicos")
    st.sidebar.subheader("Filtros de Consulta")
    dia_sel = st.sidebar.selectbox("📅 Día:", ["SABADO", "DOMINGO"], key="dia_t4")
    horarios_disponibles = ["06:00", "07:00", "08:00", "09:00", "10:00", "12:00", "13:00"]
    hora_sel = st.sidebar.selectbox("⏰ Hora:", horarios_disponibles, key="hora_t4")
    espacio_sel = st.sidebar.selectbox("🏊‍♂️ Espacio:", ["OLIMPICA", "CALENTAMIENTO", "FOSA"], key="esp_t4")

    st.subheader("📊 Grupos Específicos por Hora")
    

    df_plantilla2 = db.obtener_plantilla(dia_sel, hora_sel, espacio_sel)
    st.subheader("Grupo de Carriles y Profesores Programados")
        
    if df_plantilla2.empty:
        st.warning("⚠️ No hay registros programados en la plantilla para este horario.")
    else:
        st.dataframe(df_plantilla2[['carril', 'profesor', 'nivel']], use_container_width=True)