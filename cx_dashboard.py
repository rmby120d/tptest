import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Configuración de la página
st.set_page_config(page_title="Evaluación de Calidad de Llamadas", layout="wide")
st.title("Evaluación de Calidad de Llamadas")
service = st.selectbox("Seleccionar plantilla", ["Segurcaixa eCommerce", "Otra plantilla"])

# Generar datos de muestra
np.random.seed(42)
agents_list = ["Juan Pérez", "Ana Gómez", "Carlos Ruiz", "Lucía Martínez", "Miguel Torres"]
num_samples = 100

# IDs
ids = [f"#{i:03d}" for i in range(1, num_samples + 1)]
# Fechas aleatorias entre el 1 y el 10 de junio de 2025
dates = [pd.Timestamp("2025-06-01") + pd.to_timedelta(np.random.randint(0, 10), unit='D') + pd.to_timedelta(np.random.randint(0, 24*3600), unit='s') for _ in range(num_samples)]
# Duraciones en segundos (entre 3 y 10 minutos)
durations = np.random.randint(180, 600, size=num_samples)
# Puntajes entre 60 y 100
scores = np.random.randint(60, 100, size=num_samples)

# DataFrame de detalle
df_detail = pd.DataFrame({
    "ID": ids,
    "Agente": np.random.choice(agents_list, size=num_samples),
    "Fecha/Hora": [d.strftime("%d/%m/%Y %H:%M") for d in dates],
    "Duración (s)": durations,
    "Puntaje": scores
})

# Tendencia diaria promedio de puntaje
df_trend = (df_detail
            .assign(Fecha=lambda d: pd.to_datetime(d['Fecha/Hora'], dayfirst=True).dt.date)
            .groupby('Fecha')['Puntaje']
            .mean()
            .reset_index())

# Tópicos de ejemplo
df_topic = pd.DataFrame({
    "Tópico": ["Escucha Activa", "Cumplimiento Script", "Empatía", "Claridad"],
    "Promedio": [88, 74, 82, 90]
})
# Desempeño por agente
df_agents = pd.DataFrame({
    "Agente": agents_list,
    "Duración (s)": [df_detail[df_detail['Agente']==a]['Duración (s)'].mean() for a in agents_list],
    "Puntaje": [df_detail[df_detail['Agente']==a]['Puntaje'].mean() for a in agents_list]
})

# Mock alerts/insights
alertas_criticas = [f"{row['ID']} – Puntaje bajo ({row['Puntaje']})" for _, row in df_detail[df_detail['Puntaje'] < 70].head(5).iterrows()]
insights_ia = ["Reforzar saludo estándar en llamadas con empatía baja"]
recomendaciones = ["Coaching para manejo de objeciones"]

# Crear pestañas
tabs = st.tabs(["Visión General", "Detalle", "Tópicos", "Agentes", "Alertas", "Reportes"])

# Visión General
with tabs[0]:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Puntaje Global", f"{df_detail['Puntaje'].mean():.0f}")
    c2.metric("Operaciones", "90")
    c3.metric("Tech/Producto", "78")
    c4.metric("Alertas Críticas", str(len(alertas_criticas)))

    st.subheader("Tendencia de Calidad")
    fig_line = px.line(df_trend, x="Fecha", y="Puntaje", markers=True)
    st.plotly_chart(fig_line, use_container_width=True)

    st.subheader("Alertas Resumidas")
    for a in alertas_criticas[:3]:
        st.write(f"- {a}")

# Detalle
with tabs[1]:
    st.subheader("Detalle por Evaluación (100 muestras)")
    st.dataframe(df_detail, use_container_width=True)

# Tópicos
with tabs[2]:
    st.subheader("Análisis por Tópico")
    fig_bar = px.bar(df_topic, x="Tópico", y="Promedio", text="Promedio")
    st.plotly_chart(fig_bar, use_container_width=True)

    st.subheader("Nube de Palabras")
    text = " ".join(["empatía"] * 20 + ["script"] * 15 + ["escucha"] * 25)
    wc = WordCloud(width=400, height=200).generate(text)
    fig, ax = plt.subplots()
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)

# Agentes
with tabs[3]:
    st.subheader("Desempeño por Agente/Equipo")
    fig_scatter = px.scatter(df_agents, x="Duración (s)", y="Puntaje", text="Agente", size="Puntaje")
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.write("Ranking de Agentes")
    ranking = df_agents.sort_values("Puntaje", ascending=False)
    for _, row in ranking.iterrows():
        st.write(f"- {row['Agente']} – {row['Puntaje']:.0f}")

# Alertas e Insights
with tabs[4]:
    st.subheader("Llamadas Críticas")
    for a in alertas_criticas:
        st.write(f"- {a}")
    st.subheader("Insights IA")
    for i in insights_ia:
        st.write(f"- {i}")
    st.subheader("Recomendaciones")
    for r in recomendaciones:
        st.write(f"- {r}")

# Reportes
with tabs[5]:
    st.subheader("Reportes y Exportación")
    if st.button("Exportar PDF"):
        st.success("Funcionalidad de exportar PDF (pendiente)")
    if st.button("Exportar Excel"):
        st.success("Funcionalidad de exportar Excel (pendiente)")
    if st.button("Programar Envío Semanal"):
        st.success("Funcionalidad de programación (pendiente)")

# Para ejecutar:
# pip install streamlit pandas numpy plotly wordcloud matplotlib
# streamlit run cx_dashboard.py
