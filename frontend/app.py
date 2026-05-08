import streamlit as st
from vistas import vista_login, vista_conexiones, vista_editor_excel, vista_flujo_limpieza, vista_dashboards, vista_automatizacion, vista_gestion_usuarios

st.set_page_config(page_title="Plataforma de Datos", page_icon="📊", layout="wide")

# Inyección de CSS Personalizado para un diseño moderno, corporativo y oscuro
st.markdown("""
<style>
/* Forzar fuente Century Gothic en toda la aplicación */
* {
    font-family: 'Century Gothic', sans-serif !important;
}

/* Fondo principal */
.stApp {
    background-color: #21483A;
}

/* Títulos y textos generales */
h1, h2, h3, h4, h5, h6, p, span {
    color: #F4CAAB !important;
}

/* Tarjetas de métricas */
div[data-testid="metric-container"] {
    background-color: #4F766F;
    border-radius: 10px;
    padding: 15px 20px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    border-left: 5px solid #E2928D;
    transition: transform 0.2s ease;
}
div[data-testid="metric-container"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.4);
}
div[data-testid="metric-container"] label {
    color: #E6C570 !important;
}
div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
    color: #F4CAAB !important;
}

/* Efectos Hover dinámicos en los botones */
.stButton > button {
    background-color: #4F766F !important;
    color: #F4CAAB !important;
    border-radius: 8px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.3) !important;
    border: 1px solid #6D7172 !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 10px rgba(0,0,0,0.4) !important;
    border-color: #E2928D !important;
    color: #E2928D !important;
}

/* Estilización de la barra lateral (Sidebar) */
[data-testid="stSidebar"] {
    background-color: #4F766F !important;
}
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
    color: #F4CAAB !important;
}

/* Radio buttons como bloques clickeables en la barra lateral */
[data-testid="stSidebar"] div.row-widget.stRadio > div {
    display: flex;
    flex-direction: column;
    gap: 8px;
}
[data-testid="stSidebar"] div.row-widget.stRadio > div > label {
    background-color: #21483A !important;
    padding: 10px 15px;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s ease-in-out;
    border: 1px solid transparent;
}
[data-testid="stSidebar"] div.row-widget.stRadio > div > label:hover {
    background-color: #6D7172 !important;
    transform: translateX(5px);
    border-left: 3px solid #E6C570 !important;
}
[data-testid="stSidebar"] div.row-widget.stRadio > div > label > div[data-testid="stMarkdownContainer"] > p {
    color: #F4CAAB !important;
}
</style>
""", unsafe_allow_html=True)

if "usuario" not in st.session_state:
    st.session_state.usuario = None

def sidebar_navegacion():
    st.sidebar.title("🧭 Navegación")
    st.sidebar.divider()
    
    if st.session_state.usuario is None:
        return "Login"
    
    nombre = st.session_state.usuario.get("nombre", "Usuario")
    es_admin = st.session_state.usuario.get("es_admin", False)
    
    st.sidebar.markdown(f"👋 Hola, **{nombre}**")
    st.sidebar.divider()
    
    menu = ["🔌 Conexiones", "📝 Editor Excel", "🧹 Flujos de Limpieza", "📊 Dashboards", "🤖 Automatización"]
    
    if es_admin:
        menu.append("👥 Gestión de Usuarios")
        
    menu.append("🚪 Cerrar Sesión")
    
    opcion_con_icono = st.sidebar.radio("Ir a:", menu, label_visibility="collapsed")
    
    mapeo = {
        "🔌 Conexiones": "Conexiones",
        "📝 Editor Excel": "Editor Excel",
        "🧹 Flujos de Limpieza": "Flujos de Limpieza",
        "📊 Dashboards": "Dashboards",
        "🤖 Automatización": "Automatización",
        "👥 Gestión de Usuarios": "Gestión de Usuarios",
        "🚪 Cerrar Sesión": "Cerrar Sesión"
    }
    
    return mapeo.get(opcion_con_icono, "Login")

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
