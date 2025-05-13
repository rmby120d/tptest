
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

st.title("Simulador de Pedidos")
st.subheader("1. Selecciona un producto")

# Filtro por categoría completa
df_pvp["PRODUCTO_TAM"] = df_pvp["PRODUCT"] + " (" + df_pvp["SIZE"].fillna("Tamaño único") + ")"
categoria = st.selectbox("Filtrar por categoría", ["Todo"] + sorted(df_pvp["SECONDARY GROUP"].dropna().unique()))
productos = df_pvp.copy()
if categoria != "Todo":
    productos = productos[productos["SECONDARY GROUP"] == categoria]

# Búsqueda
busqueda = st.text_input("Buscar por nombre o código")
if busqueda:
    productos = productos[
        productos["PRODUCTO_TAM"].str.contains(busqueda, case=False, na=False) |
        productos["PRODUCT ID"].astype(str).str.contains(busqueda)
    ]

# Desplegable
producto_seleccionado = st.selectbox("Elige un producto del catálogo", productos["PRODUCTO_TAM"].tolist())

if producto_seleccionado:
    st.subheader("2. Personaliza tu producto")

    # Mostrar ingredientes por defecto si existen
    ingredientes_defecto = df_detalle[
        df_detalle["Clv. producto Compuesto"] == cod_producto
    ][["Producto simple"]].dropna().drop_duplicates()

    if not ingredientes_defecto.empty:
        st.markdown("**Ingredientes por defecto:**")
        for _, row in ingredientes_defecto.iterrows():
            st.markdown(f"- {row['Producto simple']}")
    

    prod_data = productos[productos["PRODUCTO_TAM"] == producto_seleccionado].iloc[0]
    cod_producto = prod_data["PRODUCT ID"]
    nombre_producto = prod_data["PRODUCT"]
    size = prod_data["SIZE"] if pd.notna(prod_data["SIZE"]) else "Tamaño único"
    precio_base = float(prod_data["DELIVERY PVP 281"])

    st.markdown(f"**Código:** {cod_producto}")
    st.markdown(f"**Producto:** {nombre_producto}")
    st.markdown(f"**Tamaño:** {size}")
    st.markdown(f"**Precio base:** ${precio_base}")

    ingredientes_prod = df_detalle[df_detalle["Clv. producto Compuesto"] == cod_producto]
    ingredientes_disponibles = ingredientes_prod[["GRUPO MASAS", "Producto simple", "PVP"]].dropna()

    ingredientes_seleccionados = {}
    if not ingredientes_disponibles.empty:
        for grupo in ingredientes_disponibles["GRUPO MASAS"].dropna().unique():
            opciones = ingredientes_disponibles[ingredientes_disponibles["GRUPO MASAS"] == grupo]
            nombres = [f"{row['Producto simple']} (+${row['PVP']})" for _, row in opciones.iterrows()]
            ids = opciones["Producto simple"].tolist()
            seleccion = st.selectbox(f"{grupo}", options=nombres, key=grupo)
            index = nombres.index(seleccion)
            seleccion_real = ids[index]
            precio_extra = opciones.iloc[index]["PVP"]
            ingredientes_seleccionados[grupo] = {
                "nombre": seleccion_real,
                "precio": precio_extra
            }
    else:
        st.info("Este producto no tiene ingredientes configurables.")

    st.subheader("3. Confirmación")
    cantidad = st.number_input("Cantidad", min_value=1, max_value=20, value=1)

    if st.button("Añadir al carrito"):
        extras_total = sum([v["precio"] for v in ingredientes_seleccionados.values()])
        item = {
            "codigo": cod_producto,
            "nombre": nombre_producto,
            "tamaño": size,
            "precio": precio_base + extras_total,
            "cantidad": cantidad,
            "extras": ingredientes_seleccionados
        }
        st.session_state["carrito"].append(item)
        st.success(f"{cantidad} x {nombre_producto} añadido al carrito")

st.sidebar.subheader("Carrito")
if st.session_state["carrito"]:
    total = 0
    for item in st.session_state["carrito"]:
        subtotal = item["precio"] * item["cantidad"]
        total += subtotal
        texto = f"{item['cantidad']} x {item['codigo']} - {item['nombre']} ({item['tamaño']}) = ${subtotal:.2f}"
        if item["extras"]:
            for grupo, detalle in item["extras"].items():
                texto += f" | {grupo}: {detalle['nombre']} (+${detalle['precio']})"
        st.sidebar.markdown(texto)
    st.sidebar.markdown(f"**Total: ${total:.2f}**")
    if st.sidebar.button("Vaciar carrito"):
        st.session_state["carrito"] = []
        st.experimental_rerun()
else:
    st.sidebar.info("Tu carrito está vacío.")
