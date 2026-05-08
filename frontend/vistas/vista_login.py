import streamlit as st
import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def mostrar():
    st.title("Iniciar Sesión")
    with st.form("login"):
        email = st.text_input("Email")
        password = st.text_input("Contraseña", type="password")
        if st.form_submit_button("Entrar"):
            try:
                response = requests.post(f"{BACKEND_URL}/usuarios/login", json={"email": email, "password": password})
                if response.status_code == 200:
                    usuario_data = response.json()
                    st.session_state.usuario = usuario_data
                    st.rerun()
                else:
                    st.error(f"Error de credenciales: {response.json().get('detail', 'Credenciales incorrectas')}")
            except Exception as e:
                st.error(f"Error conectando al backend: {e}")
