
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Variables de color
COLOR_CORP = "#6d84e3"
COLOR_SEC = "#555555"

# Inyectar CSS para estilo y branding
st.markdown(f"""<style>
/* Fuentes y espaciado */
body {{ font-family: 'Segoe UI', sans-serif; background-color: #f8f9fa; }}
.reportview-container .main {{ padding: 1rem 2rem 2rem; }}
/* Header fijo */
.header {{ position: fixed; top: 0; width: 100%; background-color: {COLOR_CORP}; color: white; padding: 0.75rem 1rem; z-index: 1000; display: flex; align-items: center; }}
.header img {{ height: 40px; }}
.header h1 {{ margin: 0 0 0 1rem; font-size: 1.5rem; }}
.content {{ margin-top: 70px; }}
/* Sidebar */
[data-testid="stSidebar"] {{ background-color: #ffffff; }}
.sidebar .sidebar-content {{ padding: 1rem; font-size: 0.9rem; }}
/* Cards */
.card {{ background-color: white; border-radius: 10px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); padding: 1.5rem; margin-bottom: 1.5rem; opacity: 0; animation: fade-in 0.6s ease-in forwards; }}
@keyframes fade-in {{ to {{ opacity: 1; }} }}
/* Titulares */
h2, h3 {{ color: {COLOR_CORP}; }}
/* Responsive */
@media (max-width: 768px) {{ .card {{ padding: 1rem; }} h1 {{ font-size: 1.2rem; }} }}
</style>""", unsafe_allow_html=True)

# Header con logo
st.markdown(f"""<div class="header">
    <img src="logo.png" alt="Logo">
    <h1>Dashboard Calidad de Llamadas</h1>
</div>""", unsafe_allow_html=True)

st.markdown('<div class="content">', unsafe_allow_html=True)

# Sidebar para navegación
st.sidebar.title("Navegación")
section = st.sidebar.radio("", ["Visión General","Detalle","Tópicos","Insights","Heatmap","Sentimiento"])

# Carga de datos
uploaded_file = st.sidebar.file_uploader("Sube el CSV con sentimiento", type=["csv"])
if not uploaded_file:
    st.sidebar.warning("Sube el CSV para iniciar análisis")
    st.stop()
df = pd.read_csv(uploaded_file)
df['Llamada'] = df['Llamada'].astype(str)

# Cálculos comunes
pct_si = (df['Respuestas']=="Sí").mean()*100
pct_no = (df['Respuestas']=="No").mean()*100
pct_na = (df['Respuestas']=="No aplica").mean()*100
block_comp = df.groupby('Bloque').apply(lambda x: (x['Respuestas']=="Sí").mean()*100).reset_index(name='Cumplimiento (%)')
item_comp  = df.groupby('Ítem').apply(lambda x: (x['Respuestas']=="Sí").mean()*100).reset_index(name='Cumplimiento (%)')

# Funciones de sección
def show_overview():
    st.subheader("KPIs Principales")
    st.markdown('<div class="card">', unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3)
    c1.metric("Tasa Sí", f"{pct_si:.1f}%")
    c2.metric("Tasa No", f"{pct_no:.1f}%")
    c3.metric("Tasa No aplica", f"{pct_na:.1f}%")
    st.markdown('</div>', unsafe_allow_html=True)

    # Gráficos destacados
    st.subheader("Gráficos Destacados")
    st.markdown('<div class="card">', unsafe_allow_html=True)
    # Gauge
    gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=pct_si,
        title={'text': "Cumplimiento Global (%)"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': COLOR_CORP},
            'steps': [
                {'range': [0, 60], 'color': "lightcoral"},
                {'range': [60, 80], 'color': "gold"},
                {'range': [80, 100], 'color': "lightgreen"}
            ]
        }
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
    st.markdown('</div>', unsafe_allow_html=True)

def show_detail():
    st.subheader("Detalle de Evaluaciones")
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.dataframe(df, height=500)
    st.markdown('</div>', unsafe_allow_html=True)

def show_topics():
    st.subheader("Frecuencia por Ítem")
    st.markdown('<div class="card">', unsafe_allow_html=True)
    df_items = df['Ítem'].value_counts().rename_axis('Ítem').reset_index(name='Conteo')
    bar = px.bar(df_items, x='Ítem', y='Conteo', text='Conteo', color_discrete_sequence=[COLOR_CORP])
    st.plotly_chart(bar, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.subheader("Nube de Palabras")
    st.markdown('<div class="card">', unsafe_allow_html=True)
    text = " ".join(df['Ítem'])
    wc = WordCloud(width=800, height=300, background_color='white').generate(text)
    fig, ax = plt.subplots(figsize=(12,4))
    ax.imshow(wc.recolor(color_func=lambda *args,**kwargs: COLOR_CORP), interpolation='bilinear')
    ax.axis('off')
    st.pyplot(fig)
    st.markdown('</div>', unsafe_allow_html=True)

def show_insights():
    st.subheader("Insights")
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.table(item_comp.nlargest(5,'Cumplimiento (%)'))
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.table(item_comp.nsmallest(5,'Cumplimiento (%)'))
    st.markdown('</div>', unsafe_allow_html=True)

    # Pareto de fallos
    st.markdown('<div class="card">', unsafe_allow_html=True)
    df_no = df[df['Respuestas']=="No"]
    cnt = df_no['Ítem'].value_counts().reset_index()
    cnt.columns = ['Ítem','Fails']
    cnt = cnt.sort_values('Fails',ascending=False)
    cnt['CumPct'] = cnt['Fails'].cumsum()/cnt['Fails'].sum()*100
    pareto = go.Figure()
    pareto.add_trace(go.Bar(x=cnt['Ítem'], y=cnt['Fails'], name='Fallos', marker_color=COLOR_CORP))
    pareto.add_trace(go.Scatter(x=cnt['Ítem'], y=cnt['CumPct'], name='Acum (%)', yaxis='y2', line_color=COLOR_CORP))
    pareto.update_layout(yaxis=dict(title='Fallos'),
                         yaxis2=dict(title='Acum (%)', overlaying='y', side='right', range=[0,100]),
                         xaxis_tickangle=-45, plot_bgcolor='white')
    st.plotly_chart(pareto, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

def show_heatmap():
    st.subheader("Heatmap de Cumplimiento")
    st.markdown('<div class="card">', unsafe_allow_html=True)
    mapping={"Sí":1,"No aplica":0,"No":-1}
    df_h = df.copy(); df_h['Value'] = df_h['Respuestas'].map(mapping)
    heat = df_h.pivot(index='Ítem', columns='Llamada', values='Value')
    hfig = px.imshow(heat, labels={'x':'Llamada','y':'Ítem','color':'Valor'},
                     color_continuous_scale=["lightcoral","lightgray",COLOR_CORP], aspect='auto')
    st.plotly_chart(hfig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

def show_sentiment():
    st.subheader("Sentimiento Cliente vs Asesor")
    st.markdown('<div class="card">', unsafe_allow_html=True)
    df_m = pd.melt(df, value_vars=['Sentimiento Cliente','Sentimiento Asesor'], var_name='Rol', value_name='Sentimiento')
    df_m['Rol'] = df_m['Rol'].map({'Sentimiento Cliente':'Cliente','Sentimiento Asesor':'Asesor'})
    counts = df_m.groupby(['Sentimiento','Rol']).size().reset_index(name='Conteo')
    fig = px.bar(counts, x='Sentimiento', y='Conteo', color='Rol', barmode='group',
                 color_discrete_map={'Cliente':COLOR_CORP,'Asesor':COLOR_SEC}, text='Conteo')
    fig.update_layout(xaxis_tickangle=-45, plot_bgcolor='white')
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Renderizar sección
if section == "Visión General":
    show_overview()
elif section == "Detalle":
    show_detail()
elif section == "Tópicos":
    show_topics()
elif section == "Insights":
    show_insights()
elif section == "Heatmap":
    show_heatmap()
elif section == "Sentimiento":
    show_sentiment()

st.markdown('</div>', unsafe_allow_html=True)
