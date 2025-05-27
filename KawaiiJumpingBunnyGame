import streamlit as st

# Leer el HTML de tu juego
with open("KawaiiJumpingBunnyGame.html", "r", encoding="utf-8") as f:
    html_code = f.read()

st.set_page_config(page_title="Conejito Kawaii Salta Dulces", layout="wide")

st.title("🐰 Conejito Kawaii Salta Dulces")
st.markdown(
    "Presiona **ESPACIO** o toca para saltar. ¡Evita los caramelos! Usa la flecha → para correr más rápido."
)

# Incrusta el HTML con JS (el juego se juega en la web, no en Python)
st.components.v1.html(html_code, height=380, scrolling=False)
