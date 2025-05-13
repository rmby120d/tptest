
import streamlit as st
import pandas as pd

# Cargar datos
@st.cache_data
def cargar_datos():
    file = "catalogo_productos.xlsx"
    pvp_simples = pd.read_excel(file, sheet_name="PVP Simples")
    activos = pvp_simples[pvp_simples["Estado.1"] == "Activo 281"]
    return activos

productos = cargar_datos()

# Inicializar carrito en session_state
if "carrito" not in st.session_state:
    st.session_state["carrito"] = []

# Título
st.title("Calculadora de Pedidos - Pizzería")

# Selector de categoría
categoria = st.selectbox("Selecciona la categoría", productos["SECONDARY GROUP"].unique())

# Filtrar productos por categoría
productos_categoria = productos[productos["SECONDARY GROUP"] == categoria]

# Detectar nombre y código correcto del producto
columna_producto = [c for c in productos.columns if "PRODUCT" in c.upper() and "NAME" not in c.upper()][0]
columna_codigo = "PRODUCT ID" if "PRODUCT ID" in productos.columns else productos.columns[0]  # fallback

# Mostrar lista de productos con botón de agregar
st.subheader("Productos disponibles")
for _, fila in productos_categoria.iterrows():
    nombre = fila[columna_producto]
    codigo = fila[columna_codigo]
    precio = fila["DELIVERY PVP 281"]
    size = fila["SIZE"] if pd.notna(fila["SIZE"]) else "Tamaño único"
    key = f"{codigo}_{size}"

    cols = st.columns([4, 1, 1])
    with cols[0]:
        st.write(f"**{codigo} - {nombre} ({size})**")
    with cols[1]:
        cantidad = st.number_input(f"Cantidad", min_value=1, max_value=20, value=1, key=key+"_qty")
    with cols[2]:
        if st.button("Agregar", key=key+"_btn"):
            st.session_state["carrito"].append({
                "codigo": codigo,
                "nombre": nombre,
                "tamaño": size,
                "precio": precio,
                "cantidad": cantidad
            })
            st.success(f"Agregado: {cantidad} x {nombre} ({size})")

# Mostrar resumen del carrito
if st.session_state["carrito"]:
    st.subheader("🛒 Carrito de Compras")
    total = 0
    for idx, item in enumerate(st.session_state["carrito"]):
        subtotal = item["precio"] * item["cantidad"]
        total += subtotal
        st.write(f"{item['cantidad']} x {item['codigo']} - {item['nombre']} ({item['tamaño']}) = $ {subtotal:.2f}")
    st.markdown(f"### Total: $ {total:.2f}")

    if st.button("🧹 Vaciar carrito"):
        st.session_state["carrito"] = []
        st.experimental_rerun()
else:
    st.info("Tu carrito está vacío. Agrega productos para comenzar.")
