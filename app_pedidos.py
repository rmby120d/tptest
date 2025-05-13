
import streamlit as st
import pandas as pd

# Cargar datos
@st.cache_data
def cargar_datos():
    file = "catalogo_productos.xlsx"
    return pd.read_excel(file, sheet_name="PVP Simples")

df = cargar_datos()

# Selección de tienda
st.sidebar.title("Configuración")
tienda = st.sidebar.radio("Selecciona la tienda", ["281", "394"])

# Filtrar productos activos según tienda
estado_col = "Estado.1" if tienda == "281" else "Estado"
precio_col = f"DELIVERY PVP {tienda}"
productos = df[df[estado_col] == f"Activo {tienda}"]

# Inicializar carrito en session_state
if "carrito" not in st.session_state:
    st.session_state["carrito"] = []

# Buscador por nombre o código
busqueda = st.text_input("Buscar producto por nombre o código")

# Selector de categoría
categoria = st.selectbox("Selecciona la categoría", productos["SECONDARY GROUP"].dropna().unique())
productos_categoria = productos[productos["SECONDARY GROUP"] == categoria]

# Aplicar filtro de búsqueda si hay texto
if busqueda:
    productos_categoria = productos_categoria[
        productos_categoria["PRODUCT"].str.contains(busqueda, case=False, na=False) |
        productos_categoria["PRODUCT ID"].astype(str).str.contains(busqueda)
    ]

# Mostrar productos
st.subheader("Productos disponibles")
for _, fila in productos_categoria.iterrows():
    codigo = fila["PRODUCT ID"]
    nombre = fila["PRODUCT"]
    precio = fila[precio_col]
    size = fila["SIZE"] if pd.notna(fila["SIZE"]) else "Tamaño único"
    key = f"{codigo}_{size}"

    cols = st.columns([4, 1, 1])
    with cols[0]:
        st.write(f"**{codigo} - {nombre} ({size})**")
    with cols[1]:
        cantidad = st.number_input("Cantidad", min_value=1, max_value=20, value=1, key=key+"_qty")
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

# Mostrar carrito en sidebar
with st.sidebar.expander("🛒 Ver Carrito", expanded=True):
    total = 0
    if st.session_state["carrito"]:
        for item in st.session_state["carrito"]:
            subtotal = item["precio"] * item["cantidad"]
            total += subtotal
            st.markdown(f"- {item['cantidad']} x {item['codigo']} - {item['nombre']} ({item['tamaño']}) = $ {subtotal:.2f}")
        st.markdown(f"**Total: $ {total:.2f}**")
        if st.button("🧹 Vaciar carrito"):
            st.session_state["carrito"] = []
            st.experimental_rerun()
    else:
        st.info("Tu carrito está vacío.")
