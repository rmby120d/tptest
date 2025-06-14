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

# Carga de plantilla de evaluación desde Excel
# Asegúrate de tener el archivo 'Plan de Calidad emitida SegurCaixa eCommerce.xlsx' en el mismo directorio
raw = pd.read_excel('Plan de Calidad emitida SegurCaixa eCommerce.xlsx', header=4)
# Primero fila con nombres de columnas
titles = raw.iloc[0]
raw = raw[1:]
# Renombrar columnas
titles_map = {col: titles[col] for col in raw.columns}
raw = raw.rename(columns=titles_map)
# Seleccionar y limpiar columnas relevantes
df_templates = raw[['Bloque','Ítem','Pauta','Descripción','Respuestas','PENC','PECUF','PECC','PECN']].copy()
df_templates = df_templates[df_templates['Ítem'].notna()]

defensor = np.random.RandomState(42)
# Generar datos de muestra
agents_list = ["Juan Pérez", "Ana Gómez", "Carlos Ruiz", "Lucía Martínez", "Miguel Torres"]
num_samples = 100

# IDs y fechas aleatorias
ids = [f"#{i:03d}" for i in range(1, num_samples + 1)]
dates = [pd.Timestamp("2025-06-01") + pd.to_timedelta(defensor.randint(0, 10), unit='D') + pd.to_timedelta(defensor.randint(0, 24*3600), unit='s') for _ in range(num_samples)]
durations = defensor.randint(180, 600, size=num_samples)
scores = defensor.randint(60, 100, size=num_samples)

# Tabla de detalle inicial
df_detail = pd.DataFrame({
    'ID': ids,
    'Agente': defensor.choice(agents_list, size=num_samples),
    'Fecha/Hora': [d.strftime('%d/%m/%Y %H:%M') for d in dates],
    'Duración (s)': durations,
    'Puntaje': scores
})

# Sample de plantilla para cada llamada
df_sample = df_templates.sample(n=num_samples, replace=True, random_state=42).reset_index(drop=True)
# Combinar columnas de plantilla
df_detail = pd.concat([df_detail, df_sample.reset_index(drop=True)], axis=1)

# DataFrame de tendencia diaria
df_trend = (df_detail
            .assign(Fecha=pd.to_datetime(df_detail['Fecha/Hora'], dayfirst=True).dt.date)
            .groupby('Fecha')['Puntaje']
            .mean()
            .reset_index())

# DataFrame de desempeño por agente
df_agents = (df_detail
             .groupby('Agente')
             .agg({'Duración (s)': 'mean', 'Puntaje': 'mean'})
             .reset_index())

# Alertas e insights
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
    for a in alertas_criticas[:3]: st.write(f"- {a}")

# Detalle
with tabs[1]:
    st.subheader(f"Detalle por Evaluación ({num_samples} muestras)")
    st.dataframe(df_detail, height=600, use_container_width=True)

# Tópicos
with tabs[2]:
    st.subheader("Análisis por Tópico")
    fig_bar = px.bar(df_templates.groupby('Ítem')['Pauta'].count().reset_index(name='Count'), x='Ítem', y='Count', text='Count')
    st.plotly_chart(fig_bar, use_container_width=True)

    st.subheader("Nube de Palabras")
    text = " ".join(df_detail['Ítem'].tolist())
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
    for _, row in df_agents.sort_values("Puntaje", ascending=False).iterrows():
        st.write(f"- {row['Agente']} – {row['Puntaje']:.0f}")

# Alertas e Insights
with tabs[4]:
    st.subheader("Llamadas Críticas")
    for a in alertas_criticas: st.write(f"- {a}")
    st.subheader("Insights IA")
    for i in insights_ia: st.write(f"- {i}")
    st.subheader("Recomendaciones")
    for r in recomendaciones: st.write(f"- {r}")

# Reportes
with tabs[5]:
    st.subheader("Reportes y Exportación")
    if st.button("Exportar PDF"): st.success("Pendiente")
    if st.button("Exportar Excel"): st.success("Pendiente")
    if st.button("Programar Envío Semanal"): st.success("Pendiente")

# Ejecutar:
# pip install -r requirements.txt
# streamlit run cx_dashboard.py
