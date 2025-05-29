import streamlit as st

# 1) ¡Esta tiene que ser la PRIMERA llamada a Streamlit!
st.set_page_config(page_title="Conejito Kawaii Salta Chupes", layout="wide")

# 2) Ahora ya podemos inyectar GA sin problemas
def inject_ga(measurement_id: str):
    st.markdown(
        f"""
        <!-- Global site tag (gtag.js) - Google Analytics -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=G-2F5LTZX5R4"></script>
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){{dataLayer.push(arguments);}}
          gtag('js', new Date());
          gtag('config','G-2F5LTZX5R4');
        </script>
        """,
        unsafe_allow_html=True,
    )

inject_ga("G-2F5LTZX5R4")

# 3) Resto de tu app
with open("KawaiiJumpingBunnyGame.html", "r", encoding="utf-8") as f:
    html_code = f.read()

st.title("🐰 Conejito 🌈 Kawaii Salta 🍭 Chupes ")
st.markdown("Disfruta y no comas muchas chupes 🍭 🐰 🍪.")

st.components.v1.html(html_code, height=380, scrolling=False)
