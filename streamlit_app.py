import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Monitoreo Grupos Electrógenos", layout="wide")
st.title("⚡ Panel Operativo: Grupos Electrógenos y Combustible")

# 1. PEGA AQUÍ EL ENLACE COMPARTIDO DE TU ARCHIVO EXCEL EN ONEDRIVE
URL_ONEDRIVE = "https://docs.google.com/spreadsheets/d/1-Ck3YQRoGY8YLjcXoUs8h88aYY3BMfrF/edit?usp=sharing&ouid=104586048846795279374&rtpof=true&sd=true"

def convertir_url_onedrive(url):
    # Convierte el enlace estándar de compartir de OneDrive en enlace de descarga directa para Pandas
    if "1drv.ms" in url or "onedrive.live.com" in url:
        if "download=1" not in url:
            separador = "&" if "?" in url else "?"
            return f"{url}{separador}download=1"
    return url

url_descarga = convertir_url_onedrive(URL_ONEDRIVE)

# Botón manual para refrescar los datos al instante
if st.button("🔄 Actualizar Datos"):
    st.cache_data.clear()

@st.cache_data(ttl=60)
def cargar_datos(url):
    return pd.read_excel(url)

try:
    df = cargar_datos(url_descarga)
    df = df.dropna(how="all")

    if not df.empty:
        # Aseguramos formato numérico en las columnas clave
        cols_numericas = ["Combustible_Galones", "Horas_GE1", "Voltaje_GE1", "Horas_GE2", "Voltaje_GE2"]
        for col in cols_numericas:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # Obtener la última lectura registrada
        ultimo = df.iloc[-1]

        # --- PANEL DE ALERTAS CRÍTICAS ---
        st.subheader("🚨 Estado de Alertas y Parámetros Críticos")
        alertas_activas = False

        # Verificación de Voltaje (< 13.0 V)
        if ultimo["Voltaje_GE1"] < 13.0:
            st.error(f"⚠️ ALERTA GE-01: Voltaje de batería bajo ({ultimo['Voltaje_GE1']:.1f} V). Mínimo permitido: 13.0 V.")
            alertas_activas = True
        if ultimo["Voltaje_GE2"] < 13.0:
            st.error(f"⚠️ ALERTA GE-02: Voltaje de batería bajo ({ultimo['Voltaje_GE2']:.1f} V). Mínimo permitido: 13.0 V.")
            alertas_activas = True

        # Verificación de Nivel de Aceite ('min')
        aceite_1 = str(ultimo["Aceite_GE1"]).strip().lower()
        aceite_2 = str(ultimo["Aceite_GE2"]).strip().lower()

        if aceite_1 == "min":
            st.warning("⚠️ ATENCIÓN GE-01: Nivel de aceite en MÍNIMO (min).")
            alertas_activas = True
        if aceite_2 == "min":
            st.warning("⚠️ ATENCIÓN GE-02: Nivel de aceite en MÍNIMO (min).")
            alertas_activas = True

        # Verificación de Alarmas Generales del tablero
        if str(ultimo["Alarma_GE1"]).strip().lower() not in ["ninguna", "no", "nan", ""]:
            st.error(f"🔔 Alarma Tablero GE-01: {ultimo['Alarma_GE1']}")
            alertas_activas = True
        if str(ultimo["Alarma_GE2"]).strip().lower() not in ["ninguna", "no", "nan", ""]:
            st.error(f"🔔 Alarma Tablero GE-02: {ultimo['Alarma_GE2']}")
            alertas_activas = True

        if not alertas_activas:
            st.success("✅ Todos los parámetros operan dentro de los rangos normales (Baterías ≥ 13 V, Aceite OK, Sin alarmas).")

        # --- MÉTRICAS GENERALES Y POR GRUPO ---
        st.markdown("---")
        st.subheader("📌 Última Lectura Registrada")
        
        # Tanque General
        st.metric("⛽ Nivel Tanque Compartido", f"{ultimo['Combustible_Galones']:,.1f} gal")
        
        col_ge1, col_ge2 = st.columns(2)
        
        with col_ge1:
            st.markdown("### ⚙️ Grupo Electrógeno 01")
            c1, c2, c3 = st.columns(3)
            c1.metric("Horómetro", f"{ultimo['Horas_GE1']:,.1f} h")
            c2.metric("Nivel Aceite", str(ultimo['Aceite_GE1']).upper())
            # Muestra diferencia negativa en rojo si baja de 13V
            delta_v1 = ultimo['Voltaje_GE1'] - 13.0
            c3.metric("Batería", f"{ultimo['Voltaje_GE1']:.1f} V", delta=f"{delta_v1:+.1f} V vs 13V")

        with col_ge2:
            st.markdown("### ⚙️ Grupo Electrógeno 02")
            c1, c2, c3 = st.columns(3)
            c1.metric("Horómetro", f"{ultimo['Horas_GE2']:,.1f} h")
            c2.metric("Nivel Aceite", str(ultimo['Aceite_GE2']).upper())
            delta_v2 = ultimo['Voltaje_GE2'] - 13.0
            c3.metric("Batería", f"{ultimo['Voltaje_GE2']:.1f} V", delta=f"{delta_v2:+.1f} V vs 13V")

        # --- GRÁFICOS DE TENDENCIAS ---
        st.markdown("---")
        st.subheader("📊 Evolución Histórica")
        col_g1, col_g2 = st.columns(2)

        with col_g1:
            st.markdown("**Nivel de Combustible (Galones)**")
            st.line_chart(df, x="Fecha_Hora", y="Combustible_Galones")

        with col_g2:
            st.markdown("**Voltaje de Baterías (GE-01 vs GE-02)**")
            df_voltajes = df[["Fecha_Hora", "Voltaje_GE1", "Voltaje_GE2"]].set_index("Fecha_Hora")
            st.line_chart(df_voltajes)

        # --- HISTORIAL COMPLETO ---
        st.markdown("---")
        st.subheader("📋 Historial Completo")
        st.dataframe(df.iloc[::-1], use_container_width=True)

    else:
        st.info("La hoja de Excel está vacía. Ingresa la primera fila de datos en OneDrive y presiona 'Actualizar Datos'.")

except Exception as e:
    st.error("No se pudo leer el archivo de OneDrive. Verifica que el enlace sea público ('Cualquier persona con el enlace puede ver') y que las columnas coincidan.")
