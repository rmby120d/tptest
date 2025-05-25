{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import streamlit as st\
\
# Leer el archivo HTML del juego\
with open("kids_jumping_game.html", "r", encoding="utf-8") as f:\
    html_code = f.read()\
\
st.set_page_config(\
    page_title="Kawaii Jump \uc0\u9825 ",\
    layout="wide",\
)\
\
st.title("Kawaii Jump \uc0\u9825 ")\
st.markdown("#### Un juego saltar\'edn kawaii para todos \uc0\u55357 \u56960 \u10024 ")\
\
# Insertar el HTML como un componente Streamlit\
st.components.v1.html(html_code, height=600, scrolling=False)}