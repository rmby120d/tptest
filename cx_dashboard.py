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

# Datos de muestra
fechas = pd.date_range(start="2025-06-01", periods=10, freq="D")
puntajes = np.random.randint(70, 95, size=10)

df_trend = pd.DataFrame({"Fecha": fechas, "Puntaje": puntajes})

df_detail = pd.DataFrame([
    {"ID": "#001", "Agente": "Juan Pérez", "Fecha/Hora": "14/06/2025 10:32", "Duración (s)": 324, "Puntaje": 82},
    {"ID": "#002", "Agente": "Ana Gómez", "Fecha/Hora": "14/06/2025 11:10", "Duración (s)": 290, "Puntaje": 88},
    {"ID": "#003", "Agente": "Carlos Ruiz", "Fecha/Hora": "14/06/2025 12:05", "Duración (s)": 370, "Puntaje": 76},
    {"ID": "#004", "Agente": "Lucía Martínez", "Fecha/Hora": "14/06/2025 12:45", "Duración (s)": 300, "Puntaje": 91},
    {"ID": "#005", "Agente": "Miguel Torres", "Fecha/Hora": "14/06/2025 13:15", "Duración (s)": 270, "Puntaje": 84},
])

df_topic = pd.DataFrame({
    "Tópico": ["Escucha Activa", "Cumplimiento Script", "Empatía", "Claridad"],
    "Promedio": [88, 74, 82, 90]
})

df_agents = pd.DataFrame({
    "Agente": ["Ana Gómez", "Lucía Martínez", "Juan Pérez", "Miguel Torres", "Carlos Ruiz"],
    "Duración (s)": [290, 300, 324, 270, 370],
    "Puntaje": [92, 91, 85, 84, 76]
})

# Mock alerts/insights
alertas_criticas = ["#001 – Empatía baja", "#003 – Duración excesiva"]
insights_ia = ["Reforzar saludo estándar en 5 llamadas", "Reducir silencios > 3s en respuestas"]
recomendaciones = ["Coaching para manejo de objeciones"]

# Tabs
tabs = st.tabs(["Visión General", "Detalle", "Tópicos", "Agentes", "Alertas", "Reportes"])

# Visión General
with tabs[0]:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Puntaje Global", f"{df_trend['Puntaje'].mean():.0f}")
    c2.metric("Operaciones", "90")
    c3.metric("Tech/Producto", "78")
    c4.metric("Alertas Críticas", str(len(alertas_criticas)))

    st.subheader("Tendencia de Calidad")
    fig_line = px.line(df_trend, x="Fecha", y="Puntaje", markers=True)
    st.plotly_chart(fig_line, use_container_width=True)

    st.subheader("Alertas Resumidas")
    for a in ["Juan Pérez: baja empatía (2)", "Ana Gómez: script <70%", "Carlos Ruiz: demora >30s"]:
        st.write(f"- {a}")

# Detalle
with tabs[1]:
    st.subheader("Detalle por Evaluación")
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
    for i, row in df_agents.sort_values("Puntaje", ascending=False).iterrows():
        st.write(f"- {row['Agente']} – {row['Puntaje']}")

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
# pip install streamlit pandas plotly wordcloud matplotlib
# streamlit run streamlit_dashboard.py
