
import streamlit as st
import pandas as pd

@st.cache_data
def cargar_datos():
    df_pvp = pd.read_excel("catalogo_productos.xlsx", sheet_name="PVP Simples")
    df_detalle = pd.read_excel("catalogo_productos.xlsx", sheet_name="Tienda 281 Compuestos")
    return df_pvp, df_detalle

df_pvp, df_detalle = cargar_datos()

if "carrito" not in st.session_state:
    st.session_state["carrito"] = []

# Paso 1: Selección de producto
st.title("🧾 Simulador de Pedidos")
st.subheader("1️⃣ Selecciona un producto")

busqueda = st.text_input("Buscar por nombre o código")

productos = df_pvp[df_pvp["Estado.1"] == "Activo 281"].copy()
if busqueda:
    productos = productos[
        productos["PRODUCT"].str.contains(busqueda, case=False, na=False) |
        productos["PRODUCT ID"].astype(str).str.contains(busqueda)
    ]

producto_seleccionado = st.selectbox(
    "Elige un producto del catálogo",
    productos["PRODUCT"].unique()
)

if producto_seleccionado:
    # Paso 2: Personalización
    st.subheader("2️⃣ Personaliza tu producto")

    prod_data = productos[productos["PRODUCT"] == producto_seleccionado].iloc[0]
    cod_producto = prod_data["PRODUCT ID"]
    precio_base = prod_data["DELIVERY PVP 281"]
    size = prod_data["SIZE"] if pd.notna(prod_data["SIZE"]) else "Tamaño único"

    st.markdown(f"**Código:** {cod_producto}")
    st.markdown(f"**Precio base:** ${precio_base}")
    st.markdown(f"**Tamaño:** {size}")

    # Ingredientes por defecto
    ingredientes_defecto = df_detalle[
        (df_detalle["Clv. producto Compuesto"] == cod_producto) &
        (df_detalle["Producto simple"].notna())
    ]["Producto simple"].dropna().unique()

    if len(ingredientes_defecto):
        st.markdown("**Ingredientes por defecto:**")
        for i in ingredientes_defecto:
            st.markdown(f"- {i}")
    else:
        st.info("Este producto no tiene ingredientes configurables.")

    # Paso 3: Confirmación
    st.subheader("3️⃣ Confirmación")
    cantidad = st.number_input("Cantidad", min_value=1, max_value=20, value=1)
    if st.button("➕ Añadir al carrito"):
        item = {
            "codigo": cod_producto,
            "nombre": producto_seleccionado,
            "tamaño": size,
            "precio": precio_base,
            "cantidad": cantidad
        }
        st.session_state["carrito"].append(item)
        st.success(f"{cantidad} x {producto_seleccionado} añadido al carrito")

# Paso 4: Carrito
st.sidebar.subheader("🛒 Carrito")
if st.session_state["carrito"]:
    total = 0
    for item in st.session_state["carrito"]:
        subtotal = item["precio"] * item["cantidad"]
        total += subtotal
        texto = f"{item['cantidad']} x {item['codigo']} - {item['nombre']} ({item['tamaño']}) = ${subtotal:.2f}"
        st.sidebar.markdown(texto)
    st.sidebar.markdown(f"**Total: ${total:.2f}**")
    if st.sidebar.button("🧹 Vaciar carrito"):
        st.session_state["carrito"] = []
        st.experimental_rerun()
else:
    st.sidebar.info("Tu carrito está vacío.")
