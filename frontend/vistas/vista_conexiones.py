import streamlit as st
import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def mostrar():
    st.title("Gestión de Conexiones")
    st.write("Aquí puedes subir archivos Excel/CSV o configurar conexiones a bases de datos.")

    usuario_id = st.session_state.usuario.get("id")

    tab1, tab2 = st.tabs(["Subir Archivo", "Conexión a Base de Datos"])

    with tab1:
        st.subheader("Subir Archivo (Excel o CSV)")
        uploaded_file = st.file_uploader("Elige un archivo", type=['csv', 'xlsx', 'xls'])
        
        if uploaded_file is not None:
            if st.button("Guardar y Procesar Archivo"):
                with st.spinner("Subiendo archivo para hacerlo inmutable..."):
                    try:
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                        data = {"usuario_id": usuario_id}
                        res = requests.post(f"{BACKEND_URL}/conexiones/upload", files=files, data=data)
                        
                        if res.status_code == 200:
                            st.success("Archivo subido correctamente. ¡Copia de trabajo mutable creada y original protegido!")
                        else:
                            st.error(f"Error al subir: {res.json().get('detail')}")
                    except Exception as e:
                        st.error(f"Fallo de conexión al backend: {e}")

    with tab2:
        st.subheader("Conectar a Base de Datos Externa")
        with st.form("form_db"):
            tipo_db = st.selectbox("Tipo de Motor", ["PostgreSQL", "SQL Server", "MariaDB"])
            host = st.text_input("Host/IP")
            db_name = st.text_input("Nombre de la BD")
            user = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            
            if st.form_submit_button("Probar Conexión y Guardar"):
                st.info("Funcionalidad de conexión a BD en construcción. (Mock)")
