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
        
        # Limpieza básica de nulos para que no rompa las gráficas
        df = df.dropna()

        # IDENTIFICACIÓN DINÁMICA DE COLUMNAS
        # Filtramos columnas por tipo de dato
        cols_num = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
        cols_cat = df.select_dtypes(include=['object', 'category']).columns.tolist()

        # --- SIDEBAR DINÁMICO ---
        st.sidebar.header("⚙️ Filtros Globales")
        if cols_cat:
            col_filtro = st.sidebar.selectbox("Filtrar por:", ["Ninguno"] + cols_cat)
            if col_filtro != "Ninguno":
                opciones = st.sidebar.multiselect(f"Valores de {col_filtro}:", 
                                                 options=df[col_filtro].unique(),
                                                 default=df[col_filtro].unique())
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
                    fig_hist = px.histogram(df, x=var_num, marginal="box", 
                                            title=f"Distribución de {var_num}",
                                            color_discrete_sequence=['#636EFA'])
                    st.plotly_chart(fig_hist, use_container_width=True)
                with c2:
                    st.write("**Estadísticas:**")
                    st.table(df[var_num].describe())
                
                if len(cols_num) > 1:
                    st.subheader("Matriz de Correlación")
                    fig_corr, ax = plt.subplots(figsize=(10, 5))
                    sns.heatmap(df[cols_num].corr(), annot=True, cmap='RdBu', ax=ax)
                    st.pyplot(fig_corr)
            else:
                st.warning("No se encontraron columnas numéricas en este archivo.")

        # 2. ANÁLISIS CUALITATIVO
        with tab2:
            if cols_cat:
                st.subheader("Análisis de Variables Categóricas")
                var_cat = st.selectbox("Selecciona Variable Categórica:", cols_cat)
                
                fig_bar = px.bar(df[var_cat].value_counts().reset_index(), 
                                 x='index', y=var_cat, 
                                 title=f"Conteo de {var_cat}",
                                 labels={'index': var_cat, var_cat: 'Frecuencia'},
                                 color='index')
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.warning("No se encontraron columnas categóricas.")

        # 3. GRÁFICAS CRUZADAS (EL "MOTOR" DEL EDA)
        with tab3:
            st.subheader("Explorador de Relaciones Dinámicas")
            if len(cols_num) >= 2:
                col_x, col_y = st.columns(2)
                with col_x:
                    sel_x = st.selectbox("Eje X (Numérico):", cols_num, key="x_axis")
                with col_y:
                    sel_y = st.selectbox("Eje Y (Numérico):", cols_num, key="y_axis")
                
                sel_col = st.selectbox("Color por (Categoría):", ["Sin color"] + cols_cat)
                
                color_param = sel_col if sel_col != "Sin color" else None
                
                fig_scatter = px.scatter(df, x=sel_x, y=sel_y, color=color_param,
                                         title=f"{sel_x} vs {sel_y}",
                                         trendline="ols" if not color_param else None)
                st.plotly_chart(fig_scatter, use_container_width=True)
            else:
                st.error("Se necesitan al menos 2 columnas numéricas para graficar relaciones.")

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")
        st.info("Asegúrate de que el CSV no esté vacío y tenga un formato estándar.")

else:
    st.info("💡 Sube un archivo CSV (como 'energia_renovable.csv' o 'social_media.csv') para comenzar.")
