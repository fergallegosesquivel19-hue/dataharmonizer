import streamlit as st
from vistas import vista_login, vista_conexiones, vista_editor_excel, vista_flujo_limpieza, vista_dashboards, vista_automatizacion, vista_gestion_usuarios

st.set_page_config(page_title="Plataforma de Datos", page_icon="📊", layout="wide")

if "usuario" not in st.session_state:
    st.session_state.usuario = None

def sidebar_navegacion():
    st.sidebar.title("Navegación")
    
    if st.session_state.usuario is None:
        return "Login"
    
    nombre = st.session_state.usuario.get("nombre", "Usuario")
    es_admin = st.session_state.usuario.get("es_admin", False)
    
    st.sidebar.write(f"Hola, **{nombre}**")
    
    menu = ["Conexiones", "Editor Excel", "Flujos de Limpieza", "Dashboards", "Automatización"]
    
    if es_admin:
        menu.append("Gestión de Usuarios")
        
    menu.append("Cerrar Sesión")
    
    return st.sidebar.radio("Ir a", menu)

if __name__ == "__main__":
    opcion = sidebar_navegacion()

    if opcion == "Login":
        vista_login.mostrar()
    elif opcion == "Conexiones":
        vista_conexiones.mostrar()
    elif opcion == "Editor Excel":
        vista_editor_excel.mostrar()
    elif opcion == "Flujos de Limpieza":
        vista_flujo_limpieza.mostrar()
    elif opcion == "Dashboards":
        vista_dashboards.mostrar()
    elif opcion == "Automatización":
        vista_automatizacion.mostrar()
    elif opcion == "Gestión de Usuarios":
        vista_gestion_usuarios.mostrar()
    elif opcion == "Cerrar Sesión":
        st.session_state.usuario = None
        st.rerun()
