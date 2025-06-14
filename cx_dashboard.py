import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Configuración de la página
st.set_page_config(page_title="Evaluación de Calidad de Llamadas", layout="wide")
st.title("Evaluación de Calidad de Llamadas")

# Carga de plantilla de evaluación: subir archivo si no está disponible
uploaded_file = st.file_uploader("Sube la plantilla Excel de SegurCaixa", type=["xlsx"])
if uploaded_file is None:
    st.warning("Por favor, sube el archivo 'Plan de Calidad emitida SegurCaixa eCommerce.xlsx' para continuar.")
    st.stop()

# Leer plantilla desde el archivo subido	raw = pd.read_excel(uploaded_file, header=4)
# Procesar encabezados
titles = raw.iloc[0]
raw = raw[1:]
titles_map = {col: titles[col] for col in raw.columns}
raw = raw.rename(columns=titles_map)
# Seleccionar columnas relevantes
df_templates = raw[[ 'Bloque','Ítem','Pauta','Descripción','Respuestas','PENC','PECUF','PECC','PECN']].dropna(subset=['Ítem']).reset_index(drop=True)

# Generar datos de muestra
np.random.seed(42)
agents_list = ["Juan Pérez", "Ana Gómez", "Carlos Ruiz", "Lucía Martínez", "Miguel Torres"]
num_samples = 100
# IDs, fechas, duraciones, puntajes aleatorios
ids = [f"#{i:03d}" for i in range(1, num_samples + 1)]
dates = [pd.Timestamp("2025-06-01") + pd.to_timedelta(np.random.randint(0, 10), unit='D') + pd.to_timedelta(np.random.randint(0, 24*3600), unit='s') for _ in range(num_samples)]
durations = np.random.randint(180, 600, size=num_samples)
scores = np.random.randint(60, 100, size=num_samples)
# DataFrame de detalle
 df_detail = pd.DataFrame({
    'ID': ids,
    'Agente': np.random.choice(agents_list, size=num_samples),
    'Fecha/Hora': [d.strftime('%d/%m/%Y %H:%M') for d in dates],
    'Duración (s)': durations,
    'Puntaje': scores
})
# Mixer de plantilla por muestra
df_sample = df_templates.sample(n=num_samples, replace=True, random_state=42).reset_index(drop=True)
df_detail = pd.concat([df_detail, df_sample], axis=1)

# Tendencia diaria
df_trend = (pd.to_datetime(df_detail['Fecha/Hora'], dayfirst=True)
            .to_frame(name='FechaHora')
            .assign(Fecha=lambda d: d['FechaHora'].dt.date)
            .join(df_detail['Puntaje'])
            .groupby('Fecha')['Puntaje']
            .mean()
            .reset_index())
# Desempeño por agente
df_agents = df_detail.groupby('Agente').agg({'Duración (s)': 'mean', 'Puntaje': 'mean'}).reset_index()
# Alertas e insights
alertas_criticas = [f"{row['ID']} – Puntaje bajo ({row['Puntaje']})" for _, row in df_detail[df_detail['Puntaje']<70].head(5).iterrows()]
insights_ia = ["Reforzar saludo estándar en llamadas con empatía baja"]
recomendaciones = ["Coaching para manejo de objeciones"]

# Pestañas
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

# Detalle
with tabs[1]:
    st.subheader(f"Detalle por Evaluación ({num_samples} muestras)")
    st.dataframe(df_detail, height=600, use_container_width=True)

# Tópicos
with tabs[2]:
    st.subheader("Análisis por Tópico")
    df_items_count = df_detail['Ítem'].value_counts().rename_axis('Ítem').reset_index(name='Count')
    fig_bar = px.bar(df_items_count, x='Ítem', y='Count', text='Count')
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

# Reportes
with tabs[5]:
    st.subheader("Reportes y Exportación")
    if st.button("Exportar PDF"): st.success("Pendiente")
    if st.button("Exportar Excel"): st.success("Pendiente")
    if st.button("Programar Envío Semanal"): st.success("Pendiente")

# Para ejecutar:
# pip install -r requirements.txt
# streamlit run cx_dashboard.py
