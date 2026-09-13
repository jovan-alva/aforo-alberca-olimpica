import streamlit as st
import pandas as pd
import sqlite3

DB_FILE = "aforo_alberca.db"

st.set_page_config(page_title="Control de Aforo - Alberca Olimpica", page_icon=":shark:", layout="wide")

st.title("Control de Aforo - Alberca Olimpica Francisco Márquez")

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Registro de Aforo", 
    "📊 Dashboard En Vivo", 
    "📈 Tendencias Mensuales e Historico",
    "Grupo Especificos por Hora"])
with tab1:
    st.subheader("Registro de Aforo por Turno y Espacio")
    st.subheader("Selecciona el Turno y Espacio")
        
    col1, col2, col3 = st.columns(3)
            
    with col1:
        dia_sel=st.selectbox("📅Dia:", ["SABADO", "DOMINGO"])
            
    with col2:
        horarios_disponibles = ["06:00", "07:00", "08:00", "09:00", "10:00", "12:00", "13:00"]
        hora_sel = st.selectbox("⏰ Hora:", horarios_disponibles)
            
    with col3:
        espacio_sel = st.selectbox("🏊‍♂️ Espacio:", ["OLIMPICA", "CALENTAMIENTO", "FOSA"])

    def obtener_plantilla(dia, hora, espacio):
            conexion = sqlite3.connect(DB_FILE)
            query = """
                SELECT id, carril, profesor, nivel 
                FROM horario_oficial 
                WHERE dia = ? AND hora = ? AND espacio = ?;
                """
            df = pd.read_sql_query(query, conexion, params=(dia, hora, espacio))
            conexion.close()
            return df
    df_plantilla = obtener_plantilla(dia_sel, hora_sel, espacio_sel)
            
    # --- BLOQUE 3: FORMULARIO DE CONTEO Y SATURACIÓN ---
    st.divider()
    st.subheader("Captura de Aforo y Nivel de Saturación")

    # 1. Definimos la capacidad máxima dinámica según el espacio seleccionado
    if espacio_sel == "OLIMPICA":
        capacidad_max = 20
    elif espacio_sel == "CALENTAMIENTO":
        capacidad_max = 15
    else:  # FOSA
        capacidad_max = 60

    # 2. Función para insertar las lecturas en la base de datos
    def guardar_lecturas(guardavidas, lecturas_list):
        conexion = sqlite3.connect(DB_FILE)
        cursor = conexion.cursor()
        
        query = """
            INSERT INTO registro_aforo (guardavidas_registro, horario_id, asistentes, espacio_id)
            VALUES (?, ?, ?, ?);
        """
        
        for item in lecturas_list:
            cursor.execute(query, (guardavidas, item['horario_id'], item['asistentes'], item['espacio_id']))
            
        conexion.commit()
        conexion.close()

    # 3. Formulario interactivo
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
                    min_value=0,
                    max_value=capacidad_max,
                    value=0,
                    step=1,
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
            guardar_lecturas(guardavidas, lecturas)
            st.success(f"✅ ¡Aforo guardado exitosamente por **{guardavidas}** en la base de datos!")


    # --- BLOQUE 4: CONSULTA DE HISTORIAL EN TIEMPO REAL ---
    st.divider()
    st.subheader("4. Historial de Aforos Registrados")

    def obtener_historial():
        conexion = sqlite3.connect(DB_FILE)
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
        df_historial = pd.read_sql_query(query, conexion)
        conexion.close()
        return df_historial

    # Mostramos la tabla unida con JOIN en la pantalla
    df_hist = obtener_historial()

    if df_hist.empty:
        st.info("ℹ️ Aún no hay registros almacenados en la base de datos.")
    else:
        st.dataframe(df_hist, use_container_width=True)

with tab2:
    st.subheader("📊 Dashboard En Vivo")
    # 1. Selector de Día independiente
    dia_dash = st.selectbox(
        "📅 Selecciona el Día a Consultar:", 
        ["SABADO", "DOMINGO"], 
        key="dia_dash"
    )

    try:
        conn = sqlite3.connect(DB_FILE)

        # 2. Consulta SQL: Totales por espacio y por hora para el día seleccionado
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
            WHERE r.horario_id = ?
            GROUP BY h.id
            ORDER BY h.id ASC;
        """
        
        df_dash = pd.read_sql_query(query, conn, params=(dia_dash,))
        conn.close()

        if not df_dash.empty():
            # ---------------------------------------------------------
            # 🏆 MÉTRICAS GENERALES (Totales por Espacio y Global)
            # ---------------------------------------------------------
            st.subheader(f"📈 Resumen Acumulado del {dia_dash}")
            
            total_olimpica = df_dash['olimpica'].sum()
            total_calentamiento = df_dash['calentamiento'].sum()
            total_fosa = df_dash['fosa'].sum()
            total_general = df_dash['total_hora'].sum()

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("🏊‍♂️ Olímpica", f"{total_olimpica:,}")
            m2.metric("🏊‍♀️ Calentamiento", f"{total_calentamiento:,}")
            m3.metric("🪂 Fosa", f"{total_fosa:,}")
            m4.metric("👥 TOTAL TRES ÁREAS", f"{total_general:,}")

            st.divider()

            # ---------------------------------------------------------
            # ⏰ MÉTRICAS DESGLOSADAS POR HORA
            # ---------------------------------------------------------
            st.subheader("⏰ Desglose de Usuarios por Horario")

            for index, row in df_dash.iterrows():
                st.write(f"#### 🕐 Horario: {row['hora']}")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Olímpica", f"{row['olimpica']}")
                c2.metric("Calentamiento", f"{row['calentamiento']}")
                c3.metric("Fosa", f"{row['fosa']}")
                c4.metric("Total Hora", f"{row['total_hora']}")
                st.caption("---")

        else:
            st.info(f"ℹ️ No hay registros ingresados para el día {dia_dash}.")

    except Exception as e:
        st.error(f"⚠️ Error al cargar el dashboard: {e}")

with tab3:
    st.subheader("📈 Tendencias Mensuales e Historico")
    st.info("⚠️ Esta sección está en desarrollo y se actualizará próximamente con análisis históricos y tendencias.")

    st.divider()
    st.subheader("💾 Copia de Seguridad y Respaldo")
    st.write("Descarga una copia completa de la base de datos SQLite (`.db`) con todos los registros almacenados hasta el momento.")
    
    # Leemos el archivo de la base de datos en modo binario
    try:
        with open(DB_FILE, "rb") as file:
            st.download_button(
                label="📥 Descargar Respaldo de Base de Datos (aforo_alberca.db)",
                data=file,
                file_name="aforo_alberca_respaldo.db",
                mime="application/x-sqlite3",
                use_container_width=True
            )
    except FileNotFoundError:
        st.error("⚠️ No se encontró el archivo de base de datos para descargar.")

with tab4:
    st.subheader("📊 Grupos Especificos por Hora")
    st.subheader("Selecciona el Turno y Espacio")

    col1_tab2, col2_tab2, col3_tab2 = st.columns(3)
    
    with col1_tab2:
        dia_sel_tab2 = st.selectbox(
            "📅 Día:", 
            ["SABADO", "DOMINGO"], 
            key="dia_tab2"
        )
            
    with col2_tab2:
        horarios_disponibles = ["06:00", "07:00", "08:00", "09:00", "10:00", "12:00", "13:00"]
        hora_sel_tab2 = st.selectbox(
            "⏰ Hora:", 
            horarios_disponibles, 
            key="hora_tab2"
        )
            
    with col3_tab2:
        espacio_sel_tab2 = st.selectbox(
            "🏊‍♂️ Espacio:", 
            ["OLIMPICA", "CALENTAMIENTO", "FOSA"], 
            key="espacio_tab2"
        )
    
    
    def obtener_plantilla2(dia, hora, espacio):
                conexion = sqlite3.connect(DB_FILE)
                query = """
                    SELECT id, carril, profesor, nivel 
                    FROM horario_oficial 
                    WHERE dia = ? AND hora = ? AND espacio = ?;
                    """
                df = pd.read_sql_query(query, conexion, params=(dia, hora, espacio))
                conexion.close()
                return df
    df_plantilla2 = obtener_plantilla2(dia_sel_tab2, hora_sel_tab2, espacio_sel_tab2)
    st.subheader("Grupo de Carriles y Profesores Programados en la Plantilla Oficial")
    
    if df_plantilla2.empty:
        st.warning("⚠️ No hay registros programados en la plantilla para este espacio u horario.")
    else:
            # Mostramos la plantilla oficial en la pantalla
        st.dataframe(df_plantilla2[['carril', 'profesor', 'nivel']], use_container_width=True)
