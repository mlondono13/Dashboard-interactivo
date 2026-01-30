import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

# Configuración de la página
st.set_page_config(page_title="EDA Energías Renovables", layout="wide")

st.title("⚡ Dashboard de Análisis de Energía Renovable")
st.markdown("Sube tu archivo `.csv` para comenzar el análisis exploratorio.")

# --- SECCIÓN DE CARGA DE DATOS ---
uploaded_file = st.file_uploader("Selecciona un archivo CSV", type=['csv'])

if uploaded_file is not None:
    try:
        # Intentamos leer el archivo
        df = pd.read_csv(uploaded_file)
        
        # Validación mínima: verificar si existen columnas esperadas
        # Si el archivo subido es el de 'energia_renovable.csv', procesamos fechas
        if 'Fecha_Entrada_Operacion' in df.columns:
            df['Fecha_Entrada_Operacion'] = pd.to_datetime(df['Fecha_Entrada_Operacion'])

        st.success("¡Datos cargados correctamente!")

        # --- EXPLORACIÓN INICIAL ---
        tabs = st.tabs(["📊 Visualización General", "📈 Relaciones y Filtros", "🔍 Datos Crudos"])

        with tabs[2]:
            st.subheader("Vista Previa de los Datos")
            st.dataframe(df.head(10))
            st.subheader("Estadísticas Descriptivas")
            st.write(df.describe())

        with tabs[0]:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Distribución por Tecnología")
                if 'Tecnologia' in df.columns:
                    fig_pie = px.pie(df, names='Tecnologia', hole=0.3, color_discrete_sequence=px.colors.sequential.RdBu)
                    st.plotly_chart(fig_pie, use_container_width=True)
                else:
                    st.warning("No se encontró la columna 'Tecnologia'")

            with col2:
                st.subheader("Capacidad por Operador")
                if 'Operador' in df.columns and 'Capacidad_Instalada_MW' in df.columns:
                    fig_bar = px.bar(df, x='Operador', y='Capacidad_Instalada_MW', color='Tecnologia')
                    st.plotly_chart(fig_bar, use_container_width=True)

        with tabs[1]:
            st.subheader("Análisis de Inversión vs Eficiencia")
            if 'Inversion_Inicial_MUSD' in df.columns and 'Eficiencia_Planta_Pct' in df.columns:
                fig_scatter = px.scatter(df, x='Inversion_Inicial_MUSD', y='Eficiencia_Planta_Pct', 
                                         color='Tecnologia', size='Capacidad_Instalada_MW',
                                         hover_data=['ID_Proyecto'])
                st.plotly_chart(fig_scatter, use_container_width=True)

    except Exception as e:
        # El bloque 'try' captura cualquier error (archivo corrupto, columnas faltantes, etc.)
        st.error(f"❌ Error al procesar el archivo: {e}")
        st.info("Asegúrate de que el archivo sea un CSV válido y tenga el formato correcto.")

else:
    st.info("Esperando la carga del archivo... Por favor, sube el archivo 'energia_renovable.csv' en el panel superior.")
    # Imagen de ejemplo de cómo se vería el componente de carga
