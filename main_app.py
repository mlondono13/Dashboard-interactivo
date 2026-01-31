import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Analizador Universal de Datos", layout="wide")

st.title("📂 Explorador de Datos Inteligente (EDA)")
st.markdown("Carga tu archivo CSV y la herramienta adaptará las gráficas automáticamente.")

# --- CARGA DE DATOS ---
uploaded_file = st.file_uploader("Sube tu archivo CSV aquí", type=['csv'])

if uploaded_file is not None:
    try:
        # 2. SOLUCIÓN A COLUMNAS DUPLICADAS
        df = pd.read_csv(uploaded_file)
        
        # Renombrar columnas duplicadas automáticamente (ej. Sensor, Sensor_1)
        cols = pd.Series(df.columns)
        for i, col in enumerate(cols):
            if (cols == col).sum() > 1:
                count = list(cols[:i]).count(col)
                if count > 0:
                    cols[i] = f"{col}_{count}"
        df.columns = cols

        # Limpieza básica
        df = df.dropna()

        # 3. DETECCIÓN AUTOMÁTICA DE VARIABLES
        # Numéricas: float e int / Categóricas: object y category
        cols_num = df.select_dtypes(include=['number']).columns.tolist()
        cols_cat = df.select_dtypes(include=['object', 'category']).columns.tolist()

        # --- SIDEBAR DINÁMICO (FILTROS) ---
        st.sidebar.header("⚙️ Filtros Globales")
        if cols_cat:
            col_filtro = st.sidebar.selectbox("Segmentar datos por:", ["Sin filtro"] + cols_cat)
            if col_filtro != "Sin filtro":
                opciones = st.sidebar.multiselect(f"Valores de {col_filtro}:", 
                                                 options=df[col_filtro].unique().tolist(),
                                                 default=df[col_filtro].unique().tolist())
                df = df[df[col_filtro].isin(opciones)]

        # --- SECCIONES DEL EDA (TABS) ---
        tab1, tab2, tab3 = st.tabs(["🔢 Cuantitativo", "🗂️ Cualitativo", "📈 Gráficas Cruzadas"])

        # TAB 1: ANÁLISIS NUMÉRICO
        with tab1:
            if cols_num:
                st.subheader("Distribución de Variables Numéricas")
                var_num = st.selectbox("Selecciona una métrica:", cols_num)
                
                c1, c2 = st.columns([2, 1])
                with c1:
                    fig_hist = px.histogram(df, x=var_num, marginal="box", 
                                            title=f"Análisis de {var_num}",
                                            color_discrete_sequence=['#3366CC'])
                    st.plotly_chart(fig_hist, use_container_width=True)
                with c2:
                    st.write("**Estadísticas Descriptivas:**")
                    st.table(df[var_num].describe())
            else:
                st.warning("No se detectaron columnas numéricas.")

        # TAB 2: ANÁLISIS CATEGÓRICO
        with tab2:
            if cols_cat:
                st.subheader("Análisis de Frecuencias")
                var_cat = st.selectbox("Selecciona una categoría:", cols_cat)
                
                # Solución al error de 'index': Renombrar columnas explícitamente
                df_counts = df[var_cat].value_counts().reset_index()
                df_counts.columns = [var_cat, 'conteo']
                
                fig_bar = px.bar(df_counts, 
                                 x=var_cat, 
                                 y='conteo', 
                                 title=f"Distribución de {var_cat}",
                                 color=var_cat,
                                 color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.warning("No se detectaron columnas categóricas.")

        # TAB 3: RELACIONES (SCATTER PLOTS)
        with tab3:
            st.subheader("Explorador de Correlaciones")
            if len(cols_num) >= 2:
                col_x, col_y = st.columns(2)
                with col_x:
                    sel_x = st.selectbox("Eje X (Numérico):", cols_num, key="x_universal")
                with col_y:
                    sel_y = st.selectbox("Eje Y (Numérico):", cols_num, key="y_universal")
                
                sel_color = st.selectbox("Color por (Categoría):", ["Ninguno"] + cols_cat)
                
                # Configuración dinámica del scatter
                params = {"data_frame": df, "x": sel_x, "y": sel_y, "title": f"{sel_x} vs {sel_y}"}
                if sel_color != "Ninguno":
                    params["color"] = sel_color
                
                fig_scatter = px.scatter(**params)
                st.plotly_chart(fig_scatter, use_container_width=True)
                
                # Matriz de correlación térmica
                if st.checkbox("Mostrar mapa de calor de correlación"):
                    fig_corr, ax = plt.subplots()
                    sns.heatmap(df[cols_num].corr(), annot=True, cmap='coolwarm', ax=ax)
                    st.pyplot(fig_corr)
            else:
                st.error("Se necesitan al menos 2 columnas numéricas para comparar relaciones.")

    except Exception as e:
        st.error(f"❌ Error crítico al procesar el archivo: {e}")

else:
    st.info("👋 Por favor, carga un archivo .csv en el panel de arriba para iniciar el análisis.")
