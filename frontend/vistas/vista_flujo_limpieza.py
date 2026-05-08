import streamlit as st
import requests
import pandas as pd
import json
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def mostrar():
    st.title("Flujo de Tratamiento y Homologación")
    st.write("Diseña la tubería de limpieza de datos seleccionando un archivo y aplicando reglas paso a paso.")
    
    usuario_id = st.session_state.usuario.get("id")
    
    try:
        res = requests.get(f"{BACKEND_URL}/conexiones/usuario/{usuario_id}")
        if res.status_code == 200:
            conexiones = res.json()
            archivos = [c for c in conexiones if c['tipo'] == 'EXCEL']
            
            if not archivos:
                st.info("Sube un archivo en 'Conexiones' primero.")
                return
                
            opciones = {c['id']: c['nombre'] for c in archivos}
            seleccion_id = st.selectbox("1. Seleccione el archivo origen", options=list(opciones.keys()), format_func=lambda x: opciones[x])
            
            if seleccion_id:
                res_datos = requests.get(f"{BACKEND_URL}/conexiones/{seleccion_id}/datos")
                columnas = []
                if res_datos.status_code == 200:
                    data = res_datos.json().get("data", [])
                    if data:
                        columnas = list(data[0].keys())

                st.subheader("2. Diseñar Flujo de Reglas")
                
                if "reglas_flujo" not in st.session_state:
                    st.session_state.reglas_flujo = []
                    
                with st.expander("Añadir Nueva Regla", expanded=True):
                    tipo_regla = st.selectbox("Tipo de Operación", [
                        "eliminar_nulos", 
                        "reemplazar_nulos", 
                        "remover_duplicados", 
                        "mayusculas", 
                        "minusculas", 
                        "homologacion_difusa",
                        "cruce_bases"
                    ])
                    
                    params = {}
                    if tipo_regla in ["eliminar_nulos", "remover_duplicados", "mayusculas", "minusculas"]:
                        cols = st.multiselect("Columnas a aplicar (vacío para todas)", columnas)
                        if cols:
                            params["columnas"] = cols
                            
                    elif tipo_regla == "reemplazar_nulos":
                        cols = st.multiselect("Columnas a aplicar (vacío para todas)", columnas)
                        valor = st.text_input("Valor de reemplazo", "No aplica")
                        if cols:
                            params["columnas"] = cols
                        params["valor"] = valor
                        
                    elif tipo_regla == "homologacion_difusa":
                        col = st.selectbox("Columna a homologar", columnas)
                        lista_str = st.text_area("Lista Maestra (separada por comas)", "Paracetamol 500, Paracetamol 600, Ibuprofeno 400")
                        umbral = st.slider("Umbral de Similitud (%)", 50, 100, 80)
                        
                        params["columna"] = col
                        params["lista_maestra"] = [x.strip() for x in lista_str.split(",") if x.strip()]
                        params["umbral"] = umbral
                        
                        st.info("💡 **Regla Crítica Activa**: Si hay números en el texto (ej. dosis, medidas), la coincidencia numérica debe ser EXACTA sin importar el porcentaje de similitud textual.")
                    
                    elif tipo_regla == "cruce_bases":
                        opciones_B = {c['id']: c['nombre'] for c in archivos if c['id'] != seleccion_id}
                        if not opciones_B:
                            st.warning("Necesitas subir un segundo archivo para poder cruzar bases.")
                        else:
                            conexion_id_B = st.selectbox("Base B (Archivo a cruzar)", options=list(opciones_B.keys()), format_func=lambda x: opciones_B[x])
                            
                            res_datos_B = requests.get(f"{BACKEND_URL}/conexiones/{conexion_id_B}/datos")
                            columnas_B = []
                            if res_datos_B.status_code == 200:
                                data_B = res_datos_B.json().get("data", [])
                                if data_B:
                                    columnas_B = list(data_B[0].keys())
                                    
                            col_A = st.selectbox("Columna Llave de Base A", columnas)
                            col_B = st.selectbox("Columna Llave de Base B", columnas_B)
                            umbral = st.slider("Umbral de Similitud (%)", 50, 100, 80)
                            
                            params["conexion_id_B"] = conexion_id_B
                            params["columna_A"] = col_A
                            params["columna_B"] = col_B
                            params["umbral"] = umbral
                            
                            st.info("💡 **Regla Crítica Activa**: El cruce mantendrá la validación de números EXACTOS entre ambas columnas llave.")
                    
                    if st.button("➕ Agregar Regla al Flujo"):
                        st.session_state.reglas_flujo.append({"tipo": tipo_regla, "parametros": params})
                        st.success(f"Regla '{tipo_regla}' agregada.")
                        st.rerun()

                if st.session_state.reglas_flujo:
                    st.subheader("Reglas Actuales")
                    for i, regla in enumerate(st.session_state.reglas_flujo):
                        st.write(f"**{i+1}. {regla['tipo']}**: {regla['parametros']}")
                    
                    if st.button("Limpiar Flujo"):
                        st.session_state.reglas_flujo = []
                        st.rerun()
                        
                    st.divider()
                    
                    if st.button("🚀 Ejecutar Flujo y Previsualizar", type="primary"):
                        with st.spinner("Procesando datos en el backend..."):
                            payload = {
                                "conexion_id": seleccion_id,
                                "reglas": st.session_state.reglas_flujo
                            }
                            res_ejecutar = requests.post(f"{BACKEND_URL}/procesamiento/ejecutar_flujo", json=payload)
                            
                            if res_ejecutar.status_code == 200:
                                result_data = res_ejecutar.json().get("data", [])
                                if result_data:
                                    st.success("¡Flujo ejecutado exitosamente!")
                                    st.dataframe(pd.DataFrame(result_data))
                                else:
                                    st.warning("El resultado está vacío tras aplicar las reglas.")
                            else:
                                st.error(f"Error procesando: {res_ejecutar.json().get('detail')}")
                    
                    st.divider()
                    st.subheader("💾 Guardar Flujo para Automatización")
                    nombre_flujo = st.text_input("Nombre del Flujo", "Mi_Nuevo_Flujo")
                    if st.button("Guardar Flujo", type="secondary"):
                        if not nombre_flujo:
                            st.warning("Debes darle un nombre al flujo.")
                        else:
                            payload_guardar = {
                                "nombre": nombre_flujo,
                                "conexion_origen_id": seleccion_id,
                                "reglas": st.session_state.reglas_flujo,
                                "usuario_id": usuario_id
                            }
                            res_guardar = requests.post(f"{BACKEND_URL}/flujos/", json=payload_guardar)
                            if res_guardar.status_code == 200:
                                st.success("¡Flujo guardado! Ahora puedes programarlo en la pestaña de Automatización.")
                            else:
                                st.error("Error al guardar el flujo.")

    except Exception as e:
        st.error(f"Error conectando al backend: {e}")
