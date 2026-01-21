import streamlit as st
import pandas as pd
import os
from datetime import datetime

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

# --- INICIALIZACIÓN DE ESTADO ---
# Usaremos listas para almacenar los pedidos confirmados
if 'carrito_ninos' not in st.session_state:
    st.session_state.carrito_ninos = []
if 'carrito_ninas' not in st.session_state:
    st.session_state.carrito_ninas = []

# Contadores para saber cuántos formularios mostrar
if 'num_forms_ninos' not in st.session_state:
    st.session_state.num_forms_ninos = 1
if 'num_forms_ninas' not in st.session_state:
    st.session_state.num_forms_ninas = 1

# --- BARRA LATERAL: CONFIGURACIÓN Y DESCARGA ---
st.sidebar.header("⚙️ Configuración")

# BOTÓN DE DESCARGA
st.sidebar.markdown("### 📥 Respaldo de Datos")
if os.path.exists(ARCHIVO_DB):
    with open(ARCHIVO_DB, "rb") as f:
        bytes_data = f.read()
    st.sidebar.download_button(
        label="Descargar Excel",
        data=bytes_data,
        file_name=f"Ventas_Uniformes_{datetime.now().strftime('%Y-%m-%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

st.sidebar.markdown("---")
st.sidebar.header("💰 Precios")
st.sidebar.info("Modificar precios no afecta ventas ya guardadas.")

tallas = ["4", "6", "8", "10", "12", "14", "16", "S", "M", "L", "XL"]

st.sidebar.markdown("#### 👦 Precios Camisas NIÑO")
precios_camisas_nino = {}
for talla in tallas:
    precios_camisas_nino[talla] = st.sidebar.number_input(f"Costo Niño Talla {talla}", value=30000, step=1000, key=f"p_nino_{talla}")

st.sidebar.markdown("#### 👖 Precio Pantalón NIÑO")
costo_pantalon = st.sidebar.number_input("Costo Pantalón (Valor único)", value=45000, step=1000)

st.sidebar.markdown("---")
st.sidebar.markdown("#### 👧 Precios Camisas NIÑA")
precios_camisas_nina = {}
for talla in tallas:
    precios_camisas_nina[talla] = st.sidebar.number_input(f"Costo Niña Talla {talla}", value=30000, step=1000, key=f"p_nina_{talla}")


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
        # Cambio: Colegio editable pero con valor por defecto
        colegio = st.text_input("Colegio", value="NCP") 

    st.markdown("---")
    
    col_main_nino, col_main_nina = st.columns(2)
    
    # ------------------------------------------------
    # LÓGICA DE NIÑOS
    # ------------------------------------------------
    with col_main_nino:
        st.markdown("### 👦 Niño")
        
        # Bucle para mostrar formularios dinámicos
        for i in range(st.session_state.num_forms_ninos):
            with st.expander(f"Detalles Niño {i+1}", expanded=True):
                # Generamos claves únicas para cada widget usando 'i'
                nombre_alumno_m = st.text_input(f"Nombre Alumno", key=f"nom_nino_{i}")
                
                # 1. Cantidad Camisa primero
                cant_camisa_m = st.number_input("Cant. Camisa", min_value=0, value=0, key=f"cant_cam_nino_{i}")
                
                # Solo mostrar talla si cantidad > 0
                talla_camisa_m = "4" # Valor default
                if cant_camisa_m > 0:
                    talla_camisa_m = st.selectbox("Talla Camisa", tallas, key=f"talla_nino_{i}")
                
                st.markdown("---")
                
                # 2. Cantidad Pantalón primero
                cant_pantalon = st.number_input("Cant. Pantalón", min_value=0, value=0, key=f"cant_pant_nino_{i}")
                
                cintura, cadera, pierna = 0.0, 0.0, 0.0
                if cant_pantalon > 0:
                    st.caption("Medidas Pantalón:")
                    cintura = st.number_input("Cintura", key=f"cint_nino_{i}")
                    cadera = st.number_input("Cadera", key=f"cad_nino_{i}")
                    pierna = st.number_input("Pierna", key=f"pier_nino_{i}")

                # Botón de acción (Confirmar vs Actualizar)
                # Verificamos si este índice 'i' ya existe en el carrito guardado
                es_actualizacion = i < len(st.session_state.carrito_ninos)
                texto_boton = "🔄 Actualizar niño al pedido" if es_actualizacion else "✅ Confirmar niño al pedido"
                
                if st.button(texto_boton, key=f"btn_nino_{i}"):
                    precio_camisa = precios_camisas_nino[talla_camisa_m] if cant_camisa_m > 0 else 0
                    subtotal = (cant_camisa_m * precio_camisa) + (cant_pantalon * costo_pantalon)
                    
                    item_data = {
                        "ID_Temp": i, # Para rastrear formulario
                        "Tipo": "Niño",
                        "Nombre Alumno": nombre_alumno_m,
                        "Camisas": cant_camisa_m,
                        "Talla Camisa": talla_camisa_m if cant_camisa_m > 0 else "N/A",
                        "Pantalones": cant_pantalon,
                        "Medidas": f"Cin:{cintura}, Cad:{cadera}, Pier:{pierna}" if cant_pantalon > 0 else "N/A",
                        "Subtotal": subtotal
                    }
                    
                    if es_actualizacion:
                        st.session_state.carrito_ninos[i] = item_data
                        st.success(f"Niño {i+1} actualizado.")
                    else:
                        st.session_state.carrito_ninos.append(item_data)
                        st.success(f"Niño {i+1} confirmado.")

        # Botón afuera para agregar otro formulario de niño
        if st.button("➕ Adicionar otro Niño"):
            st.session_state.num_forms_ninos += 1
            st.rerun()

    # ------------------------------------------------
    # LÓGICA DE NIÑAS
    # ------------------------------------------------
    with col_main_nina:
        st.markdown("### 👧 Niña")
        
        for i in range(st.session_state.num_forms_ninas):
            with st.expander(f"Detalles Niña {i+1}", expanded=True):
                nombre_alumno_f = st.text_input(f"Nombre Alumna", key=f"nom_nina_{i}")
                
                # 1. Cantidad Camisa primero
                cant_camisa_f = st.number_input("Cant. Camisa", min_value=0, value=0, key=f"cant_cam_nina_{i}")
                
                talla_camisa_f = "4"
                if cant_camisa_f > 0:
                    talla_camisa_f = st.selectbox("Talla Camisa", tallas, key=f"talla_nina_{i}")
                
                # Botón Acción
                es_actualizacion_f = i < len(st.session_state.carrito_ninas)
                texto_boton_f = "🔄 Actualizar niña al pedido" if es_actualizacion_f else "✅ Confirmar niña al pedido"

                if st.button(texto_boton_f, key=f"btn_nina_{i}"):
                    precio_camisa = precios_camisas_nina[talla_camisa_f] if cant_camisa_f > 0 else 0
                    subtotal = (cant_camisa_f * precio_camisa)
                    
                    item_data = {
                        "ID_Temp": i,
                        "Tipo": "Niña",
                        "Nombre Alumno": nombre_alumno_f,
                        "Camisas": cant_camisa_f,
                        "Talla Camisa": talla_camisa_f if cant_camisa_f > 0 else "N/A",
                        "Subtotal": subtotal
                    }
                    
                    if es_actualizacion_f:
                        st.session_state.carrito_ninas[i] = item_data
                        st.success(f"Niña {i+1} actualizada.")
                    else:
                        st.session_state.carrito_ninas.append(item_data)
                        st.success(f"Niña {i+1} confirmada.")

        if st.button("➕ Adicionar otra Niña"):
            st.session_state.num_forms_ninas += 1
            st.rerun()

    # ------------------------------------------------
    # LÓGICA GLOBAL DE TELA (SOLO SI HAY PANTALONES)
    # ------------------------------------------------
    st.markdown("---")
    
    # Calcular si hay pantalones en CUALQUIERA de los niños agregados al carrito
    total_pantalones_global = sum(n.get('Pantalones', 0) for n in st.session_state.carrito_ninos)
    
    entrega_tela_global = "No"
    metros_tela_global = 0.0

    if total_pantalones_global > 0:
        st.info(f"👖 Se detectaron {total_pantalones_global} pantalones en el pedido total.")
        st.markdown("#### Datos de Confección (Global)")
        col_tela1, col_tela2 = st.columns(2)
        with col_tela1:
            entrega_tela_global = st.radio("¿Entrega tela para la confección?", ("No", "Si"), index=0)
        with col_tela2:
            if entrega_tela_global == "Si":
                metros_tela_global = st.number_input("Metros totales de tela entregados:", min_value=0.0, step=0.1)

    # --- RESUMEN Y TOTALES ---
    st.markdown("---")
    st.subheader("🧾 Resumen Final")
    
    total_nino = sum(item['Subtotal'] for item in st.session_state.carrito_ninos)
    total_nina = sum(item['Subtotal'] for item in st.session_state.carrito_ninas)
    gran_total = total_nino + total_nina

    col_res1, col_res2 = st.columns(2)
    with col_res1:
        if st.session_state.carrito_ninos:
            st.markdown("**Lista Niños:**")
            st.dataframe(pd.DataFrame(st.session_state.carrito_ninos).drop(columns=['ID_Temp'], errors='ignore'))
    with col_res2:
        if st.session_state.carrito_ninas:
            st.markdown("**Lista Niñas:**")
            st.dataframe(pd.DataFrame(st.session_state.carrito_ninas).drop(columns=['ID_Temp'], errors='ignore'))

    st.markdown(f"## Total General: ${gran_total:,.0f}")

    # --- PAGO Y CIERRE ---
    st.markdown("### Registro de Pago")
    col_pay1, col_pay2 = st.columns(2)
    with col_pay1:
        valor_recibido = st.number_input("Valor Recibido", min_value=0, step=1000)
    with col_pay2:
        tipo_pago = st.selectbox("Tipo de Pago", ["Efectivo", "Transferencia"])

    estado_pago = "Pendiente"
    if valor_recibido > 0:
        if valor_recibido < gran_total:
            estado_pago = "Abono"
            st.warning(f"⚠️ Restan: ${gran_total - valor_recibido:,.0f}")
        elif valor_recibido == gran_total:
            estado_pago = "Pago Total"
            st.success("✅ PAGO TOTAL")
        else:
            st.error("Error: Valor recibido mayor al total")
    
    if st.button("💾 CERRAR VENTA Y GUARDAR"):
        if not nombre_cliente:
            st.error("Falta el nombre del cliente")
        elif gran_total == 0:
            st.error("El pedido está vacío")
        else:
            id_venta = datetime.now().strftime("%Y%m%d%H%M%S")
            nueva_venta = {
                "ID": id_venta,
                "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Cliente": nombre_cliente,
                "Celular": celular,
                "Colegio": colegio,
                "Descripción": descripcion,
                # Guardamos listas como string
                "Detalle Niños": str([ {k:v for k,v in i.items() if k!='ID_Temp'} for i in st.session_state.carrito_ninos]),
                "Detalle Niñas": str([ {k:v for k,v in i.items() if k!='ID_Temp'} for i in st.session_state.carrito_ninas]),
                "Entrega Tela": entrega_tela_global,
                "Metros Tela": metros_tela_global if entrega_tela_global == "Si" else 0,
                "Entrega Tela Pendiente": "Si" if entrega_tela_global == "No" and total_pantalones_global > 0 else "No",
                "Total General": gran_total,
                "Pagado": valor_recibido,
                "Saldo Pendiente": gran_total - valor_recibido,
                "Estado Pago": estado_pago,
                "Medio Pago": tipo_pago
            }
            guardar_venta(nueva_venta)
            
            # Reset
            st.session_state.carrito_ninos = []
            st.session_state.carrito_ninas = []
            st.session_state.num_forms_ninos = 1
            st.session_state.num_forms_ninas = 1
            st.balloons()
            st.success("Venta guardada exitosamente.")
            st.rerun()

# ==========================================
# SECCIÓN 2: BUSCAR Y EDITAR
# ==========================================
elif menu == "Buscar / Editar Ventas":
    st.header("Base de Datos")
    df = cargar_datos()
    
    if not df.empty:
        filtro = st.text_input("🔍 Buscar cliente...")
        if filtro:
            df = df[df['Cliente'].astype(str).str.contains(filtro, case=False) | df['ID'].astype(str).str.contains(filtro)]
        
        # Alerta visual colores
        st.dataframe(df.style.apply(lambda x: ['background-color: #ffcccc' if (x['Saldo Pendiente'] > 0 or x.get('Entrega Tela Pendiente') == 'Si') else 'background-color: #ccffcc' for i in x], axis=1))
        
        st.markdown("---")
        st.subheader("Gestión Post-Venta")
        id_editar = st.selectbox("Seleccione ID:", df['ID'].unique())
        
        if id_editar:
            idx = df[df['ID'] == id_editar].index[0]
            venta_act = df.loc[idx]
            
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                st.info(f"💰 Saldo Pendiente: ${venta_act['Saldo Pendiente']:,.0f}")
                nuevo_pago = st.number_input("Actualizar Total Pagado:", value=float(venta_act['Pagado']))
                if st.button("Actualizar Pago"):
                    df.at[idx, 'Pagado'] = nuevo_pago
                    saldo = venta_act['Total General'] - nuevo_pago
                    df.at[idx, 'Saldo Pendiente'] = saldo
                    df.at[idx, 'Estado Pago'] = "Pago Total" if saldo <= 0 else "Abono"
                    actualizar_db(df)
                    st.success("Pago actualizado")
                    st.rerun()

            with col_e2:
                # Lógica tela post-venta
                tela_pend = venta_act.get('Entrega Tela Pendiente', 'No')
                st.info(f"🧵 Entrega Tela Pendiente: {tela_pend}")
                
                if tela_pend == "Si":
                    metros_entregados = st.number_input("Metros que acaban de entregar:", min_value=0.0)
                    if st.button("Confirmar Recepción Tela"):
                        df.at[idx, 'Entrega Tela Pendiente'] = "No"
                        # Sumamos a lo que ya había (si había 0, pone los nuevos)
                        df.at[idx, 'Metros Tela'] = float(venta_act.get('Metros Tela', 0)) + metros_entregados
                        # Cambiamos el estado general de la venta a "Si" entregó tela
                        df.at[idx, 'Entrega Tela'] = "Si" 
                        actualizar_db(df)
                        st.success("Tela actualizada")
                        st.rerun()
    else:
        st.warning("Sin registros.")