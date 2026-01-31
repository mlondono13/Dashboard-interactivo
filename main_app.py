import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# Configuración de página
st.set_page_config(page_title="Explorador Universal de Datos", layout="wide")

st.title("📂 Analizador de Datos Universal (EDA)")
st.markdown("Sube cualquier archivo CSV y el sistema detectará automáticamente las variables.")

# --- CARGA DE DATOS ---
uploaded_file = st.file_uploader("Sube tu archivo CSV aquí", type=['csv'])

if uploaded_file is not None:
    try:
        # Intentar leer el archivo
        df = pd.read_csv(uploaded_file)
        
        # Limpieza básica para evitar errores en gráficas
        df = df.dropna()

        # IDENTIFICACIÓN DINÁMICA DE COLUMNAS
        cols_num = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
        cols_cat = df.select_dtypes(include=['object', 'category']).columns.tolist()

        # --- SIDEBAR DINÁMICO ---
        st.sidebar.header("⚙️ Filtros Globales")
        if cols_cat:
            col_filtro = st.sidebar.selectbox("Filtrar por:", ["Ninguno"] + cols_cat)
            if col_filtro != "Ninguno":
                opciones = st.sidebar.multiselect(f"Valores de {col_filtro}:", 
                                                 options=df[col_filtro].unique().tolist(),
                                                 default=df[col_filtro].unique().tolist())
                df = df[df[col_filtro].isin(opciones)]

        # --- SECCIONES EDA ---
        tab1, tab2, tab3 = st.tabs(["🔢 Cuantitativo", "🗂️ Cualitativo", "📈 Gráficas Cruzadas"])

        # 1. ANÁLISIS CUANTITATIVO
        with tab1:
            if cols_num:
                st.subheader("Análisis de Variables Numéricas")
                var_num = st.selectbox("Selecciona Variable Numérica:", cols_num)
                
                c1, c2 = st.columns([2, 1])
                with c1:
                    # CORRECCIÓN: Histogramas directos
                    fig_hist = px.histogram(df, x=var_num, marginal="box", 
                                            title=f"Distribución de {var_num}",
                                            color_discrete_sequence=['#636EFA'])
                    st.plotly_chart(fig_hist, use_container_width=True)
                with c2:
                    st.write("**Estadísticas:**")
                    st.table(df[var_num].describe())
            else:
                st.warning("No hay columnas numéricas.")

        # 2. ANÁLISIS CUALITATIVO (AQUÍ ESTABA EL ERROR)
        with tab2:
            if cols_cat:
                st.subheader("Análisis de Variables Categóricas")
                var_cat = st.selectbox("Selecciona Variable Categórica:", cols_cat)
                
                # CORRECCIÓN: Usamos un método más seguro para el conteo
                df_counts = df[var_cat].value_counts().reset_index()
                # Renombramos explícitamente las columnas para evitar el error de 'index'
                df_counts.columns = [var_cat, 'conteo']
                
                fig_bar = px.bar(df_counts, 
                                 x=var_cat, 
                                 y='conteo', 
                                 title=f"Frecuencia de {var_cat}",
                                 color=var_cat)
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.warning("No hay columnas categóricas.")

        # 3. GRÁFICAS CRUZADAS
        with tab3:
            st.subheader("Explorador de Relaciones Dinámicas")
            if len(cols_num) >= 2:
                col_x, col_y = st.columns(2)
                with col_x:
                    sel_x = st.selectbox("Eje X (Numérico):", cols_num, key="x_axis_unique")
                with col_y:
                    sel_y = st.selectbox("Eje Y (Numérico):", cols_num, key="y_axis_unique")
                
                sel_col = st.selectbox("Color por (Categoría):", ["Sin color"] + cols_cat)
                
                # CORRECCIÓN: Parámetros dinámicos para Scatter
                scatter_params = {
                    "data_frame": df,
                    "x": sel_x,
                    "y": sel_y,
                    "title": f"{sel_x} vs {sel_y}"
                }
                
                if sel_col != "Sin color":
                    scatter_params["color"] = sel_col
                else:
                    # Solo añadir línea de tendencia si NO hay color (para evitar errores de compatibilidad)
                    scatter_params["trendline"] = "ols"

                fig_scatter = px.scatter(**scatter_params)
                st.plotly_chart(fig_scatter, use_container_width=True)
            else:
                st.error("Se necesitan más datos numéricos.")

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")

else:
    st.info("💡 Sube un archivo CSV para comenzar.")
