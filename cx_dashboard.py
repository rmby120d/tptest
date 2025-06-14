
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Configuración de la página
st.set_page_config(page_title="Evaluación Calidad Llamadas (Simulación)", layout="wide")
st.title("Evaluación de Calidad de Llamadas - Simulación de 40 Conversaciones")

# Cargar simulación de 40 conversaciones
uploaded_file = st.file_uploader("Sube el CSV de simulación (conversaciones_40_sim.csv)", type=["csv"])
if not uploaded_file:
    st.warning("Por favor, sube el archivo `conversaciones_40_sim.csv` para continuar.")
    st.stop()

# Leer datos
df_eval = pd.read_csv(uploaded_file)
df_eval['Llamada'] = df_eval['Llamada'].astype(str)

# KPIs Globales
pct_si = (df_eval['Respuestas'] == 'Sí').mean() * 100
pct_no = (df_eval['Respuestas'] == 'No').mean() * 100
pct_na = (df_eval['Respuestas'] == 'No aplica').mean() * 100

# Cumplimiento por Bloque e Ítem
block_comp = df_eval.groupby('Bloque')    .apply(lambda x: (x['Respuestas'] == 'Sí').mean() * 100)    .reset_index(name='Cumplimiento (%)')
item_comp = df_eval.groupby('Ítem')    .apply(lambda x: (x['Respuestas'] == 'Sí').mean() * 100)    .reset_index(name='Cumplimiento (%)')

# Crear pestañas
tabs = st.tabs(["Visión General", "Detalle", "Tópicos", "Insights", "Heatmap"])

# Visión General
with tabs[0]:
    st.subheader("KPIs y Gráficos Destacados")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tasa Sí", f"{pct_si:.1f}%")
    c2.metric("Tasa No", f"{pct_no:.1f}%")
    c3.metric("Tasa No aplica", f"{pct_na:.1f}%")
    c4.empty()
    # Gauge cumplimiento global
    gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=pct_si,
        title={'text': "Cumplimiento Global (%)"},
        gauge={'axis': {'range': [0, 100]},
               'bar': {'color': "green"},
               'steps': [
                   {'range': [0, 60],  'color': "lightcoral"},
                   {'range': [60, 80], 'color': "gold"},
                   {'range': [80, 100],'color': "lightgreen"}
               ]}
    ))
    st.plotly_chart(gauge, use_container_width=True)
    # Radar cumplimiento por bloque
    bloques = block_comp['Bloque'].tolist()
    valores = block_comp['Cumplimiento (%)'].tolist()
    bloques.append(bloques[0]); valores.append(valores[0])
    radar = go.Figure(go.Scatterpolar(r=valores, theta=bloques, fill='toself'))
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
    fig_bar = px.bar(df_items, x='Ítem', y='Conteo', text='Conteo', title="Conteo por Ítem")
    st.plotly_chart(fig_bar, use_container_width=True)
    st.subheader("Nube de Palabras")
    text = " ".join(df_eval['Ítem'].tolist())
    wc = WordCloud(width=800, height=300).generate(text)
    fig, ax = plt.subplots(figsize=(12,4))
    ax.imshow(wc, interpolation='bilinear'); ax.axis('off')
    st.pyplot(fig)

# Insights
with tabs[3]:
    st.subheader("Top 5 Ítems Mejor Cumplidos")
    st.table(item_comp.nlargest(5, 'Cumplimiento (%)'))
    st.subheader("Top 5 Ítems con Menor Cumplimiento")
    st.table(item_comp.nsmallest(5, 'Cumplimiento (%)'))
    # Gráfico Pareto de fallos ('No')
    st.subheader("Gráfico Pareto de Fallos por Ítem")
    df_no = df_eval[df_eval['Respuestas'] == 'No']
    counts = df_no['Ítem'].value_counts().reset_index()
    counts.columns = ['Ítem','Fails']
    counts = counts.sort_values('Fails', ascending=False)
    counts['CumPct'] = counts['Fails'].cumsum() / counts['Fails'].sum() * 100
    pareto = go.Figure()
    pareto.add_trace(go.Bar(x=counts['Ítem'], y=counts['Fails'], name='Número de fallos'))
    pareto.add_trace(go.Scatter(x=counts['Ítem'], y=counts['CumPct'], name='Pct. acumulado', yaxis='y2'))
    pareto.update_layout(
        yaxis=dict(title='Número de fallos'),
        yaxis2=dict(title='Pct. acumulado', overlaying='y', side='right', range=[0,100]),
        xaxis_tickangle=-45
    )
    st.plotly_chart(pareto, use_container_width=True)

# Heatmap
with tabs[4]:
    st.subheader("Heatmap de Cumplimiento por Ítem y Llamada")
    mapping = {"Sí": 1, "No aplica": 0, "No": -1}
    df_h = df_eval.copy()
    df_h["Value"] = df_h["Respuestas"].map(mapping)
    heat_data = df_h.pivot(index='Ítem', columns='Llamada', values='Value')
    fig_heat = px.imshow(
        heat_data,
        labels={'x': "Llamada", 'y': "Ítem", 'color': "Valor"},
        x=heat_data.columns, y=heat_data.index,
        color_continuous_scale=["lightcoral","lightgray","lightgreen"],
        aspect="auto",
        title="Heatmap de Cumplimiento"
    )
    st.plotly_chart(fig_heat, use_container_width=True)

# Para ejecutar:
# pip install streamlit pandas plotly wordcloud matplotlib
# streamlit run cx_dashboard_sim.py
