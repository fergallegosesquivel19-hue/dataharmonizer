import streamlit as st
import plotly.express as px
import pandas as pd
import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def mostrar():
    st.title("Dashboards y Reportes Analíticos")
    st.write("Visualiza los datos que han sido procesados y homologados por tus flujos automáticos.")
    
    try:
        # 1. Obtener lista de archivos procesados
        res_archivos = requests.get(f"{BACKEND_URL}/dashboards/archivos")
        
        if res_archivos.status_code == 200:
            archivos = res_archivos.json()
            if not archivos:
                st.info("No hay archivos procesados aún. Configura y ejecuta un flujo desde Automatización.")
                return
            
            # 2. Seleccionar archivo
            archivo_sel = st.selectbox("Seleccione el conjunto de datos procesado:", archivos)
            
            if archivo_sel:
                with st.spinner("Cargando datos..."):
                    res_datos = requests.get(f"{BACKEND_URL}/dashboards/datos/{archivo_sel}")
                    
                if res_datos.status_code == 200:
                    datos = res_datos.json().get("data", [])
                    if not datos:
                        st.warning("El archivo seleccionado no contiene datos.")
                        return
                        
                    df = pd.DataFrame(datos)
                    columnas = list(df.columns)
                    
                    st.success(f"Datos cargados: {df.shape[0]} filas, {df.shape[1]} columnas.")
                    with st.expander("Ver Datos Tabulares", expanded=False):
                        st.dataframe(df, use_container_width=True)
                        
                    st.divider()
                    st.subheader("Generador de Gráficos")
                    
                    tabs = st.tabs(["Gráfico de Barras", "Gráfico de Pastel", "Gráfico de Dispersión"])
                    
                    # --- BARRAS ---
                    with tabs[0]:
                        col1, col2 = st.columns(2)
                        x_bar = col1.selectbox("Eje X (Categoría)", columnas, key="bar_x")
                        y_bar = col2.selectbox("Eje Y (Valor Numérico)", columnas, key="bar_y")
                        
                        if st.button("Generar Barras"):
                            try:
                                fig_bar = px.bar(df, x=x_bar, y=y_bar, title=f"{y_bar} por {x_bar}", color=x_bar)
                                st.plotly_chart(fig_bar, use_container_width=True)
                            except Exception as e:
                                st.error(f"Error generando gráfico: Verifica que el Eje Y sea numérico. ({e})")
                                
                    # --- PASTEL ---
                    with tabs[1]:
                        col1, col2 = st.columns(2)
                        names_pie = col1.selectbox("Categorías (Agrupación)", columnas, key="pie_names")
                        values_pie = col2.selectbox("Valores (Suma)", columnas, key="pie_values")
                        
                        if st.button("Generar Pastel"):
                            try:
                                fig_pie = px.pie(df, names=names_pie, values=values_pie, title=f"Distribución de {values_pie} por {names_pie}")
                                st.plotly_chart(fig_pie, use_container_width=True)
                            except Exception as e:
                                st.error(f"Error generando gráfico: {e}")
                                
                    # --- DISPERSIÓN ---
                    with tabs[2]:
                        col1, col2, col3 = st.columns(3)
                        x_scat = col1.selectbox("Eje X", columnas, key="scat_x")
                        y_scat = col2.selectbox("Eje Y", columnas, key="scat_y")
                        color_scat = col3.selectbox("Color (Opcional)", ["Ninguno"] + columnas, key="scat_color")
                        
                        if st.button("Generar Dispersión"):
                            try:
                                c = color_scat if color_scat != "Ninguno" else None
                                fig_scat = px.scatter(df, x=x_scat, y=y_scat, color=c, title=f"Dispersión: {x_scat} vs {y_scat}")
                                st.plotly_chart(fig_scat, use_container_width=True)
                            except Exception as e:
                                st.error(f"Error generando gráfico: {e}")
                                
                else:
                    st.error("Error al obtener los datos del archivo.")
        else:
            st.error("Error conectando con el servicio de Dashboards.")
            
    except Exception as e:
        st.error(f"Error de conexión: {e}")
