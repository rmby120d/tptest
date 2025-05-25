import streamlit as st

# Leer el archivo HTML del juego
with open("kids_jumping_game.html", "r", encoding="utf-8") as f:
    html_code = f.read()

st.set_page_config(
    page_title="Kawaii Jump ♡",
    layout="wide",
)

st.title("Kawaii Jump ♡")
st.markdown("#### Un juego saltarín kawaii para todos 🚀✨")

# Insertar el HTML como un componente Streamlit
st.components.v1.html(html_code, height=600, scrolling=False)
