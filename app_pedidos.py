
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

# Título
st.title("Calculadora de Pedidos - Pizzería")

# Selector de categoría
categoria = st.selectbox("Selecciona la categoría", productos["SECONDARY GROUP"].unique())

# Filtrar productos por categoría
productos_categoria = productos[productos["SECONDARY GROUP"] == categoria]

# Mostrar lista de productos con checkbox
st.subheader("Productos disponibles")
carrito = []

# Detectar el nombre correcto de la columna de producto
columna_producto = [c for c in productos.columns if "PRODUCT" in c.upper() and "NAME" not in c.upper()][0]

for _, fila in productos_categoria.iterrows():
    nombre = fila[columna_producto]
    precio = fila["DELIVERY PVP 281"]
    size = fila["SIZE"] if pd.notna(fila["SIZE"]) else "Tamaño único"
    key = f"{nombre}_{size}"

    if st.checkbox(f"{nombre} ({size}) - $ {precio:.2f}", key=key):
        cantidad = st.number_input(f"Cantidad de {nombre} ({size})", min_value=1, max_value=20, value=1, key=key+"_qty")
        carrito.append({"nombre": nombre, "tamaño": size, "precio": precio, "cantidad": cantidad})

# Mostrar resumen del pedido
if carrito:
    st.subheader("Resumen del Pedido")
    total = 0
    for item in carrito:
        subtotal = item["precio"] * item["cantidad"]
        total += subtotal
        st.write(f"{item['cantidad']} x {item['nombre']} ({item['tamaño']}) = $ {subtotal:.2f}")

    st.markdown(f"### Total: $ {total:.2f}")
else:
    st.info("Selecciona productos para empezar tu pedido.")
