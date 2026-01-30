import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# Configuración inicial
st.set_page_config(page_title="EDA Dinámico", layout="wide")

st.title("📊 Análisis Exploratorio de Datos Dinámico")
st.markdown("Carga tu archivo CSV y explora las variables según su naturaleza.")

# --- CARGA DE DATOS ---
uploaded_file = st.file_uploader("Sube tu archivo CSV", type=['csv'])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        
        # --- BARRA LATERAL (FILTROS DINÁMICOS) ---
        st.sidebar.header("⚙️ Configuración de Filtros")
        
        # Identificar tipos de columnas automáticamente
        cols_cat = df.select_dtypes(include=['object']).columns.tolist()
        cols_num = df.select_dtypes(include=['float64', 'int64']).columns.tolist()

        # Filtro dinámico por una variable categórica (si existe)
        if cols_cat:
            cat_filter = st.sidebar.selectbox("Filtrar por categoría:", ["Todos"] + cols_cat)
            if cat_filter != "Todos":
                val_filter = st.sidebar.multiselect(f"Valores de {cat_filter}:", 
                                                   options=df[cat_filter].unique(),
                                                   default=df[cat_filter].unique())
                df = df[df[cat_filter].isin(val_filter)]

        # --- SECCIONES POR TABS ---
        tab1, tab2, tab3 = st.tabs(["🔢 Cuantitativos", "🗂️ Cualitativos", "📈 Gráficos Personalizados"])

        # --- SECCIÓN CUANTITATIVA ---
        with tab1:
            st.header("Análisis de Variables Numéricas")
            if cols_num:
                col_sel = st.selectbox("Selecciona una variable para ver su distribución:", cols_num)
                
                c1, c2 = st.columns(2)
                with c1:
                    fig_hist = px.histogram(df, x=col_sel, marginal="box", 
                                            title=f"Histograma de {col_sel}",
                                            color_discrete_sequence=['indianred'])
                    st.plotly_chart(fig_hist, use_container_width=True)
                
                with c2:
                    st.write("**Estadísticas Descriptivas:**")
                    st.write(df[col_sel].describe())
                
                st.subheader("Matriz de Correlación")
                if len(cols_num) > 1:
                    fig_corr, ax = plt.subplots()
                    sns.heatmap(df[cols_num].corr(), annot=True, cmap='coolwarm', ax=ax)
                    st.pyplot(fig_corr)
            else:
                st.warning("No hay columnas numéricas detectadas.")

        # --- SECCIÓN CUALITATIVA ---
        with tab2:
            st.header("Análisis de Variables Categóricas")
            if cols_cat:
                cat_sel = st.selectbox("Selecciona una categoría para contar:", cols_cat)
                
                fig_bar = px.bar(df[cat_sel].value_counts().reset_index(), 
                                 x='index', y=cat_sel, 
                                 labels={'index': cat_sel, cat_sel: 'Conteo'},
                                 title=f"Frecuencia de {cat_sel}",
                                 color='index')
                st.plotly_chart(fig_bar, use_container_width=True)
                
                st.write("**Tabla de Frecuencias:**")
                st.table(df[cat_sel].value_counts())
            else:
                st.warning("No hay columnas categóricas detectadas.")

        # --- SECCIÓN DE GRÁFICAS DINÁMICAS ---
        with tab3:
            st.header("Explorador de Relaciones")
            if len(cols_num) >= 2:
                x_axis = st.selectbox("Eje X (Numérico):", cols_num, index=0)
                y_axis = st.selectbox("Eje Y (Numérico):", cols_num, index=1)
                
                color_axis = None
                if cols_cat:
                    color_axis = st.selectbox("Color por (Categoría):", ["Ninguno"] + cols_cat)
                
                fig_scatter = px.scatter(df, x=x_axis, y=y_axis, 
                                         color=color_axis if color_axis != "Ninguno" else None,
                                         title=f"Relación {x_axis} vs {y_axis}",
                                         trendline="ols" if color_axis == "Ninguno" else None)
                st.plotly_chart(fig_scatter, use_container_width=True)
            else:
                st.warning("Se necesitan al menos 2 columnas numéricas para comparar.")

    except Exception as e:
        st.error(f"Hubo un error al procesar los datos: {e}")

else:
    st.info("👋 ¡Bienvenido! Por favor sube un archivo CSV en el panel de la izquierda para comenzar.")
