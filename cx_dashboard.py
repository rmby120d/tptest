
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
df_eval['Llamada'] = df_eval['Llamada'].astype(str)

# KPIs Globales
total_evals = len(df_eval)
pct_si = (df_eval['Respuestas'] == 'Sí').mean() * 100
pct_no = (df_eval['Respuestas'] == 'No').mean() * 100
pct_na = (df_eval['Respuestas'] == 'No aplica').mean() * 100
comp_per_call = df_eval.groupby('Llamada').apply(lambda x: (x['Respuestas'] == 'Sí').mean()).mean() * 100

# Cumplimiento por Bloque e Ítem
block_comp = df_eval.groupby('Bloque').apply(lambda x: (x['Respuestas'] == 'Sí').mean() * 100).reset_index(name='Cumplimiento (%)')
item_comp = df_eval.groupby('Ítem').apply(lambda x: (x['Respuestas'] == 'Sí').mean() * 100).reset_index(name='Cumplimiento (%)')
best_items = item_comp.nlargest(5, 'Cumplimiento (%)')
worst_items = item_comp.nsmallest(5, 'Cumplimiento (%)')

# Métricas generales
num_calls = df_eval['Llamada'].nunique()
num_items = df_eval['Ítem'].nunique()

# Crear pestañas
tabs = st.tabs(["Visión General", "Detalle", "Tópicos", "Insights"])

# Visión General con KPIs
with tabs[0]:
    st.subheader("Resumen General y KPIs")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Número de llamadas", num_calls)
    c2.metric("Criterios por llamada", num_items)
    c3.metric("Tasa cumplimiento global", f"{pct_si:.1f}%")
    c4.metric("Tasa incumplimiento global", f"{pct_no:.1f}%")

    c5, c6 = st.columns(2)
    c5.metric("Tasa no aplicable", f"{pct_na:.1f}%")
    c6.metric("Promedio cumplimiento por llamada", f"{comp_per_call:.1f}%")

    st.markdown("---")
    st.subheader("Distribución de Respuestas")
    resp_counts = df_eval['Respuestas'].value_counts().reset_index()
    resp_counts.columns = ['Respuesta', 'Conteo']
    fig_pie = px.pie(resp_counts, names='Respuesta', values='Conteo', title="Distribución de Respuestas")
    st.plotly_chart(fig_pie, use_container_width=True)

    st.subheader("Cumplimiento por Bloque (%)")
    st.dataframe(block_comp, use_container_width=True)

# Detalle
with tabs[1]:
    st.subheader("Detalle de Evaluaciones")
    st.dataframe(df_eval, height=600, use_container_width=True)

# Tópicos
with tabs[2]:
    st.subheader("Frecuencia por Ítem")
    df_items = df_eval['Ítem'].value_counts().reset_index()
    df_items.columns = ['Ítem', 'Conteo']
    fig_bar = px.bar(df_items, x='Ítem', y='Conteo', text='Conteo', title="Conteo de Evaluaciones por Ítem")
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
    st.subheader("Top 5 Ítems Mejor Cumplidos")
    st.table(best_items)
    st.subheader("Top 5 Ítems con Menor Cumplimiento")
    st.table(worst_items)
    st.subheader("Ejemplos de Alertas 'No'")
    df_no = df_eval[df_eval['Respuestas'] == 'No']
    for _, row in df_no.head(10).iterrows():
        st.write(f"- Llamada `{row['Llamada']}`, Ítem: **{row['Ítem']}**")

# Para ejecutar:
# pip install streamlit pandas plotly wordcloud matplotlib
# streamlit run cx_dashboard_sim.py
