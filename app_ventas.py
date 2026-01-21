import streamlit as st
import pandas as pd
import os
from datetime import datetime
import io

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Gestión de Ventas Uniformes", layout="wide")
ARCHIVO_DB = 'base_datos_ventas.xlsx'

# --- FUNCIONES DE BASE DE DATOS ---
def cargar_datos():
    if os.path.exists(ARCHIVO_DB):
        try:
            return pd.read_excel(ARCHIVO_DB)
        except:
            return pd.DataFrame()
    else:
        return pd.DataFrame()

def guardar_venta(nueva_venta):
    df = cargar_datos()
    df_nuevo = pd.DataFrame([nueva_venta])
    df_final = pd.concat([df, df_nuevo], ignore_index=True)
    df_final.to_excel(ARCHIVO_DB, index=False)

def actualizar_db(df):
    df.to_excel(ARCHIVO_DB, index=False)

# --- INICIALIZACIÓN DE ESTADO (CARRITO) ---
if 'carrito_ninos' not in st.session_state:
    st.session_state.carrito_ninos = []
if 'carrito_ninas' not in st.session_state:
    st.session_state.carrito_ninas = []

# --- BARRA LATERAL: CONFIGURACIÓN Y DESCARGA ---
st.sidebar.header("⚙️ Configuración")

# BOTÓN DE DESCARGA
st.sidebar.markdown("### 📥 Respaldo de Datos")
if os.path.exists(ARCHIVO_DB):
    with open(ARCHIVO_DB, "rb") as f:
        bytes_data = f.read()
    
    st.sidebar.download_button(
        label="Descargar Excel al Dispositivo",
        data=bytes_data,
        file_name=f"Ventas_Uniformes_{datetime.now().strftime('%Y-%m-%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        help="Haz clic para guardar una copia de las ventas en tu celular o PC"
    )
else:
    st.sidebar.warning("Aún no hay ventas para descargar.")

st.sidebar.markdown("---")
st.sidebar.header("💰 Configuración de Precios")
st.sidebar.info("Modificar precios no afecta ventas ya guardadas.")

tallas = ["4", "6", "8", "10", "12", "14", "16", "S", "M", "L", "XL"]

# PRECIOS NIÑO
st.sidebar.markdown("#### 👦 Precios Camisas NIÑO")
precios_camisas_nino = {}
for talla in tallas:
    precios_camisas_nino[talla] = st.sidebar.number_input(f"Costo Camisa Niño Talla {talla}", value=30000, step=1000, key=f"p_nino_{talla}")

st.sidebar.markdown("#### 👖 Precio Pantalón NIÑO")
costo_pantalon = st.sidebar.number_input("Costo Pantalón (Valor único)", value=45000, step=1000)

st.sidebar.markdown("---")

# PRECIOS NIÑA
st.sidebar.markdown("#### 👧 Precios Camisas NIÑA")
precios_camisas_nina = {}
for talla in tallas:
    precios_camisas_nina[talla] = st.sidebar.number_input(f"Costo Camisa Niña Talla {talla}", value=30000, step=1000, key=f"p_nina_{talla}")


# --- INTERFAZ PRINCIPAL ---
st.title("👕 Sistema de Ventas - Uniformes NCP")

menu = st.radio("Seleccione una opción:", ["Nueva Venta", "Buscar / Editar Ventas"])

# ==========================================
# SECCIÓN 1: NUEVA VENTA
# ==========================================
if menu == "Nueva Venta":
    st.subheader("Datos del Cliente")
    col1, col2 = st.columns(2)
    with col1:
        nombre_cliente = st.text_input("Nombre Cliente")
        celular = st.text_input("Celular")
    with col2:
        descripcion = st.text_area("Descripción")
        colegio = st.text_input("Colegio", value="NCP (Predeterminado)", disabled=True)

    st.markdown("---")
    
    # --- ÁREA DE AGREGAR PRODUCTOS ---
    col_add1, col_add2 = st.columns(2)
    
    with col_add1:
        st.markdown("### 👦 Adicionar Niño")
        with st.expander("Detalles Niño"):
            nombre_alumno_m = st.text_input("Nombre Alumno (Niño)")
            talla_camisa_m = st.selectbox("Talla Camisa Niño", tallas, key="t_nino")
            cant_camisa_m = st.number_input("Cant. Camisa Niño", min_value=0, value=0, key="c_nino")
            
            st.markdown("**Medidas Pantalón:**")
            cintura = st.number_input("Cintura", key="cin")
            cadera = st.number_input("Cadera", key="cad")
            pierna = st.number_input("Contorno Pierna", key="pier")
            cant_pantalon = st.number_input("Cant. Pantalón", min_value=0, value=0, key="cp_nino")
            
            entrega_tela = st.radio("¿Entrega tela?", ("No", "Si"), key="tela_opt")
            metros_tela = 0.0
            if entrega_tela == "Si":
                metros_tela = st.number_input("Metros de tela", min_value=0.0, step=0.1)
            
            if st.button("➕ Agregar Niño al Pedido"):
                # CÁLCULO CON PRECIOS DE NIÑO
                precio_camisa = precios_camisas_nino[talla_camisa_m]
                subtotal = (cant_camisa_m * precio_camisa) + (cant_pantalon * costo_pantalon)
                
                item = {
                    "Tipo": "Niño",
                    "Nombre Alumno": nombre_alumno_m,
                    "Camisas": cant_camisa_m,
                    "Talla Camisa": talla_camisa_m,
                    "Precio Unit. Camisa": precio_camisa,
                    "Pantalones": cant_pantalon,
                    "Medidas": f"Cin:{cintura}, Cad:{cadera}, Pier:{pierna}",
                    "Entrega Tela": entrega_tela,
                    "Metros Tela": metros_tela,
                    "Subtotal": subtotal
                }
                st.session_state.carrito_ninos.append(item)
                st.success(f"Niño agregado. (Camisa T{talla_camisa_m}: ${precio_camisa:,.0f})")

    with col_add2:
        st.markdown("### 👧 Adicionar Niña")
        with st.expander("Detalles Niña"):
            nombre_alumno_f = st.text_input("Nombre Alumna (Niña)")
            talla_camisa_f = st.selectbox("Talla Camisa Niña", tallas, key="t_nina")
            cant_camisa_f = st.number_input("Cant. Camisa Niña", min_value=0, value=0, key="c_nina")
            
            if st.button("➕ Agregar Niña al Pedido"):
                # CÁLCULO CON PRECIOS DE NIÑA
                precio_camisa = precios_camisas_nina[talla_camisa_f]
                subtotal = (cant_camisa_f * precio_camisa)
                
                item = {
                    "Tipo": "Niña",
                    "Nombre Alumno": nombre_alumno_f,
                    "Camisas": cant_camisa_f,
                    "Talla Camisa": talla_camisa_f,
                    "Precio Unit. Camisa": precio_camisa,
                    "Subtotal": subtotal
                }
                st.session_state.carrito_ninas.append(item)
                st.success(f"Niña agregada. (Camisa T{talla_camisa_f}: ${precio_camisa:,.0f})")

    # --- RESUMEN Y TOTALES ---
    st.markdown("---")
    st.subheader("🧾 Resumen del Pedido")
    
    total_nino = sum(item['Subtotal'] for item in st.session_state.carrito_ninos)
    total_nina = sum(item['Subtotal'] for item in st.session_state.carrito_ninas)
    gran_total = total_nino + total_nina

    if st.session_state.carrito_ninos:
        st.write("##### Detalle Niños:")
        st.table(pd.DataFrame(st.session_state.carrito_ninos))
        st.write(f"**Sub-Total Niño:** ${total_nino:,.0f}")

    if st.session_state.carrito_ninas:
        st.write("##### Detalle Niñas:")
        st.table(pd.DataFrame(st.session_state.carrito_ninas))
        st.write(f"**Sub-Total Niña:** ${total_nina:,.0f}")

    st.markdown(f"## Total General: ${gran_total:,.0f}")

    # --- PAGO Y CIERRE ---
    st.markdown("### Registro de Pago")
    valor_recibido = st.number_input("Valor Recibido", min_value=0, step=1000)
    tipo_pago = st.selectbox("Tipo de Pago", ["Efectivo", "Transferencia"])

    estado_pago = "Pendiente"
    if valor_recibido > 0:
        if valor_recibido < gran_total:
            estado_pago = "Abono"
            st.warning(f"Estado: ABONO. Restan: ${gran_total - valor_recibido:,.0f}")
        elif valor_recibido == gran_total:
            estado_pago = "Pago Total"
            st.success("Estado: PAGO TOTAL")
        else:
            st.error("El valor recibido supera el total.")
    
    if st.button("💾 CONFIRMAR Y CERRAR VENTA"):
        if not nombre_cliente:
            st.error("Falta el nombre del cliente")
        elif gran_total == 0:
            st.error("El carrito está vacío")
        else:
            id_venta = datetime.now().strftime("%Y%m%d%H%M%S")
            nueva_venta = {
                "ID": id_venta,
                "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Cliente": nombre_cliente,
                "Celular": celular,
                "Descripción": descripcion,
                "Detalle Niños": str(st.session_state.carrito_ninos),
                "Detalle Niñas": str(st.session_state.carrito_ninas),
                "Total General": gran_total,
                "Pagado": valor_recibido,
                "Saldo Pendiente": gran_total - valor_recibido,
                "Estado Pago": estado_pago,
                "Medio Pago": tipo_pago,
                "Entrega Tela Pendiente": "Si" if any(x.get('Entrega Tela') == 'No' for x in st.session_state.carrito_ninos) else "No"
            }
            guardar_venta(nueva_venta)
            st.session_state.carrito_ninos = []
            st.session_state.carrito_ninas = []
            st.balloons()
            st.success("Venta registrada correctamente. Puede descargar la base de datos actualizada en el menú lateral.")
            st.rerun()

# ==========================================
# SECCIÓN 2: BUSCAR Y EDITAR
# ==========================================
elif menu == "Buscar / Editar Ventas":
    st.header("Base de Datos de Ventas")
    df = cargar_datos()
    
    if not df.empty:
        filtro = st.text_input("🔍 Buscar por Nombre de Cliente o ID")
        
        if filtro:
            df = df[df['Cliente'].astype(str).str.contains(filtro, case=False) | df['ID'].astype(str).str.contains(filtro)]
        
        st.dataframe(df.style.apply(lambda x: ['background-color: #ffcccc' if (x['Saldo Pendiente'] > 0 or x['Entrega Tela Pendiente'] == 'Si') else 'background-color: #ccffcc' for i in x], axis=1))
        
        st.markdown("---")
        st.subheader("Editar Venta Existente")
        id_editar = st.selectbox("Seleccione ID de venta para editar:", df['ID'].unique())
        
        if id_editar:
            idx = df[df['ID'] == id_editar].index[0]
            venta_act = df.loc[idx]
            
            st.write(f"Cliente: **{venta_act['Cliente']}** | Total: ${venta_act['Total General']:,.0f}")
            
            col_e1, col_e2 = st.columns(2)
            
            with col_e1:
                st.markdown("#### Actualizar Pagos")
                nuevo_pago = st.number_input("Nuevo valor total pagado (acumulado)", value=float(venta_act['Pagado']))
                if st.button("Actualizar Pago"):
                    df.at[idx, 'Pagado'] = nuevo_pago
                    saldo = venta_act['Total General'] - nuevo_pago
                    df.at[idx, 'Saldo Pendiente'] = saldo
                    if saldo <= 0:
                        df.at[idx, 'Estado Pago'] = "Pago Total"
                    else:
                        df.at[idx, 'Estado Pago'] = "Abono"
                    actualizar_db(df)
                    st.success("Pago actualizado")
                    st.rerun()

            with col_e2:
                st.markdown("#### Entrega de Tela")
                st.info(f"Estado actual tela pendiente: {venta_act.get('Entrega Tela Pendiente', 'N/A')}")
                if st.button("Marcar Tela como ENTREGADA"):
                    df.at[idx, 'Entrega Tela Pendiente'] = "No"
                    actualizar_db(df)
                    st.success("Estado de tela actualizado")
                    st.rerun()
            
    else:
        st.warning("No hay ventas registradas aún.")