# 🚀 Data Harmonizer: Enterprise Data Platform

![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)

**Data Harmonizer** es una plataforma robusta diseñada para la gobernanza, limpieza y homologación de datos farmacéuticos y comerciales. A diferencia de scripts simples, esta solución implementa una **Arquitectura Hexagonal** y principios **SOLID**, garantizando escalabilidad y mantenibilidad empresarial.

---

## 🛠️ Arquitectura Técnica

La plataforma está desacoplada en micro-contenedores para separar responsabilidades:

| Componente | Tecnología | Responsabilidad |
| :--- | :--- | :--- |
| **Frontend** | Streamlit | Interfaz de usuario, edición de celdas inmutables y dashboards. |
| **Backend API** | FastAPI | Procesamiento lógico, autenticación y orquestación de flujos. |
| **Base de Datos** | SQLite + SQLAlchemy | Persistencia de usuarios y logs de tareas automáticas. |
| **Motor de Datos** | Pandas + RapidFuzz | Limpieza profunda y homologación de catálogos. |

---

## ✨ Características Principales

### 1. 🔐 Seguridad de Nivel Bancario
- **Autenticación:** Sistema de login con hashing de contraseñas mediante `Passlib` y `Bcrypt`.
- **Roles:** Gestión de usuarios (Admin/User) para controlar quién puede editar o solo visualizar.

### 2. 🛡️ Inmutabilidad de Datos Originales
- El sistema nunca sobreescribe el archivo fuente. 
- Crea una **Copia de Trabajo** temporal para cada proceso, permitiendo auditorías de datos y reversión de cambios.

### 3. ⚖️ Regla Crítica: Homologación Sensible (Numerical Matching)
Esta es la joya de la corona del motor. En el cruce de catálogos, implementamos una lógica estricta para medidas:
- **Texto:** Búsqueda difusa (Fuzzy Match) para errores de dedo (ej. "Paracetmol" ≈ "Paracetamol").
- **Números:** Coincidencia **EXACTA**. 
  - ✅ "Paracetamol 500mg" se une con "Paracetamol 500mg".
  - ❌ "Paracetamol 500mg" **NUNCA** se unirá con "Paracetamol 600mg", evitando errores críticos de inventario.

### 4. 📊 Dashboards Interactivos
Visualización dinámica de la salud de los datos mediante gráficos de Plotly, permitiendo identificar duplicados y nulos de forma visual antes de la exportación.

---

## 🚀 Instalación y Despliegue

La plataforma está completamente dockerizada. Solo necesitas ejecutar:

```bash
# Clonar el proyecto
git clone [https://github.com/fergallegosesquivel19-hue/dataharmonizer.git](https://github.com/fergallegosesquivel19-hue/dataharmonizer.git)

# Levantar el entorno
docker-compose up --build