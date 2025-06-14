import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Colores corporativos
COLOR_CORP = "#6d84e3"
COLOR_SEC  = "#555555"

# Configuración de la página
st.set_page_config(page_title="Dashboard Calidad Llamadas", layout="wide")
st.title("Dashboard Calidad de Llamadas y Sentimiento")

# Carga del CSV
uploaded = st.sidebar.file_uploader(
    "Sube el CSV con sentimiento (conversaciones_40_sim_sentimiento.csv)", 
    type=["csv"]
)
if not uploaded:
    st.sidebar.warning("Sube el CSV para continuar")
    st.stop()

df = pd.read_csv(uploaded)
df['Llamada'] = df['Llamada'].astype(str)

# Métricas básicas
pct_si    = (df['Respuestas']=="Sí").mean()*100
pct_no    = (df['Respuestas']=="No").mean()*100
pct_na    = (df['Respuestas']=="No aplica").mean()*100

block_comp = (
    df.groupby('Bloque')['Respuestas']
      .apply(lambda x: (x=="Sí").mean()*100)
      .reset_index(name='Cumplimiento (%)')
)
item_comp  = (
    df.groupby('Ítem')['Respuestas']
      .apply(lambda x: (x=="Sí").mean()*100)
      .reset_index(name='Cumplimiento (%)')
)
call_comp  = (
    df.groupby('Llamada')['Respuestas']
      .apply(lambda x: (x=="Sí").mean()*100)
      .reset_index(name='Comp_%')
)

# Puntuaciones para boxplot/tendencia
score_map = {'Sí':1, 'No aplica':0, 'No':-1}
df['Score'] = df['Respuestas'].map(score_map)

# Pestañas
tabs = st.tabs(["Visión General","Detalle","Tópicos","Insights","Heatmap","Sentimiento"])

# 1) Visión General
with tabs[0]:
    st.subheader("KPIs Principales")
    c1,c2,c3 = st.columns(3)
    c1.metric("Tasa Sí", f"{pct_si:.1f}%")
    c2.metric("Tasa No", f"{pct_no:.1f}%")
    c3.metric("Tasa No aplica", f"{pct_na:.1f}%")
    st.markdown("---")
    # Gauge
    gauge = go.Figure(go.Indicator(
        mode="gauge+number", value=pct_si,
        title={'text': "Cumplimiento Global (%)"},
        gauge={'axis':{'range':[0,100]}, 'bar':{'color':COLOR_CORP},
               'steps':[
                   {'range':[0,60],'color':'lightcoral'},
                   {'range':[60,80],'color':'gold'},
                   {'range':[80,100],'color':'lightgreen'}
               ]}
    ))
    st.plotly_chart(gauge, use_container_width=True)
    # Radar
    labels = list(block_comp['Bloque'])
    values = list(block_comp['Cumplimiento (%)'])
    labels.append(labels[0]); values.append(values[0])
    radar = go.Figure(go.Scatterpolar(
        r=values, theta=labels, fill='toself', marker_color=COLOR_CORP
    ))
    radar.update_layout(polar=dict(radialaxis=dict(range=[0,100])), showlegend=False)
    st.plotly_chart(radar, use_container_width=True)

# 2) Detalle
with tabs[1]:
    st.subheader("Detalle de Evaluaciones")
    st.dataframe(df, height=500, use_container_width=True)

# 3) Tópicos
with tabs[2]:
    st.subheader("Frecuencia por Ítem")
    df_items = (
        df['Ítem']
        .value_counts()
        .rename_axis('Ítem')
        .reset_index(name='Conteo')
    )
    fig_topics = px.bar(
        df_items, x='Ítem', y='Conteo',
        text='Conteo', color_discrete_sequence=[COLOR_CORP]
    )
    st.plotly_chart(fig_topics, use_container_width=True)
    st.subheader("Nube de Palabras de Ítems")
    wc_text = " ".join(df['Ítem'])
    wc = WordCloud(width=800, height=300, background_color='white').generate(wc_text)
    fig_wc, ax_wc = plt.subplots(figsize=(12,4))
    ax_wc.imshow(
        wc.recolor(color_func=lambda *args,**kw:COLOR_CORP),
        interpolation='bilinear'
    )
    ax_wc.axis('off')
    st.pyplot(fig_wc)

# 4) Insights
with tabs[3]:
    st.subheader("Insights Avanzados")
    # 1. Correlación ítems
    corr_df = (
        df.pivot(index='Llamada', columns='Ítem', values='Score')
          .corr()
    )
    fig1 = px.imshow(corr_df, color_continuous_scale='Viridis', title='Correlación entre Ítems')
    st.plotly_chart(fig1, use_container_width=True)
    st.markdown("---")
    # 2. 100% Stacked Bar
    resp_pct = (
        df.groupby(['Ítem','Respuestas'])
          .size()
          .reset_index(name='Count')
    )
    resp_pct['Pct'] = (
        resp_pct.groupby('Ítem')['Count']
                .transform(lambda x: x/x.sum()*100)
    )
    fig2 = px.bar(resp_pct, x='Ítem', y='Pct', color='Respuestas', title='Distribución % por Ítem')
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown("---")
    # 3. Línea de evolución por llamada
    fig3 = px.line(call_comp, x='Llamada', y='Comp_%', title='Cumplimiento % por Llamada')
    st.plotly_chart(fig3, use_container_width=True)

# 5) Heatmap original
with tabs[4]:
    st.subheader("Heatmap de Cumplimiento")
    df_h = df.copy()
    df_h['Val'] = df_h['Score']
    heat = df_h.pivot(index='Ítem', columns='Llamada', values='Val')
    fig_heat = px.imshow(
        heat,
        labels={'x':'Llamada','y':'Ítem','color':'Score'},
        color_continuous_scale=["lightcoral","lightgray",COLOR_CORP],
        aspect='auto'
    )
    st.plotly_chart(fig_heat, use_container_width=True)

# 6) Sentimiento
with tabs[5]:
    st.subheader("Sentimiento Cliente vs Asesor")
    melt = pd.melt(
        df,
        value_vars=['Sentimiento Cliente','Sentimiento Asesor'],
        var_name='Rol', value_name='Sentimiento'
    )
    melt['Rol'] = melt['Rol'].map({
        'Sentimiento Cliente':'Cliente',
        'Sentimiento Asesor':'Asesor'
    })
    cnt = (
        melt.groupby(['Sentimiento','Rol'])
            .size()
            .reset_index(name='Conteo')
    )
    fig_sent = px.bar(
        cnt, x='Sentimiento', y='Conteo',
        color='Rol', barmode='group',
        color_discrete_map={'Cliente':COLOR_CORP,'Asesor':COLOR_SEC},
        text='Conteo', title='Distribución de Sentimientos'
    )
    st.plotly_chart(fig_sent, use_container_width=True)
