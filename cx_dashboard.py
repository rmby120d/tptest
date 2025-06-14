
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Color corporativo y secundario
COLOR_CORP = "#6d84e3"
COLOR_SEC = "#555555"

# Configuración
st.set_page_config(page_title="Evaluación de Calidad de Llamadas (Completo)", layout="wide")
st.title("Dashboard de Calidad de Llamadas y Sentimiento")

# Subida del CSV
uploaded_file = st.file_uploader(
    "Sube el CSV de simulación con sentimiento (conversaciones_40_sim_sentimiento.csv)",
    type=["csv"]
)
if not uploaded_file:
    st.warning("Por favor, sube `conversaciones_40_sim_sentimiento.csv` para continuar.")
    st.stop()

# Lectura
df = pd.read_csv(uploaded_file)
df['Llamada'] = df['Llamada'].astype(str)

# KPIs globales
pct_si = (df['Respuestas'] == 'Sí').mean() * 100
pct_no = (df['Respuestas'] == 'No').mean() * 100
pct_na = (df['Respuestas'] == 'No aplica').mean() * 100

# Cumplimiento por bloque e ítem
block_comp = df.groupby('Bloque').apply(lambda x: (x['Respuestas']=='Sí').mean()*100).reset_index(name='Cumplimiento (%)')
item_comp  = df.groupby('Ítem').apply(lambda x: (x['Respuestas']=='Sí').mean()*100).reset_index(name='Cumplimiento (%)')

# Crear pestañas
tabs = st.tabs(["Visión General","Detalle","Tópicos","Insights","Heatmap","Sentimiento"])

# 1) Visión General
with tabs[0]:
    st.subheader("KPIs Principales")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Tasa Sí",        f"{pct_si:.1f}%")
    c2.metric("Tasa No",        f"{pct_no:.1f}%")
    c3.metric("Tasa No aplica", f"{pct_na:.1f}%")
    c4.empty()
    # Gauge
    gauge = go.Figure(go.Indicator(
        mode="gauge+number", value=pct_si,
        title={'text':"Cumplimiento Global (%)"},
        gauge={'axis':{'range':[0,100]},
               'bar':{'color':COLOR_CORP},
               'steps':[
                   {'range':[0,60],  'color':"lightcoral"},
                   {'range':[60,80], 'color':"gold"},
                   {'range':[80,100],'color':"lightgreen"}
               ]}
    ))
    gauge.update_layout(paper_bgcolor='white', font_color=COLOR_CORP)
    st.plotly_chart(gauge, use_container_width=True)
    # Radar
    bloques = block_comp['Bloque'].tolist()
    valores = block_comp['Cumplimiento (%)'].tolist()
    bloques.append(bloques[0]); valores.append(valores[0])
    radar = go.Figure(go.Scatterpolar(r=valores, theta=bloques, fill='toself', marker_color=COLOR_CORP))
    radar.update_layout(polar=dict(radialaxis=dict(range=[0,100])), showlegend=False)
    st.plotly_chart(radar, use_container_width=True)

# 2) Detalle
with tabs[1]:
    st.subheader("Detalle de Evaluaciones")
    st.dataframe(df, height=600, use_container_width=True)

# 3) Tópicos
with tabs[2]:
    st.subheader("Frecuencia por Ítem")
    df_items = df['Ítem'].value_counts().rename_axis('Ítem').reset_index(name='Conteo')
    bar = px.bar(df_items, x='Ítem', y='Conteo', text='Conteo', color_discrete_sequence=[COLOR_CORP])
    st.plotly_chart(bar, use_container_width=True)
    st.subheader("Nube de Palabras")
    text = " ".join(df['Ítem'])
    wc = WordCloud(width=800, height=300, background_color='white').generate(text)
    fig, ax = plt.subplots(figsize=(12,4))
    ax.imshow(wc.recolor(color_func=lambda *args,**kwargs: COLOR_CORP), interpolation='bilinear')
    ax.axis('off')
    st.pyplot(fig)

# 4) Insights
with tabs[3]:
    st.subheader("Top 5 Mejor Cumplidos")
    st.table(item_comp.nlargest(5, 'Cumplimiento (%)'))
    st.subheader("Top 5 Peor Cumplidos")
    st.table(item_comp.nsmallest(5, 'Cumplimiento (%)'))
    # Pareto de fallos
    st.subheader("Pareto de Fallos por Ítem")
    df_no = df[df['Respuestas']=='No']
    cnt = df_no['Ítem'].value_counts().reset_index()
    cnt.columns = ['Ítem','Fails']
    cnt = cnt.sort_values('Fails', ascending=False)
    cnt['CumPct'] = cnt['Fails'].cumsum()/cnt['Fails'].sum()*100
    pareto = go.Figure()
    pareto.add_trace(go.Bar(x=cnt['Ítem'], y=cnt['Fails'], name='Fallos', marker_color=COLOR_CORP))
    pareto.add_trace(go.Scatter(x=cnt['Ítem'], y=cnt['CumPct'], name='Acumulado (%)', yaxis='y2', line_color=COLOR_CORP))
    pareto.update_layout(yaxis=dict(title='Fallos'),
                         yaxis2=dict(title='Acumulado (%)', overlaying='y', side='right', range=[0,100]),
                         xaxis_tickangle=-45, plot_bgcolor='white')
    st.plotly_chart(pareto, use_container_width=True)

# 5) Heatmap
with tabs[4]:
    st.subheader("Heatmap de Cumplimiento")
    mapping={"Sí":1,"No aplica":0,"No":-1}
    df_h = df.copy(); df_h['Value']=df_h['Respuestas'].map(mapping)
    heat = df_h.pivot(index='Ítem', columns='Llamada', values='Value')
    hfig = px.imshow(heat, labels={'x':'Llamada','y':'Ítem','color':'Valor'},
                     color_continuous_scale=["lightcoral","lightgray",COLOR_CORP],
                     aspect='auto', title='Heatmap')
    st.plotly_chart(hfig, use_container_width=True)

# 6) Sentimiento
with tabs[5]:
    st.subheader("Sentimiento Cliente vs Asesor")
    # Preparar datos
    df_melt = pd.melt(df, value_vars=['Sentimiento Cliente','Sentimiento Asesor'],
                      var_name='Rol', value_name='Sentimiento')
    df_melt['Rol'] = df_melt['Rol'].map({'Sentimiento Cliente':'Cliente','Sentimiento Asesor':'Asesor'})
    counts = df_melt.groupby(['Sentimiento','Rol']).size().reset_index(name='Conteo')
    # Gráfico de barras
    fig = px.bar(counts, x='Sentimiento', y='Conteo', color='Rol', barmode='group',
                 color_discrete_map={'Cliente':COLOR_CORP,'Asesor':COLOR_SEC},
                 text='Conteo', title='Distribución de Sentimientos')
    fig.update_layout(xaxis_tickangle=-45, plot_bgcolor='white')
    st.plotly_chart(fig, use_container_width=True)
