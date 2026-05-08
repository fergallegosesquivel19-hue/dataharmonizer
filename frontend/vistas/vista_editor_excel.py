import streamlit as st
import requests
import pandas as pd
import json
import os
import traceback

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def mostrar():
    st.title("Editor de Celdas Inmutable")
    st.write("Selecciona un archivo subido para previsualizar su copia de trabajo y hacer ajustes manuales antes de la automatización.")
    
    usuario_id = st.session_state.usuario.get("id")
    es_admin = st.session_state.usuario.get("es_admin", False)
    
    try:
        endpoint = f"{BACKEND_URL}/conexiones/all" if es_admin else f"{BACKEND_URL}/conexiones/usuario/{usuario_id}"
        res = requests.get(endpoint)
        if res.status_code == 200:
            conexiones = res.json()
            if conexiones:
                archivos = [c for c in conexiones if c['tipo'] == 'EXCEL']
                if archivos:
                    opciones = {c['id']: c['nombre'] for c in archivos}
                    seleccion_id = st.selectbox("Seleccione el archivo a editar", options=list(opciones.keys()), format_func=lambda x: opciones[x])
                    
                    if seleccion_id:
                        res_datos = requests.get(f"{BACKEND_URL}/conexiones/{seleccion_id}/datos")
                        if res_datos.status_code == 200:
                            data = res_datos.json().get("data", [])
                            if data:
                                df = pd.DataFrame(data)
                                
                                # --- MÉTRICAS RÁPIDAS ---
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Total de Filas", f"{len(df):,}")
                                with col2:
                                    st.metric("Valores Nulos", f"{int(df.isnull().sum().sum()):,}")
                                with col3:
                                    st.metric("Columnas", f"{len(df.columns):,}")
                                st.divider()
                                
                                st.write("📝 **Datos actuales (Copia de Trabajo)**")
                                edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
                                
                                if st.button("💾 Guardar Cambios Manuales"):
                                    df_json = edited_df.to_json(orient="records", date_format="iso")
                                    payload = {"data": json.loads(df_json)}
                                    res_put = requests.put(f"{BACKEND_URL}/conexiones/{seleccion_id}/datos", json=payload)
                                    if res_put.status_code == 200:
                                        st.success("Los cambios han sido guardados en la copia de trabajo. El archivo original sigue intacto.")
                                    else:
                                        st.error("Error al guardar cambios.")
                            else:
                                st.warning("El archivo está vacío.")
                        else:
                            st.error("Error cargando los datos del archivo.")
                else:
                    st.info("No has subido ningún archivo aún.")
            else:
                st.info("No tienes conexiones configuradas.")
    except Exception as e:
        error_msg = traceback.format_exc()
        st.error(f"Error conectando al backend: {e}\n\nDetalles:\n{error_msg}")
