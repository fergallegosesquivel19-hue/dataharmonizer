import streamlit as st
import requests
import pandas as pd
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def mostrar():
    st.title("Automatización y Orquestación")
    st.write("Programa la ejecución desatendida de tus flujos de limpieza para mantener tus datos procesados actualizados de forma automática.")
    
    usuario_id = st.session_state.usuario.get("id")
    es_admin = st.session_state.usuario.get("es_admin", False)
    
    try:
        # Obtener flujos guardados
        endpoint = f"{BACKEND_URL}/flujos/all" if es_admin else f"{BACKEND_URL}/flujos/usuario/{usuario_id}"
        res_flujos = requests.get(endpoint)
        if res_flujos.status_code == 200:
            flujos = res_flujos.json()
            if not flujos:
                st.info("No tienes flujos guardados. Ve a 'Flujos de Limpieza', diseña uno y guárdalo.")
                return
                
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Programar un Flujo")
                opciones = {f['id']: f['nombre'] for f in flujos}
                seleccion_id = st.selectbox("Seleccione el flujo a programar", options=list(opciones.keys()), format_func=lambda x: opciones[x])
                
                if seleccion_id:
                    flujo_sel = next(f for f in flujos if f['id'] == seleccion_id)
                    st.write(f"**Cron Actual:** `{flujo_sel.get('cron_expresion') or 'No programado'}`")
                    
                    st.write("Configura la periocidad (expresión cron):")
                    cron_exp = st.text_input("Expresión CRON", "* * * * *", help="Ej. * * * * * (cada minuto), 0 8 * * * (diario a las 8 AM)")
                    
                    if st.button("⏰ Programar Ejecución", type="primary"):
                        res_prog = requests.post(f"{BACKEND_URL}/flujos/{seleccion_id}/programar", json={"cron_expresion": cron_exp})
                        if res_prog.status_code == 200:
                            st.success(f"Flujo programado con CRON: {cron_exp}")
                            st.rerun()
                        else:
                            st.error(f"Error: {res_prog.json().get('detail')}")
                            
                    if st.button("🛑 Detener Ejecución"):
                        res_det = requests.post(f"{BACKEND_URL}/flujos/{seleccion_id}/detener")
                        if res_det.status_code == 200:
                            st.success("Ejecución detenida.")
                            st.rerun()
                        else:
                            st.error("Error al detener.")
            
            with col2:
                st.subheader("Trabajos Activos en Segundo Plano")
                res_jobs = requests.get(f"{BACKEND_URL}/flujos/orquestador/trabajos")
                if res_jobs.status_code == 200:
                    jobs = res_jobs.json()
                    if jobs:
                        df_jobs = pd.DataFrame(jobs)
                        st.dataframe(df_jobs, use_container_width=True)
                    else:
                        st.info("El orquestador no tiene tareas pendientes.")
                else:
                    st.error("Error leyendo trabajos.")
                    
        else:
            st.error("Error obteniendo los flujos.")
            
    except Exception as e:
        st.error(f"Error conectando al backend: {e}")
