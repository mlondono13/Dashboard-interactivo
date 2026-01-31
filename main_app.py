import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
from groq import Groq

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Universal EDA & AI Assistant", layout="wide")

st.title("📂 Explorador de Datos + Asistente AI")
st.markdown("Carga tu dataset y utiliza Inteligencia Artificial para interpretar los hallazgos.")

# --- BARRA LATERAL: API KEY Y FILTROS ---
st.sidebar.header("🔑 Configuración de Groq")
groq_api_key = st.sidebar.text_input("Ingresa tu Groq API Key:", type="password")

# --- CARGA DE DATOS ---
uploaded_file = st.file_uploader("Sube tu archivo CSV aquí", type=['csv'])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        
        # Limpieza de duplicados
        cols = pd.Series(df.columns)
        for i, col in enumerate(cols):
            if (cols == col).sum() > 1:
                count = list(cols[:i]).count(col)
                if count > 0:
                    cols[i] = f"{col}_{count}"
        df.columns = cols
        df = df.dropna()

        cols_num = df.select_dtypes(include=['number']).columns.tolist()
        cols_cat = df.select_dtypes(include=['object', 'category']).columns.tolist()

        # --- SECCIONES DEL EDA (TABS) ---
        tab1, tab2, tab3, tab4 = st.tabs(["🔢 Cuantitativo", "🗂️ Cualitativo", "📈 Gráficas", "🤖 Asistente AI"])

        # TAB 1, 2 y 3 (Mantienen la lógica anterior)
        with tab1:
            if cols_num:
                var_num = st.selectbox("Selecciona métrica:", cols_num)
                fig_hist = px.histogram(df, x=var_num, marginal="box", title=f"Análisis de {var_num}")
                st.plotly_chart(fig_hist, use_container_width=True)
                st.table(df[var_num].describe())

        with tab2:
            if cols_cat:
                var_cat = st.selectbox("Selecciona categoría:", cols_cat)
                df_counts = df[var_cat].value_counts().reset_index()
                df_counts.columns = [var_cat, 'conteo']
                fig_bar = px.bar(df_counts, x=var_cat, y='conteo', color=var_cat)
                st.plotly_chart(fig_bar, use_container_width=True)

        with tab3:
            if len(cols_num) >= 2:
                c_x = st.selectbox("Eje X:", cols_num, key="x_asist")
                c_y = st.selectbox("Eje Y:", cols_num, key="y_asist")
                fig_scat = px.scatter(df, x=c_x, y=c_y, title=f"{c_x} vs {c_y}")
                st.plotly_chart(fig_scat, use_container_width=True)

        # --- TAB 4: ASISTENTE AI CON LLAMA 3.3 ---
        with tab4:
            st.header("Chat con Llama 3.3 Versatile")
            
            if not groq_api_key:
                st.warning("⚠️ Por favor, ingresa tu API Key de Groq en la barra lateral para activar el asistente.")
            else:
                user_question = st.text_area("Pregunta algo sobre tus datos:", 
                                            placeholder="Ej: ¿Qué tendencia observas entre el uso de redes y el sueño?")
                
                if st.button("Analizar con IA"):
                    if user_question:
                        try:
                            client = Groq(api_key=groq_api_key)
                            
                            # Preparamos un resumen de los datos para darle contexto a la IA
                            data_summary = f"""
                            El dataset tiene {df.shape[0]} filas y {df.shape[1]} columnas.
                            Columnas numéricas: {cols_num}
                            Columnas categóricas: {cols_cat}
                            Resumen estadístico básico:
                            {df.describe().to_string()}
                            """
                            
                            with st.spinner("Llama 3.3 está pensando..."):
                                chat_completion = client.chat.completions.create(
                                    messages=[
                                        {
                                            "role": "system",
                                            "content": "Eres un experto analista de datos. Utiliza el resumen del dataset proporcionado para responder de forma concisa y profesional."
                                        },
                                        {
                                            "role": "user",
                                            "content": f"Contexto del dataset:\n{data_summary}\n\nPregunta del usuario: {user_question}"
                                        }
                                    ],
                                    model="llama-3.3-70b-versatile",
                                )
                                
                                response = chat_completion.choices[0].message.content
                                st.markdown("### 💡 Respuesta del Asistente:")
                                st.write(response)
                                
                        except Exception as e:
                            st.error(f"Error con la API de Groq: {e}")
                    else:
                        st.info("Escribe una pregunta para continuar.")

    except Exception as e:
        st.error(f"❌ Error crítico: {e}")

else:
    st.info("👋 Carga un CSV para habilitar el análisis y el asistente AI.")
