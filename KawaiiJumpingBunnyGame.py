import streamlit as st

# ————————————————————————————————————————————————————————————
# 1) Función para inyectar Google Analytics vía st.markdown
# ————————————————————————————————————————————————————————————
def inject_ga(measurement_id: str):
    st.markdown(
        f"""
        <!-- Global site tag (gtag.js) - Google Analytics -->
        <script async src="https://www.googletagmanager.com/gtag/js?id={measurement_id}"></script>
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){{dataLayer.push(arguments);}}
          gtag('js', new Date());
          gtag('config','{measurement_id}');
        </script>
        """,
        unsafe_allow_html=True,
    )

# 2) Aquí pones tu ID de GA4
inject_ga("G-2F5LTZX5R4")

# ————————————————————————————————————————————————————————————
# 3) Tu código original de Streamlit
# ————————————————————————————————————————————————————————————
# Leer el HTML de tu juego
with open("KawaiiJumpingBunnyGame.html", "r", encoding="utf-8") as f:
    html_code = f.read()

st.set_page_config(page_title="Conejito Kawaii Salta Chupes", layout="wide")

st.title("🐰 Conejito 🌈 Kawaii Salta 🍭 Chupes ")
st.markdown(
    "Disfruta y no comas muchas chupes 🍭 🐰 🍪."
)

# Incrusta el HTML con JS (el juego se juega en la web, no en Python)
st.components.v1.html(html_code, height=380, scrolling=False)
