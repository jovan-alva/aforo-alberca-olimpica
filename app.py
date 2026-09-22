import streamlit as st
import database as db
import analytics as an

st.set_page_config(page_title="Control de Aforo - Alberca Olímpica", page_icon=":shark:", layout="wide")
st.title("Control de Aforo - Alberca Olímpica Francisco Márquez")

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Registro de Aforo", 
    "📊 Dashboard En Vivo", 
    "📈 Tendencias Mensuales e Histórico",
    "Grupos Específicos por Hora"
])

# ==========================================
# PESTAÑA 1: REGISTRO DE AFORO
# ==========================================
with tab1:
    st.subheader("Registro de Aforo por Turno y Espacio")
    col1, col2, col3 = st.columns(3)
            
    with col1:
        dia_sel = st.selectbox("📅 Día:", ["SABADO", "DOMINGO"], key="dia_reg")
    with col2:
        horarios_disponibles = ["06:00", "07:00", "08:00", "09:00", "10:00", "12:00", "13:00"]
        hora_sel = st.selectbox("⏰ Hora:", horarios_disponibles, key="hora_reg")
    with col3:
        espacio_sel = st.selectbox("🏊‍♂️ Espacio:", ["OLIMPICA", "CALENTAMIENTO", "FOSA"], key="esp_reg")

    df_plantilla = db.obtener_plantilla(dia_sel, hora_sel, espacio_sel)
            
    st.divider()
    st.subheader("Captura de Aforo y Nivel de Saturación")

    capacidad_max = 20 if espacio_sel == "OLIMPICA" else 15 if espacio_sel == "CALENTAMIENTO" else 60

    with st.form(key="form_aforo"):
        st.write(f"📏 **Capacidad máxima para {espacio_sel}:** {capacidad_max} usuarios {'por carril' if espacio_sel != 'FOSA' else 'en área general'}.")
        guardavidas = st.text_input("🪪 Guardavidas en turno:", value="JOVAN")
        
        lecturas = []
        for index, fila in df_plantilla.iterrows():
            col_carril, col_info, col_asistentes = st.columns([1, 3, 2])
            with col_carril:
                st.markdown(f"### Carril {fila['carril']}")
            with col_info:
                st.caption(f"👨‍🏫 Profesor: **{fila['profesor']}** | Nivel: **{fila['nivel']}**")
            with col_asistentes:
                num_asistentes = st.number_input(
                    label=f"Asistentes (Carril {fila['carril']}):",
                    min_value=0, max_value=capacidad_max, value=0, step=1,
                    key=f"input_{fila['id']}"
                )
                lecturas.append({
                    'horario_id': fila['id'],
                    'asistentes': num_asistentes,
                    'espacio_id': 1 if espacio_sel == "OLIMPICA" else 2 if espacio_sel == "CALENTAMIENTO" else 3
                })
                
        boton_guardar = st.form_submit_button(label="💾 Guardar Aforo del Turno", use_container_width=True)

    if boton_guardar:
        if guardavidas.strip() == "":
            st.error("⚠️ Por favor ingresa el nombre del guardavidas.")
        else:
            db.guardar_lecturas(guardavidas, lecturas)
            st.success(f"✅ ¡Aforo guardado exitosamente por **{guardavidas}**!")

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
with tab2:
    st.subheader("📊 Dashboard En Vivo")
    dia_dash = st.selectbox("📅 Selecciona el Día a Consultar:", ["SABADO", "DOMINGO"], key="dia_dash")

    try:
        df_dash = db.obtener_resumen_dashboard(dia_dash)

        if not df_dash.empty and df_dash['total_hora'].sum() > 0:
            tot_olimpica, tot_calentamiento, tot_fosa, tot_general = an.calcular_kpis_dashboard(df_dash)

            st.subheader(f"📈 Resumen Acumulado del {dia_dash}")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("🏊‍♂️ Olímpica", f"{tot_olimpica:,}")
            m2.metric("🏊‍♀️ Calentamiento", f"{tot_calentamiento:,}")
            m3.metric("🪂 Fosa", f"{tot_fosa:,}")
            m4.metric("👥 TOTAL TRES ÁREAS", f"{tot_general:,}")

            st.divider()
            st.subheader("⏰ Desglose de Usuarios por Horario")

            for index, row in df_dash.iterrows():
                st.write(f"#### 🕐 Horario: {row['hora']}")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Olímpica", f"{int(row['olimpica'])}")
                c2.metric("Calentamiento", f"{int(row['calentamiento'])}")
                c3.metric("Fosa", f"{int(row['fosa'])}")
                c4.metric("Total Hora", f"{int(row['total_hora'])}")
                st.caption("---")
        else:
            st.info(f"ℹ️ No hay registros ingresados para el día {dia_dash}.")
    except Exception as e:
        st.error(f"⚠️ Error al cargar el dashboard: {e}")

# ==========================================
# PESTAÑA 3: HISTÓRICO Y RESPALDO
# ==========================================
with tab3:
    st.subheader("📈 Tendencias Mensuales e Histórico")
    st.info("⚠️ Esta sección está en desarrollo.")
    st.divider()

# ==========================================
# PESTAÑA 4: GRUPOS ESPECÍFICOS
# ==========================================
with tab4:
    st.subheader("📊 Grupos Específicos por Hora")
    col1_tab4, col2_tab4, col3_tab4 = st.columns(3)
    
    with col1_tab4:
        dia_sel_t4 = st.selectbox("📅 Día:", ["SABADO", "DOMINGO"], key="dia_t4")
    with col2_tab4:
        hora_sel_t4 = st.selectbox("⏰ Hora:", horarios_disponibles, key="hora_t4")
    with col3_tab4:
        espacio_sel_t4 = st.selectbox("🏊‍♂️ Espacio:", ["OLIMPICA", "CALENTAMIENTO", "FOSA"], key="esp_t4")

    df_plantilla2 = db.obtener_plantilla(dia_sel_t4, hora_sel_t4, espacio_sel_t4)
    st.subheader("Grupo de Carriles y Profesores Programados")
    
    if df_plantilla2.empty:
        st.warning("⚠️ No hay registros programados en la plantilla para este horario.")
    else:
        st.dataframe(df_plantilla2[['carril', 'profesor', 'nivel']], use_container_width=True)