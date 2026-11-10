import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración inicial de la página
st.set_page_config(page_title="Control de Grupos Electrógenos", layout="wide")
st.title("⚡ Monitoreo Operativo: 2 Grupos Electrógenos (Tanque Compartido)")

# Nombre del archivo de respaldo local
ARCHIVO_DATOS = "registro_aeropuerto_ge.csv"

# --- PANEL LATERAL: FORMULARIO DE REGISTRO ---
st.sidebar.header("📝 Registro de Lectura Operativa")

with st.sidebar.form("form_ge_compartido", clear_on_submit=True):
    # Fecha y hora del registro
    fecha_registro = st.date_input("Fecha de lectura", value=datetime.now())
    hora_registro = st.time_input("Hora de lectura", value=datetime.now().time())
    
    st.markdown("---")
    st.subheader("⛽ Tanque de Combustible (General)")
    combustible_tanque = st.number_input(
        "Nivel del Tanque (Galones):", 
        min_value=0.0, 
        step=1.0, 
        format="%.1f"
    )
    
    st.markdown("---")
    st.subheader("⚙️ Grupo Electrógeno 01")
    horometro_ge1 = st.number_input("Horómetro GE-01 (Horas):", min_value=0.0, step=0.1, format="%.1f")
    alarma_ge1 = st.checkbox("⚠️ ¿Alarma activa en GE-01?")
    detalle_ge1 = st.text_input("Detalle Alarma GE-01 (opcional):")
    
    st.markdown("---")
    st.subheader("⚙️ Grupo Electrógeno 02")
    horometro_ge2 = st.number_input("Horómetro GE-02 (Horas):", min_value=0.0, step=0.1, format="%.1f")
    alarma_ge2 = st.checkbox("⚠️ ¿Alarma activa en GE-02?")
    detalle_ge2 = st.text_input("Detalle Alarma GE-02 (opcional):")
    
    st.markdown("---")
    operador = st.text_input("Técnico / Operador responsable:")
    
    # Botón de envío
    submitted = st.form_submit_button("Guardar Registro")
    
    if submitted:
        fecha_hora_str = f"{fecha_registro} {hora_registro.strftime('%H:%M')}"
        
        # Consolidar la información estructurada
        nuevo_registro = {
            "Fecha_Hora": fecha_hora_str,
            "Combustible_Galones": combustible_tanque,
            "Horas_GE1": horometro_ge1,
            "Alarma_GE1": f"Sí - {detalle_ge1}" if alarma_ge1 else "Ninguna",
            "Horas_GE2": horometro_ge2,
            "Alarma_GE2": f"Sí - {detalle_ge2}" if alarma_ge2 else "Ninguna",
            "Operador": operador if operador else "No especificado"
        }
        
        df_nuevo = pd.DataFrame([nuevo_registro])
        
        try:
            with open(ARCHIVO_DATOS, 'r') as f:
                header_flag = False
        except FileNotFoundError:
            header_flag = True
            
        df_nuevo.to_csv(ARCHIVO_DATOS, mode='a', header=header_flag, index=False)
        st.sidebar.success("¡Registro guardado con éxito!")
        st.rerun()

# --- VISTA PRINCIPAL DEL DASHBOARD ---
st.markdown("---")

try:
    df = pd.read_csv(ARCHIVO_DATOS)
    
    if not df.empty:
        # Métricas generales arriba
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Registros", len(df))
        col2.metric("Nivel Tanque Actual", f"{df['Combustible_Galones'].iloc[-1]:,.1f} gal")
        col3.metric("Horómetro Último GE-01", f"{df['Horas_GE1'].iloc[-1]:,.1f} h")
        col4.metric("Horómetro Último GE-02", f"{df['Horas_GE2'].iloc[-1]:,.1f} h")
        
        # Gráficos de tendencias
        st.subheader("📊 Tendencias Operativas")
        
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            st.markdown("**Nivel del Tanque Compartido (Galones)**")
            st.line_chart(df, x="Fecha_Hora", y="Combustible_Galones")
            
        with col_g2:
            st.markdown("**Horas de Funcionamiento (GE-01 vs GE-02)**")
            df_horometros = df[["Fecha_Hora", "Horas_GE1", "Horas_GE2"]].set_index("Fecha_Hora")
            st.line_chart(df_horometros)
            
        # Tabla de historial completo
        st.subheader("📋 Historial de Registros Detallado")
        st.dataframe(df.sort_values(by="Fecha_Hora", ascending=False), use_container_width=True)
        
    else:
        st.info("El archivo de registros está vacío. Comienza ingresando datos en el panel lateral.")

except FileNotFoundError:
    st.info("👋 ¡Bienvenido! Aún no hay un archivo de datos creado. Usa el formulario de la izquierda para registrar la primera lectura.")
