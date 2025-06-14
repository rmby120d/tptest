
import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Configuración de la página
st.set_page_config(page_title="Evaluación de Calidad de Llamadas (Simulación)", layout="wide")
st.title("Evaluación de Calidad de Llamadas - Simulación de 40 Conversaciones")

# Cargar simulación de 40 conversaciones
uploaded_file = st.file_uploader(
    "Sube el CSV de simulación (conversaciones_40_sim.csv)", 
    type=["csv"]
)
if not uploaded_file:
    st.warning("Por favor, sube el archivo `conversaciones_40_sim.csv` para continuar.")
    st.stop()

# Lee el CSV
df_eval = pd.read_csv(uploaded_file)
# Asegurarse de que 'Llamada' sea tipo texto
df_eval['Llamada'] = df_eval['Llamada'].astype(str)

# Métricas generales
num_calls = df_eval['Llamada'].nunique()
num_items = df_eval['Ítem'].nunique()

# Crear pestañas
tabs = st.tabs(["Visión General", "Detalle", "Tópicos", "Insights"])

# Visión General
with tabs[0]:
    st.subheader("Resumen General")
    col1, col2 = st.columns(2)
    col1.metric("Número de llamadas", num_calls)
    col2.metric("Criterios por llamada", num_items)

    # Distribución de respuestas
    resp_counts = df_eval['Respuestas'].value_counts().reset_index()
    resp_counts.columns = ['Respuesta', 'Conteo']
    fig_pie = px.pie(
        resp_counts, 
        names='Respuesta', 
        values='Conteo', 
        title="Distribución de Respuestas"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# Detalle
with tabs[1]:
    st.subheader("Detalle de Evaluaciones")
    st.dataframe(df_eval, height=600, use_container_width=True)

# Tópicos
with tabs[2]:
    st.subheader("Frecuencia por Ítem")
    df_items = df_eval['Ítem'].value_counts().reset_index()
    df_items.columns = ['Ítem', 'Conteo']
    fig_bar = px.bar(
        df_items, 
        x='Ítem', 
        y='Conteo', 
        text='Conteo', 
        title="Conteo de Evaluaciones por Ítem"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    st.subheader("Nube de Palabras de Ítems")
    text = " ".join(df_eval['Ítem'].tolist())
    wc = WordCloud(width=800, height=300).generate(text)
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)

# Insights
with tabs[3]:
    st.subheader("Alertas 'No'")
    df_no = df_eval[df_eval['Respuestas'] == 'No']
    for _, row in df_no.head(10).iterrows():
        st.write(f"- Llamada `{row['Llamada']}`, Ítem: **{row['Ítem']}**")

