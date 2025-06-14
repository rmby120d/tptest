
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
pct_si = (df_eval['Respuestas'] == 'Sí').mean() * 100
pct_no = (df_eval['Respuestas'] == 'No').mean() * 100
pct_na = (df_eval['Respuestas'] == 'No aplica').mean() * 100

# Cumplimiento por Bloque e Ítem
block_comp = df_eval.groupby('Bloque').apply(lambda x: (x['Respuestas'] == 'Sí').mean() * 100).reset_index(name='Cumplimiento (%)')

# Crear pestañas
tabs = st.tabs(["Visión General", "Detalle", "Tópicos", "Insights"])

# Visión General
with tabs[0]:
    st.subheader("KPIs y Gráficos Destacados")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tasa cumplimiento global", f"{pct_si:.1f}%")
    c2.metric("Tasa incumplimiento global", f"{pct_no:.1f}%")
    c3.metric("Tasa no aplicable", f"{pct_na:.1f}%")
    c4.empty()  # espacio para futuros KPIs

    # Gauge para cumplimiento global
    gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=pct_si,
        title={'text': "Cumplimiento Global (%)"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "green"},
            'steps': [
                {'range': [0, 60],  'color': "lightcoral"},
                {'range': [60, 80], 'color': "gold"},
                {'range': [80, 100],'color': "lightgreen"}
            ],
        }
    ))
    st.plotly_chart(gauge, use_container_width=True)

    # Radar chart de cumplimiento por bloque
    bloques = block_comp['Bloque'].tolist()
    valores = block_comp['Cumplimiento (%)'].tolist()
    bloques.append(bloques[0])
    valores.append(valores[0])
    radar = go.Figure(go.Scatterpolar(
        r=valores,
        theta=bloques,
        fill='toself',
        name='Cumplimiento por Bloque'
    ))
    radar.update_layout(polar=dict(radialaxis=dict(range=[0,100])), showlegend=False)
    st.plotly_chart(radar, use_container_width=True)

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
    # Recalcular cumplimiento por ítem para insights
    item_comp = df_eval.groupby('Ítem').apply(lambda x: (x['Respuestas'] == 'Sí').mean() * 100).reset_index(name='Cumplimiento (%)')
    best_items = item_comp.nlargest(5, 'Cumplimiento (%)')
    worst_items = item_comp.nsmallest(5, 'Cumplimiento (%)')
    st.subheader("Top 5 Ítems Mejor Cumplidos")
    st.table(best_items)
    st.subheader("Top 5 Ítems con Menor Cumplimiento")
    st.table(worst_items)
    st.subheader("Ejemplos de Alertas 'No'")
    df_no = df_eval[df_eval['Respuestas'] == 'No']
    for _, row in df_no.head(10).iterrows():
        st.write(f"- Llamada `{row['Llamada']}`, Ítem: **{row['Ítem']}**")
