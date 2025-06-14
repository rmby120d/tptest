
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Colores
COLOR_CORP = "#6d84e3"
COLOR_SEC = "#555555"

# Configuración
st.set_page_config(page_title="Dashboard Calidad Llamadas – Global", layout="wide")
st.title("Dashboard Calidad de Llamadas y Sentimiento")

# Carga de CSV
uploaded_file = st.sidebar.file_uploader(
    "Sube el CSV con sentimiento (conversaciones_40_sim_sentimiento.csv)", 
    type=["csv"]
)
if not uploaded_file:
    st.sidebar.warning("Sube el CSV para continuar")
    st.stop()
df = pd.read_csv(uploaded_file)
df['Llamada'] = df['Llamada'].astype(str)

# Cálculos resumen
pct_si = (df['Respuestas']=="Sí").mean()*100
pct_no = (df['Respuestas']=="No").mean()*100
pct_na = (df['Respuestas']=="No aplica").mean()*100
block_comp = df.groupby('Bloque').apply(lambda x:(x['Respuestas']=="Sí").mean()*100).reset_index(name='Cumplimiento (%)')
item_comp  = df.groupby('Ítem').apply(lambda x:(x['Respuestas']=="Sí").mean()*100).reset_index(name='Cumplimiento (%)')

# Navegación en pestañas
tabs = st.tabs(["Visión General","Detalle","Tópicos","Insights","Heatmap","Sentimiento"])

# 1. Visión General
with tabs[0]:
    st.subheader("KPIs Globales")
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
               'steps':[{'range':[0,60],'color':'lightcoral'},
                        {'range':[60,80],'color':'gold'},
                        {'range':[80,100],'color':'lightgreen'}]}
    ))
    st.plotly_chart(gauge, use_container_width=True)
    # Radar
    bloques = block_comp['Bloque'].tolist()
    valores = block_comp['Cumplimiento (%)'].tolist()
    bloques.append(bloques[0]); valores.append(valores[0])
    radar = go.Figure(go.Scatterpolar(r=valores, theta=bloques, fill='toself', marker_color=COLOR_CORP))
    radar.update_layout(polar=dict(radialaxis=dict(range=[0,100])), showlegend=False)
    st.plotly_chart(radar, use_container_width=True)

# 2. Detalle
with tabs[1]:
    st.subheader("Detalle de Evaluaciones")
    st.dataframe(df, height=500, use_container_width=True)

# 3. Tópicos
with tabs[2]:
    st.subheader("Frecuencia por Ítem")
    df_items = df['Ítem'].value_counts().rename_axis('Ítem').reset_index(name='Conteo')
    bar = px.bar(df_items, x='Ítem', y='Conteo', text='Conteo', color_discrete_sequence=[COLOR_CORP])
    st.plotly_chart(bar, use_container_width=True)
    st.subheader("Nube de Palabras")
    text = " ".join(df['Ítem'])
    wc = WordCloud(width=800, height=300, background_color='white').generate(text)
    fig, ax = plt.subplots(figsize=(12,4))
    ax.imshow(wc.recolor(color_func=lambda *args,**kw:COLOR_CORP), interpolation='bilinear'); ax.axis('off')
    st.pyplot(fig)

# 4. Insights
with tabs[3]:
    st.subheader("Top 5 Ítems")
    st.table(item_comp.nlargest(5,'Cumplimiento (%)'))
    st.table(item_comp.nsmallest(5,'Cumplimiento (%)'))

# 5. Heatmap
with tabs[4]:
    st.subheader("Heatmap de Cumplimiento")
    mapping={"Sí":1,"No aplica":0,"No":-1}
    df_h = df.copy(); df_h['Value'] = df_h['Respuestas'].map(mapping)
    heat = df_h.pivot(index='Ítem',columns='Llamada',values='Value')
    fig_heat = px.imshow(
        heat, labels={'x':'Llamada','y':'Ítem','color':'Valor'},
        color_continuous_scale=["lightcoral","lightgray",COLOR_CORP], aspect='auto'
    )
    st.plotly_chart(fig_heat, use_container_width=True)

# 6. Sentimiento
with tabs[5]:
    st.subheader("Sentimiento Cliente vs Asesor")
    df_melt = pd.melt(df, value_vars=['Sentimiento Cliente','Sentimiento Asesor'], var_name='Rol', value_name='Sentimiento')
    df_melt['Rol'] = df_melt['Rol'].map({'Sentimiento Cliente':'Cliente','Sentimiento Asesor':'Asesor'})
    counts = df_melt.groupby(['Sentimiento','Rol']).size().reset_index(name='Conteo')
    # Gráfico actual
    fig_bar = px.bar(
        counts, x='Sentimiento', y='Conteo', color='Rol', barmode='group',
        color_discrete_map={'Cliente':COLOR_CORP,'Asesor':COLOR_SEC},
        text='Conteo', title='Distribución de Sentimientos'
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # Opciones de correlación sugeridas:
    st.markdown("**Gráficos de correlación sugeridos:**")
    with st.expander("1. Scatter con regresión"):
        # Mapear a valores
        mapping = {"Negativo +":-2, "Negativo -":-1, "Neutral +":0, "Neutral -":1, "Positivo -":2, "Positivo +":3}
        df_plot = df.assign(
            SentCli = df['Sentimiento Cliente'].map(mapping),
            SentAs  = df['Sentimiento Asesor'].map(mapping))
        fig = px.scatter(df_plot, x='SentCli', y='SentAs', trendline='ols',
                         labels={'SentCli':'Cliente','SentAs':'Asesor'},
                         title='Scatter Cliente vs Asesor con L. Tendencia')
        st.plotly_chart(fig, use_container_width=True)
    with st.expander("2. Heatmap de co-ocurrencias"):
        df_heat2 = df_plot.groupby(['Sentimiento Cliente','Sentimiento Asesor']).size().reset_index(name='Count')
        heat2 = df_heat2.pivot(index='Sentimiento Cliente', columns='Sentimiento Asesor', values='Count')
        fig2 = px.imshow(heat2, color_continuous_scale='Blues', title='Co-ocurrencias')
        st.plotly_chart(fig2, use_container_width=True)
    with st.expander("3. Parallel Coordinates"):
        fig3 = px.parallel_coordinates(
            df_plot, dimensions=['SentCli','SentAs'], color='SentCli',
            color_continuous_scale=px.colors.sequential.Viridis,
            labels={'SentCli':'Cliente','SentAs':'Asesor'}
        )
        st.plotly_chart(fig3, use_container_width=True)
    with st.expander("4. Sankey Diagram"):
        # Preparar nodos y enlaces
        labels = list(mapping.keys())
        src_tgt = df_plot.groupby(['Sentimiento Cliente','Sentimiento Asesor']).size().reset_index(name='Count')
        label_idx = {lab:i for i,lab in enumerate(labels)}
        link = dict(
            source = src_tgt['Sentimiento Cliente'].map(label_idx),
            target = src_tgt['Sentimiento Asesor'].map(label_idx),
            value  = src_tgt['Count']
        )
        sankey = go.Figure(go.Sankey(node=dict(label=labels, color=COLOR_CORP),
                                     link=link))
        st.plotly_chart(sankey, use_container_width=True)
    with st.expander("5. Joint Distribution"):
        fig5 = px.scatter(df_plot, x='SentCli', y='SentAs', marginal_x='histogram', marginal_y='histogram',
                          labels={'SentCli':'Cliente','SentAs':'Asesor'},
                          title='Distribución Conjunta con Histogramas')
        st.plotly_chart(fig5, use_container_width=True)
