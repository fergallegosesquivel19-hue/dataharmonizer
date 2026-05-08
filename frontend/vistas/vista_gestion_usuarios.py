import streamlit as st
import requests
import pandas as pd
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def mostrar():
    st.title("Gestión de Usuarios")
    
    st.subheader("Registrar Nuevo Usuario")
    with st.form("registro_usuario"):
        nuevo_email = st.text_input("Email")
        nuevo_nombre = st.text_input("Nombre")
        nueva_password = st.text_input("Contraseña", type="password")
        es_admin = st.checkbox("¿Es administrador?")
        
        if st.form_submit_button("Registrar"):
            try:
                payload = {
                    "email": nuevo_email,
                    "nombre": nuevo_nombre,
                    "password_hash": nueva_password,
                    "es_admin": es_admin
                }
                res = requests.post(f"{BACKEND_URL}/usuarios/", json=payload)
                if res.status_code == 200:
                    st.success(f"Usuario {nuevo_email} creado exitosamente.")
                else:
                    st.error(f"Error al crear usuario: {res.json().get('detail')}")
            except Exception as e:
                st.error(f"Error de conexión: {e}")

    st.divider()
    st.subheader("Usuarios Actuales")
    
    try:
        res = requests.get(f"{BACKEND_URL}/usuarios/")
        if res.status_code == 200:
            usuarios = res.json()
            if usuarios:
                df = pd.DataFrame(usuarios)
                df_mostrar = df[['id', 'email', 'nombre', 'es_admin']]
                st.dataframe(df_mostrar, use_container_width=True)
                
                st.subheader("Eliminar Usuario")
                usuario_a_eliminar = st.selectbox("Seleccione un usuario para eliminar", df['id'].astype(str) + " - " + df['email'])
                id_eliminar = int(usuario_a_eliminar.split(" - ")[0])
                tiene_flujos = st.checkbox("¿Simular que tiene flujos activos? (Para probar la regla de negocio)")
                
                if st.button("Eliminar Seleccionado"):
                    if id_eliminar == st.session_state.usuario['id']:
                        st.warning("No puedes eliminar tu propio usuario en sesión.")
                    else:
                        del_res = requests.delete(f"{BACKEND_URL}/usuarios/{id_eliminar}?tiene_flujos={str(tiene_flujos).lower()}")
                        if del_res.status_code == 200:
                            st.success("Usuario eliminado.")
                            st.rerun()
                        else:
                            st.error(f"Error: {del_res.json().get('detail')}")
            else:
                st.info("No hay usuarios registrados.")
    except Exception as e:
        st.error(f"No se pudo cargar la lista de usuarios: {e}")
