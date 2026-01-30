#Acá irá el código de Python para el Dashboard
import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="EDA Energía Renovable", layout="wide")

st.title("⚡ Análisis Exploratorio: Proyectos de Energía")

# Carga de datos
@st.cache_data
def load_data():
    df = pd.read_csv('energia_renovable.csv')
    df['Fecha_Entrada_Operacion'] = pd.to_datetime(df['Fecha_Entrada_Operacion'])
    return df

df = load_data()

# Sidebar para filtros
st.sidebar.header("Filtros")
tecnologia = st.sidebar.multiselect("Selecciona Tecnología:", 
                                    options=df["Tecnologia"].unique(),
                                    default=df["Tecnologia"].unique())

df_selection = df[df["Tecnologia"].isin(tecnologia)]

# Métricas principales
col1, col2, col3 = st.columns(3)
col1.metric("Total Proyectos", len(df_selection))
col2.metric("Capacidad Total (MW)", f"{df_selection['Capacidad_Instalada_MW'].sum():,.2f}")
col3.metric("Inversión Promedio (MUSD)", f"{df_selection['Inversion_Inicial_MUSD'].mean():,.2f}")

# Gráficos Interactivos
st.markdown("---")
c1, c2 = st.columns(2)

with c1:
    st.subheader("Distribución por Tecnología")
    fig_tech = px.pie(df_selection, names='Tecnologia', values='Capacidad_Instalada_MW', hole=0.4)
    st.plotly_chart(fig_tech, use_container_width=True)

with c2:
    st.subheader("Inversión vs Generación Diaria")
    fig_scatter = px.scatter(df_selection, x="Inversion_Inicial_MUSD", y="Generacion_Diaria_MWh", 
                             color="Tecnologia", size="Eficiencia_Planta_Pct", hover_name="ID_Proyecto")
    st.plotly_chart(fig_scatter, use_container_width=True)
