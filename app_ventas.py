import streamlit as st
import pandas as pd
import os
from datetime import datetime
import time
import pytz 
import math
import json

# --- CONFIGURACIÓN DE ZONA HORARIA ---
timezone_co = pytz.timezone('America/Bogota')

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Gestión de Ventas Uniformes", layout="wide")
ARCHIVO_DB = 'base_datos_ventas.xlsx'
ARCHIVO_CONFIG = 'config_precios.json'

# --- ESTILOS CSS ---
st.markdown("""
<style>
    .stDataFrame { font-size: 14px; }
    .metric-card { background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-bottom: 10px; text-align: center; }
    .metric-title { font-size: 14px; font-weight: bold; color: #555; }
    .metric-value { font-size: 24px; font-weight: bold; color: #000; }
    div[data-testid="stSidebar"] { background-color: #f8f9fa; }
</style>
""", unsafe_allow_html=True)

# --- FUNCIONES DE BASE DE DATOS ---
def cargar_datos():
    if os.path.exists(ARCHIVO_DB):
        try:
            df = pd.read_excel(ARCHIVO_DB, dtype={'ID': str, 'Celular Principal': str, 'Celular Adicional': str})
            if 'Tela Sugerida (mts)' not in df.columns:
                return pd.DataFrame()
            return df
        except:
            return pd.DataFrame()
    else:
        return pd.DataFrame()

def guardar_venta(filas_venta):
    df = cargar_datos()
    df_nuevo = pd.DataFrame(filas_venta)
    df_final = pd.concat([df, df_nuevo], ignore_index=True)
    df_final.to_excel(ARCHIVO_DB, index=False)

def actualizar_db(df):
    df.to_excel(ARCHIVO_DB, index=False)

# --- FUNCIONES DE CONFIGURACIÓN (PRECIOS) ---
def cargar_config():
    defaults = {
        "precios_nino": {
            "4": 44000, "6": 44000, "8": 44000, "10": 44000, "12": 44000, "14": 44000,
            "16": 46000, "S": 46000, "M": 46000,
            "L": 48000, "XL": 48000
        },
        "precios_nina": {
            "4": 38000, "6": 38000, "8": 38000,
            "10": 40000, "12": 40000, "14": 40000, "16": 40000,
            "S": 43000, "M": 43000,
            "L": 46000, "XL": 46000
        },
        "precio_pantalon": 35000,
        "ultima_actualizacion": "Valores Iniciales"
    }
    
    if os.path.exists(ARCHIVO_CONFIG):
        try:
            with open(ARCHIVO_CONFIG, 'r') as f:
                return json.load(f)
        except:
            return defaults
    return defaults

def guardar_config(nuevo_config):
    with open(ARCHIVO_CONFIG, 'w') as f:
        json.dump(nuevo_config, f)

# --- FUNCIONES DE CÁLCULO ---
def redondear_tela(metros_reales):
    return math.ceil(metros_reales * 10) / 10

# --- INICIALIZACIÓN DE ESTADO ---
if 'carrito_ninos' not in st.session_state:
    st.session_state.carrito_ninos = []
if 'carrito_ninas' not in st.session_state:
    st.session_state.carrito_ninas = []

if 'num_forms_ninos' not in st.session_state:
    st.session_state.num_forms_ninos = 1
if 'num_forms_ninas' not in st.session_state:
    st.session_state.num_forms_ninas = 1

# Cargar configuración
config_actual = cargar_config()
precios_camisas_nino = config_actual["precios_nino"]
precios_camisas_nina = config_actual["precios_nina"]
costo_pantalon = config_actual["precio_pantalon"]

# --- BARRA LATERAL ---
st.sidebar.header("⚙️ Configuración")

# SECCIÓN DE RESPALDO
st.sidebar.markdown("### 📥 Respaldo y Restauración")

# 1. Descargar
if os.path.exists(ARCHIVO_DB):
    with open(ARCHIVO_DB, "rb") as f:
        bytes_data = f.read()
    
    ahora_bq = datetime.now(timezone_co)
    hora_generacion = ahora_bq.strftime("%Y-%m-%d %I:%M %p")
    
    st.sidebar.download_button(
        label="Descargar Excel",
        data=bytes_data,
        file_name=f"Ventas_Uniformes_{ahora_bq.strftime('%Y-%m-%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    st.sidebar.caption(f"📅 Datos al: {hora_generacion}")
else:
    st.sidebar.warning("Base de datos vacía.")

st.sidebar.markdown("---")

# 2. Subir (Restaurar)
st.sidebar.markdown("#### 🔄 Restaurar Base de Datos")
archivo_subido = st.sidebar.file_uploader("Subir Excel para restaurar", type=["xlsx"])

if archivo_subido is not None:
    if st.sidebar.button("⚠️ Confirmar Restauración"):
        try:
            df_restore = pd.read_excel(archivo_subido)
            if 'ID' in df_restore.columns:
                df_restore.to_excel(ARCHIVO_DB, index=False)
                st.sidebar.success("¡Restauración exitosa! Reiniciando...")
                time.sleep(2)
                st.rerun()
            else:
                st.sidebar.error("El archivo no tiene el formato correcto (falta columna ID).")
        except Exception as e:
            st.sidebar.error(f"Error al restaurar: {e}")

st.sidebar.markdown("---")
st.sidebar.header("💰 Gestión de Precios")

st.sidebar.info(f"📅 Act: {config_actual.get('ultima_actualizacion', 'N/A')}")

with st.sidebar.form("form_precios"):
    tallas = ["4", "6", "8", "10", "12", "14", "16", "S", "M", "L", "XL"]

    st.markdown("#### 👦 Camisas NIÑO")
    input_precios_nino = {}
    for talla in tallas:
        val_default = config_actual["precios_nino"].get(talla, 0)
        input_precios_nino[talla] = st.number_input(f"Costo Niño Talla {talla}", value=int(val_default), step=1000, format="%d", key=f"p_nino_{talla}")

    st.markdown("#### 👖 Pantalón NIÑO")
    val_pant = config_actual.get("precio_pantalon", 35000)
    input_pantalon = st.number_input("Costo Pantalón", value=int(val_pant), step=1000, format="%d")

    st.markdown("---")
    st.markdown("#### 👧 Camisas NIÑA")
    input_precios_nina = {}
    for talla in tallas:
        val_default = config_actual["precios_nina"].get(talla, 0)
        input_precios_nina[talla] = st.number_input(f"Costo Niña Talla {talla}", value=int(val_default), step=1000, format="%d", key=f"p_nina_{talla}")
    
    submitted = st.form_submit_button("💾 CONFIRMAR CAMBIOS")
    
    if submitted:
        ahora_bq = datetime.now(timezone_co)
        fecha_act = ahora_bq.strftime("%Y-%m-%d %I:%M %p")
        
        nuevo_conf = {
            "precios_nino": input_precios_nino,
            "precios_nina": input_precios_nina,
            "precio_pantalon": input_pantalon,
            "ultima_actualizacion": fecha_act
        }
        guardar_config(nuevo_conf)
        st.success("✅ Precios actualizados!")
        time.sleep(1)
        st.rerun()


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
        nombre_cliente = st.text_input("Nombre Cliente (Obligatorio)")
        celular_principal = st.text_input("Celular Principal (Obligatorio)")
        celular_adicional = st.text_input("Celular Adicional (Opcional)")
        
    with col2:
        descripcion = st.text_area("Descripción")
        colegio = st.text_input("Colegio", value="NCP") 

    st.markdown("---")
    
    col_main_nino, col_main_nina = st.columns(2)
    
    with col_main_nino:
        st.markdown("### 👦 Niño")
        
        for i in range(st.session_state.num_forms_ninos):
            num_nino = i + 1
            with st.expander(f"Detalles Niño {num_nino}", expanded=True):
                nombre_alumno_m = st.text_input(f"Nombre Alumno", key=f"nom_nino_{i}")
                
                cant_camisa_m = st.number_input("Cant. Camisa", min_value=0, value=0, key=f"cant_cam_nino_{i}")
                talla_camisa_m = "4" 
                if cant_camisa_m > 0:
                    talla_camisa_m = st.selectbox("Talla Camisa", tallas, key=f"talla_nino_{i}")
                    costo_actual = precios_camisas_nino.get(talla_camisa_m, 0)
                    st.caption(f"Precio Unitario: ${costo_actual:,.0f}")
                
                st.markdown("---")
                
                cant_pantalon = st.number_input("Cant. Pantalón", min_value=0, value=0, key=f"cant_pant_nino_{i}")
                
                cintura, cadera, pierna, largo_cm = 0, 0, 0, 0
                if cant_pantalon > 0:
                    st.caption("Medidas Pantalón (cm):")
                    cintura = st.number_input("Cintura (cm)", min_value=0, step=1, format="%d", key=f"cint_nino_{i}")
                    cadera = st.number_input("Cadera (cm)", min_value=0, step=1, format="%d", key=f"cad_nino_{i}")
                    pierna = st.number_input("Pierna (cm)", min_value=0, step=1, format="%d", key=f"pier_nino_{i}")
                    
                    largo_cm = st.number_input("Largo Pantalón (cm)", min_value=0, step=1, format="%d", key=f"largo_nino_{i}")

                es_actualizacion = i < len(st.session_state.carrito_ninos)
                texto_boton = "🔄 Actualizar pedido" if es_actualizacion else "✅ Confirmar pedido"
                
                if st.button(texto_boton, key=f"btn_nino_{i}"):
                    precio_camisa = precios_camisas_nino.get(talla_camisa_m, 0) if cant_camisa_m > 0 else 0
                    subtotal = (cant_camisa_m * precio_camisa) + (cant_pantalon * costo_pantalon)
                    
                    consumo_tela_item = ((largo_cm / 100.0) + 0.20) * cant_pantalon if cant_pantalon > 0 else 0
                    
                    item_data = {
                        "ID_Temp": i, 
                        "Tipo_Visual": f"Niño {num_nino}",
                        "Nombre Alumno": nombre_alumno_m,
                        "Camisas": cant_camisa_m,
                        "Talla Camisa": talla_camisa_m if cant_camisa_m > 0 else "N/A",
                        "Pantalones": cant_pantalon,
                        "Medidas Cin": cintura if cant_pantalon > 0 else 0,
                        "Medidas Cad": cadera if cant_pantalon > 0 else 0,
                        "Medidas Pier": pierna if cant_pantalon > 0 else 0,
                        "Largo Pantalon": largo_cm if cant_pantalon > 0 else 0, 
                        "Consumo Tela Calc": consumo_tela_item,
                        "Subtotal": subtotal
                    }
                    
                    if es_actualizacion:
                        st.session_state.carrito_ninos[i] = item_data
                        st.success(f"Niño {num_nino} actualizado.")
                    else:
                        st.session_state.carrito_ninos.append(item_data)
                        st.success(f"Niño {num_nino} confirmado.")

        if st.button("➕ Adicionar otro Niño"):
            st.session_state.num_forms_ninos += 1
            st.rerun()

    with col_main_nina:
        st.markdown("### 👧 Niña")
        
        for i in range(st.session_state.num_forms_ninas):
            num_nina = i + 1
            with st.expander(f"Detalles Niña {num_nina}", expanded=True):
                nombre_alumno_f = st.text_input(f"Nombre Alumna", key=f"nom_nina_{i}")
                
                cant_camisa_f = st.number_input("Cant. Camisa", min_value=0, value=0, key=f"cant_cam_nina_{i}")
                talla_camisa_f = "4"
                if cant_camisa_f > 0:
                    talla_camisa_f = st.selectbox("Talla Camisa", tallas, key=f"talla_nina_{i}")
                    costo_actual = precios_camisas_nina.get(talla_camisa_f, 0)
                    st.caption(f"Precio Unitario: ${costo_actual:,.0f}")
                
                es_actualizacion_f = i < len(st.session_state.carrito_ninas)
                texto_boton_f = "🔄 Actualizar pedido" if es_actualizacion_f else "✅ Confirmar pedido"

                if st.button(texto_boton_f, key=f"btn_nina_{i}"):
                    precio_camisa = precios_camisas_nina.get(talla_camisa_f, 0) if cant_camisa_f > 0 else 0
                    subtotal = (cant_camisa_f * precio_camisa)
                    
                    item_data = {
                        "ID_Temp": i,
                        "Tipo_Visual": f"Niña {num_nina}",
                        "Nombre Alumno": nombre_alumno_f,
                        "Camisas": cant_camisa_f,
                        "Talla Camisa": talla_camisa_f if cant_camisa_f > 0 else "N/A",
                        "Subtotal": subtotal
                    }
                    
                    if es_actualizacion_f:
                        st.session_state.carrito_ninas[i] = item_data
                        st.success(f"Niña {num_nina} actualizada.")
                    else:
                        st.session_state.carrito_ninas.append(item_data)
                        st.success(f"Niña {num_nina} confirmada.")

        if st.button("➕ Adicionar otra Niña"):
            st.session_state.num_forms_ninas += 1
            st.rerun()

    st.markdown("---")
    
    consumo_tela_bruto = sum(n.get('Consumo Tela Calc', 0) for n in st.session_state.carrito_ninos)
    tela_requerida_sugerida = redondear_tela(consumo_tela_bruto)
    
    total_pantalones_global = sum(n.get('Pantalones', 0) for n in st.session_state.carrito_ninos)
    
    entrega_tela_global = "No"
    metros_tela_global = 0.0

    if total_pantalones_global > 0:
        st.info(f"👖 {total_pantalones_global} Pantalones. Consumo calculado: {consumo_tela_bruto:.2f}mts -> Sugerido: **{tela_requerida_sugerida}mts**")
        
        col_tela1, col_tela2 = st.columns(2)
        with col_tela1:
            entrega_tela_global = st.radio("¿Entrega tela para la confección?", ("No", "Si"), index=0)
        with col_tela2:
            if entrega_tela_global == "Si":
                metros_tela_global = st.number_input("Metros totales de tela entregados (mts):", min_value=0.0, step=0.1, format="%.2f")
                
                if metros_tela_global >= tela_requerida_sugerida:
                    st.success("✅ Tela suficiente.")
                else:
                    st.warning(f"⚠️ Faltan {tela_requerida_sugerida - metros_tela_global:.2f}mts aprox.")

    st.markdown("---")
    st.subheader("🧾 Resumen Final")
    
    total_nino = sum(item['Subtotal'] for item in st.session_state.carrito_ninos)
    total_nina = sum(item['Subtotal'] for item in st.session_state.carrito_ninas)
    gran_total = total_nino + total_nina

    col_res1, col_res2 = st.columns(2)
    with col_res1:
        if st.session_state.carrito_ninos:
            df_ninos_view = pd.DataFrame(st.session_state.carrito_ninos)
            if not df_ninos_view.empty:
                st.markdown("**Lista Niños:**")
                df_show_nino = df_ninos_view[['Tipo_Visual', 'Nombre Alumno', 'Largo Pantalon', 'Subtotal']].rename(columns={'Largo Pantalon': 'Largo Pant (cm)'})
                st.dataframe(df_show_nino)
    with col_res2:
        if st.session_state.carrito_ninas:
            df_ninas_view = pd.DataFrame(st.session_state.carrito_ninas)
            if not df_ninas_view.empty:
                st.markdown("**Lista Niñas:**")
                st.dataframe(df_ninas_view[['Tipo_Visual', 'Nombre Alumno', 'Subtotal']])

    st.markdown(f"## Total General: ${gran_total:,.0f}")

    st.markdown("### Registro de Pago")
    col_pay1, col_pay2 = st.columns(2)
    with col_pay1:
        valor_recibido = st.number_input("Valor Recibido", min_value=0, step=1000, format="%d")
    with col_pay2:
        tipo_pago = st.selectbox("Tipo de Pago", ["-Seleccionar-", "Efectivo", "Transferencia"])

    estado_pago = "Pendiente"
    if valor_recibido == 0:
        estado_pago = "Pendiente"
    elif valor_recibido > 0:
        if valor_recibido < gran_total:
            estado_pago = "Abono"
            st.warning(f"⚠️ Restan: ${gran_total - valor_recibido:,.0f}")
        elif valor_recibido == gran_total:
            estado_pago = "Pago Total"
            st.success("✅ PAGO TOTAL")
        else:
            st.error("Error: Valor recibido mayor al total")
    
    if st.button("💾 CERRAR VENTA Y GUARDAR"):
        errores = []
        if not nombre_cliente: errores.append("Falta Nombre Cliente")
        if not celular_principal: errores.append("Falta Celular Principal")
        if gran_total == 0: errores.append("El pedido está vacío")
        if valor_recibido > 0 and tipo_pago == "-Seleccionar-":
            errores.append("Seleccione un Tipo de Pago válido")

        if errores:
            for e in errores: st.error(f"⚠️ {e}")
        else:
            ahora_bq = datetime.now(timezone_co)
            fecha_hoy = ahora_bq.strftime("%Y-%m-%d %H:%M")
            id_venta = ahora_bq.strftime("%Y%m%d%H%M%S")
            
            fecha_abono = fecha_hoy if (estado_pago == "Abono") else ""
            fecha_total = fecha_hoy if (estado_pago == "Pago Total") else ""
            
            # Lógica Entrega Tela (Niñas o sin pantalón -> No Aplica)
            entrega_tela_str = entrega_tela_global if entrega_tela_global == "Si" else "No"
            
            saldo_pagado_por_asignar = valor_recibido
            metros_tela_por_asignar = metros_tela_global if entrega_tela_global == "Si" else 0
            
            todos_items = []
            for n in st.session_state.carrito_ninos: n['EsNino'] = True; todos_items.append(n)
            for n in st.session_state.carrito_ninas: n['EsNino'] = False; todos_items.append(n)
            
            filas_a_guardar = []
            fecha_entrega_tela_log = fecha_hoy if entrega_tela_global == "Si" else ""
            
            for index, item in enumerate(todos_items):
                subtotal_item = item['Subtotal']
                
                if saldo_pagado_por_asignar >= subtotal_item:
                    pago_asignado = subtotal_item
                else:
                    pago_asignado = saldo_pagado_por_asignar
                
                saldo_pagado_por_asignar -= pago_asignado
                if saldo_pagado_por_asignar < 0: saldo_pagado_por_asignar = 0

                saldo_pendiente_item = subtotal_item - pago_asignado
                
                metros_asignados = 0
                
                # Definir estado de entrega tela para esta fila
                estado_entrega_tela_fila = "No Aplica"
                if item.get("Pantalones", 0) > 0:
                    estado_entrega_tela_fila = entrega_tela_str
                    # Asignación de tela cascada
                    if metros_tela_por_asignar > 0:
                        metros_asignados = metros_tela_por_asignar
                        metros_tela_por_asignar = 0 # Toda la tela global se asigna al primer registro que necesite (si no se quiere distribuir)
                        # Nota: En nueva venta asignamos todo al primero o distribuimos?
                        # Para simplificar y seguir lógica anterior: todo al primero del grupo.
                
                fila = {
                    "ID": id_venta,
                    "Fecha Venta": fecha_hoy,
                    "Cliente": nombre_cliente,
                    "Celular Principal": str(celular_principal).strip(),
                    "Celular Adicional": str(celular_adicional).strip() if celular_adicional else "",
                    "Colegio": colegio,
                    "Descripción": descripcion,
                    "Tipo Detalle": item["Tipo_Visual"],
                    "Nombre Alumno": item["Nombre Alumno"],
                    "Camisas": item["Camisas"],
                    "Talla Camisa": item["Talla Camisa"],
                    "Pantalones": item.get("Pantalones", 0),
                    
                    "Largo Pant (cm)": item.get("Largo Pantalon", 0),
                    "Medidas Cin (cm)": item.get("Medidas Cin", 0),
                    "Medidas Cad (cm)": item.get("Medidas Cad", 0),
                    "Medidas Pier (cm)": item.get("Medidas Pier", 0),
                    
                    "Tela Sugerida (mts)": round(item.get("Consumo Tela Calc", 0), 2),
                    
                    "Subtotal niño(a)": subtotal_item,
                    "Pagado (Distribuido)": int(pago_asignado),
                    "Saldo Pendiente (Distribuido)": int(saldo_pendiente_item),
                    "Estado Pago": estado_pago,
                    "Medio Pago": tipo_pago if pago_asignado > 0 else "",
                    "Fecha Abono": fecha_abono if pago_asignado > 0 else "",
                    "Fecha Total Pago": fecha_total,
                    
                    "Entrega Tela": estado_entrega_tela_fila,
                    "Metros Tela (mts)": round(metros_asignados, 2),
                    "Fecha Entrega Tela": fecha_entrega_tela_log if metros_asignados > 0 else "",
                    "Fecha Entrega Nueva Tela": ""
                }
                filas_a_guardar.append(fila)
            
            if saldo_pagado_por_asignar > 0 and filas_a_guardar:
                filas_a_guardar[-1]["Pagado (Distribuido)"] += int(saldo_pagado_por_asignar)

            guardar_venta(filas_a_guardar)
            
            st.session_state.carrito_ninos = []
            st.session_state.carrito_ninas = []
            st.session_state.num_forms_ninos = 1
            st.session_state.num_forms_ninas = 1
            st.balloons()
            st.success("Venta guardada exitosamente.")
            time.sleep(2)
            st.rerun()

# ==========================================
# SECCIÓN 2: BUSCAR / EDITAR / DATOS POST-VENTA
# ==========================================
elif menu == "Buscar / Editar Ventas":
    df = cargar_datos()
    
    st.header("📊 Datos Post-Venta")
    
    if not df.empty:
        # --- FILTRO POR TALLA ---
        col_dash_filter, _ = st.columns([1, 3])
        with col_dash_filter:
            talla_filter = st.selectbox("Filtrar conteo por Talla:", ["Todas"] + tallas)
        
        if talla_filter == "Todas":
            df_counts = df
        else:
            df_counts = df[df['Talla Camisa'].astype(str) == talla_filter]

        total_camisas_nino = df_counts[df_counts['Tipo Detalle'].astype(str).str.contains("Niño", na=False)]['Camisas'].sum()
        total_camisas_nina = df_counts[df_counts['Tipo Detalle'].astype(str).str.contains("Niña", na=False)]['Camisas'].sum()
        total_pantalones = df_counts['Pantalones'].sum()

        total_ventas_dinero = df_counts['Subtotal niño(a)'].sum()
        total_pendiente_dinero = df_counts['Saldo Pendiente (Distribuido)'].sum()
        
        total_tela_sugerida = df_counts['Tela Sugerida (mts)'].sum()
        total_tela_entregada = df_counts['Metros Tela (mts)'].sum()
        balance_tela = total_tela_entregada - total_tela_sugerida

        st.markdown("---")
        
        st.subheader("Conteo de Prendas")
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.markdown(f"<div class='metric-card'><div class='metric-title'>Camisas Niño</div><div class='metric-value'>{int(total_camisas_nino)}</div></div>", unsafe_allow_html=True)
        with col_m2:
            st.markdown(f"<div class='metric-card'><div class='metric-title'>Pantalones</div><div class='metric-value'>{int(total_pantalones)}</div></div>", unsafe_allow_html=True)
        with col_m3:
            st.markdown(f"<div class='metric-card'><div class='metric-title'>Camisas Niña</div><div class='metric-value'>{int(total_camisas_nina)}</div></div>", unsafe_allow_html=True)

        st.subheader("Financiero & Tela")
        col_f1, col_f2, col_f3, col_f4 = st.columns(4)
        
        with col_f1:
            st.markdown(f"<div class='metric-card'><div class='metric-title'>Venta Total</div><div class='metric-value'>${total_ventas_dinero:,.0f}</div></div>", unsafe_allow_html=True)
        with col_f2:
             color_deuda = "#d9534f" if total_pendiente_dinero > 0 else "#5cb85c"
             st.markdown(f"<div class='metric-card'><div class='metric-title'>Cartera (Pendiente)</div><div class='metric-value' style='color:{color_deuda}'>${total_pendiente_dinero:,.0f}</div></div>", unsafe_allow_html=True)
        
        with col_f3:
            st.markdown(f"<div class='metric-card'><div class='metric-title'>Tela Sugerida</div><div class='metric-value'>{total_tela_sugerida:,.2f} m</div></div>", unsafe_allow_html=True)
        with col_f4:
            color_tela = "#d9534f" if balance_tela < 0 else "#5cb85c"
            texto_balance = f"{balance_tela:,.2f} m" if balance_tela >= 0 else f"{balance_tela:,.2f} m (Falta)"
            st.markdown(f"<div class='metric-card'><div class='metric-title'>Balance Tela</div><div class='metric-value' style='color:{color_tela}'>{texto_balance}</div></div>", unsafe_allow_html=True)

    else:
        st.info("No hay datos para mostrar estadísticas.")

    st.markdown("---")
    st.header("🔎 Base de Datos y Gestión")
    
    if not df.empty:
        col_filtro1, col_filtro2 = st.columns([1, 2])
        with col_filtro1:
            criterio = st.selectbox("Buscar por:", [
                "Cliente", "Celular Principal", "Celular Adicional", 
                "Colegio", "Nombre Alumno", 
                "Clientes con SALDO pendiente", "Clientes con TELA pendiente"
            ])
        
        with col_filtro2:
            if "pendiente" in criterio:
                valor_busqueda = ""
            else:
                valor_busqueda = st.text_input(f"Escriba dato para {criterio}...")

        df_filtrado = df.copy()
        if "SALDO pendiente" in criterio:
            ids_con_saldo = df.groupby('ID')['Saldo Pendiente (Distribuido)'].sum()
            ids_con_saldo = ids_con_saldo[ids_con_saldo > 0].index
            df_filtrado = df[df['ID'].isin(ids_con_saldo)]
        elif "TELA pendiente" in criterio:
            df_filtrado = df[(df['Entrega Tela'] == 'No') & (df['Pantalones'] > 0)]
        elif valor_busqueda:
            if criterio == "Cliente":
                df_filtrado = df[df['Cliente'].astype(str).str.contains(valor_busqueda, case=False, na=False)]
            elif "Celular" in criterio:
                df_filtrado = df[df[criterio].astype(str).str.contains(valor_busqueda, case=False, na=False)]
            elif criterio == "Nombre Alumno":
                df_filtrado = df[df['Nombre Alumno'].astype(str).str.contains(valor_busqueda, case=False, na=False)]
            else:
                df_filtrado = df[df[criterio].astype(str).str.contains(valor_busqueda, case=False, na=False)]
        
        def color_rows(row):
            if row['Saldo Pendiente (Distribuido)'] > 0:
                return ['background-color: rgba(255, 0, 0, 0.2)'] * len(row)
            elif row['Entrega Tela'] == 'No' and row['Pantalones'] > 0:
                return ['background-color: rgba(255, 0, 0, 0.2)'] * len(row)
            return ['background-color: rgba(0, 128, 0, 0.2)'] * len(row)

        format_dict = {
            "Tela Sugerida (mts)": "{:.2f}",
            "Metros Tela (mts)": "{:.2f}",
            "Subtotal niño(a)": "${:,.0f}",
            "Pagado (Distribuido)": "${:,.0f}",
            "Saldo Pendiente (Distribuido)": "${:,.0f}"
        }
        
        st.dataframe(df_filtrado.style.format(format_dict, na_rep="-").apply(color_rows, axis=1))

        st.markdown("---")
        st.subheader("Gestión Post-Venta (Individual)")
        
        lista_clientes = df['Cliente'].unique().tolist()
        col_sel1, col_sel2 = st.columns(2)
        cliente_sel = col_sel1.selectbox("Seleccione Cliente:", options=[""] + lista_clientes)
        
        if cliente_sel:
            ids_disponibles = df[df['Cliente'] == cliente_sel]['ID'].unique().tolist()
        else:
            ids_disponibles = df['ID'].unique().tolist()
            
        id_editar = col_sel2.selectbox("Seleccione ID Venta:", options=[""] + ids_disponibles)
        
        if id_editar:
            filas_venta = df[df['ID'] == id_editar]
            
            # --- SECCIÓN DE EDICIÓN Y ELIMINACIÓN DE VENTA ---
            st.markdown("#### 🛠️ Modificar / Eliminar Venta")
            
            # Botón Eliminar
            if st.button("🗑️ Eliminar esta Venta Completa", type="primary"):
                try:
                    df = df[df['ID'] != id_editar]
                    actualizar_db(df)
                    st.success("Venta eliminada correctamente.")
                    time.sleep(1.5)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al eliminar: {e}")

            st.write("Puede modificar las cantidades, tallas o medidas directamente en la tabla. Al finalizar, presione 'Guardar Cambios'.")
            
            # Columnas editables
            cols_edit = ['Nombre Alumno', 'Camisas', 'Talla Camisa', 'Pantalones', 
                         'Largo Pant (cm)', 'Medidas Cin (cm)', 'Medidas Cad (cm)', 'Medidas Pier (cm)']
            
            edited_df = st.data_editor(filas_venta[cols_edit], num_rows="fixed")
            
            if st.button("💾 Guardar Cambios en Registros"):
                # Proceso de actualización lógica
                indices_editados = filas_venta.index
                
                for idx in indices_editados:
                    row_data = edited_df.loc[idx]
                    
                    # 1. Recalcular Subtotal
                    talla = row_data['Talla Camisa']
                    qty_cam = row_data['Camisas']
                    qty_pant = row_data['Pantalones']
                    
                    # Determinar precio camisa (Niño vs Niña)
                    tipo_detalle = df.at[idx, 'Tipo Detalle']
                    if "Niña" in str(tipo_detalle):
                         precio_c = precios_camisas_nina.get(str(talla), 30000)
                    else:
                         precio_c = precios_camisas_nino.get(str(talla), 30000)
                    
                    nuevo_subtotal = (qty_cam * precio_c) + (qty_pant * costo_pantalon)
                    
                    # 2. Recalcular Consumo Tela
                    largo_cm = row_data['Largo Pant (cm)']
                    consumo_tela = 0.0
                    if qty_pant > 0:
                        consumo_tela = ((largo_cm / 100.0) + 0.20) * qty_pant
                    
                    # 3. Actualizar Dataframe original
                    df.at[idx, 'Nombre Alumno'] = row_data['Nombre Alumno']
                    df.at[idx, 'Camisas'] = qty_cam
                    df.at[idx, 'Talla Camisa'] = talla
                    df.at[idx, 'Pantalones'] = qty_pant
                    df.at[idx, 'Largo Pant (cm)'] = largo_cm
                    df.at[idx, 'Medidas Cin (cm)'] = row_data['Medidas Cin (cm)']
                    df.at[idx, 'Medidas Cad (cm)'] = row_data['Medidas Cad (cm)']
                    df.at[idx, 'Medidas Pier (cm)'] = row_data['Medidas Pier (cm)']
                    
                    df.at[idx, 'Subtotal niño(a)'] = nuevo_subtotal
                    df.at[idx, 'Tela Sugerida (mts)'] = round(consumo_tela, 2)
                    
                    # Recalcular Saldo Pendiente (Nuevo Subtotal - Lo que ya pagó)
                    pagado_actual = df.at[idx, 'Pagado (Distribuido)']
                    nuevo_saldo = nuevo_subtotal - pagado_actual
                    if nuevo_saldo < 0: nuevo_saldo = 0 # No permitir saldos negativos
                    df.at[idx, 'Saldo Pendiente (Distribuido)'] = int(nuevo_saldo)
                    
                    # Actualizar "No Aplica" si pantalones bajaron a 0
                    if qty_pant == 0:
                        df.at[idx, 'Entrega Tela'] = "No Aplica"

                actualizar_db(df)
                st.success("Registros actualizados y recalculados.")
                time.sleep(1.5)
                st.rerun()

            st.markdown("---")
            
            # --- SECCIÓN PAGOS Y TELA (SIN CAMBIOS LÓGICOS MAYORES, SOLO VISUAL) ---
            
            # Recalcular totales visuales con la data (posiblemente) editada
            filas_venta_actual = df[df['ID'] == id_editar]
            total_venta_real = filas_venta_actual['Subtotal niño(a)'].sum()
            pagado_real = filas_venta_actual['Pagado (Distribuido)'].sum()
            saldo_real = filas_venta_actual['Saldo Pendiente (Distribuido)'].sum()
            metros_entregados_real = filas_venta_actual['Metros Tela (mts)'].sum()

            st.info(f"Resumen Financiero: Total: ${total_venta_real:,.0f} | Pagado: ${pagado_real:,.0f} | **Saldo Pendiente: ${saldo_real:,.0f}**")

            col_post1, col_post2 = st.columns(2)
            
            with col_post1:
                st.markdown("#### 💸 Actualizar Pagos")
                if saldo_real > 0:
                    abono_extra = st.number_input("Ingresar Nuevo Abono ($):", min_value=0, step=1000, format="%d")
                    medio_abono = st.selectbox("Medio de Pago:", ["-Seleccionar-", "Efectivo", "Transferencia"], key="pay_post")
                    
                    if st.button("Registrar Pago"):
                        if medio_abono == "-Seleccionar-" or abono_extra == 0:
                            st.error("Verifique monto y medio de pago.")
                        else:
                            ahora_bq = datetime.now(timezone_co)
                            fecha_ahora = ahora_bq.strftime("%Y-%m-%d %H:%M")
                            
                            abono_restante = abono_extra
                            indices = df[df['ID'] == id_editar].index
                            
                            for idx in indices:
                                if abono_restante <= 0: break
                                saldo_fila = df.at[idx, 'Saldo Pendiente (Distribuido)']
                                if saldo_fila > 0:
                                    monto_a_cubrir = min(saldo_fila, abono_restante)
                                    df.at[idx, 'Pagado (Distribuido)'] += monto_a_cubrir
                                    df.at[idx, 'Saldo Pendiente (Distribuido)'] -= monto_a_cubrir
                                    abono_restante -= monto_a_cubrir
                                    if df.at[idx, 'Pagado (Distribuido)'] == monto_a_cubrir:
                                         df.at[idx, 'Fecha Abono'] = fecha_ahora
                            
                            nuevo_saldo_total = df.loc[df['ID'] == id_editar, 'Saldo Pendiente (Distribuido)'].sum()
                            estado_nuevo = "Pago Total" if nuevo_saldo_total <= 0 else "Abono"
                            df.loc[df['ID'] == id_editar, 'Estado Pago'] = estado_nuevo
                            if estado_nuevo == "Pago Total":
                                df.loc[df['ID'] == id_editar, 'Fecha Total Pago'] = fecha_ahora
                                
                            actualizar_db(df)
                            st.success("Pago registrado.")
                            time.sleep(1.5); st.rerun()
                else:
                    st.success("PAZ Y SALVO")

            with col_post2:
                st.markdown("#### 🧵 Gestión de Tela")
                
                req_total = 0
                for index, row in filas_venta_actual.iterrows():
                    if row['Pantalones'] > 0:
                        largo_cm = row.get('Largo Pant (cm)', 0)
                        qty = row.get('Pantalones', 0)
                        consumo = ((largo_cm / 100.0) + 0.20) * qty
                        req_total += consumo
                
                req_sugerido = redondear_tela(req_total)
                pendiente_tela = req_sugerido - metros_entregados_real
                
                st.write(f"Total Sugerido: **{req_sugerido}mts** | Entregado: **{metros_entregados_real}mts**")
                
                if pendiente_tela > 0:
                    st.error(f"⚠️ PENDIENTE: **{pendiente_tela:.2f}mts**")
                elif pendiente_tela < 0:
                    st.success(f"✅ Sobrante: **{abs(pendiente_tela):.2f}mts**")
                else:
                    st.success("✅ COMPLETO")
                
                # LISTADO DETALLADO POR NIÑO (SIN LINEA DIVISORIA)
                st.markdown("**Detalle por Niño:**")
                for index, row in filas_venta_actual.iterrows():
                    if row['Pantalones'] > 0:
                        largo_cm = row.get('Largo Pant (cm)', 0)
                        qty = row.get('Pantalones', 0)
                        consumo = ((largo_cm / 100.0) + 0.20) * qty
                        st.write(f"• {row['Tipo Detalle']} | {row['Nombre Alumno']}: **{consumo:.2f} mts**")

                st.markdown("---")
                nuevos_metros = st.number_input("Adicionar tela entregada (mts):", min_value=0.0, step=0.1, format="%.2f")
                
                if st.button("Registrar Tela (Cascada)"):
                    if nuevos_metros > 0:
                        ahora_bq = datetime.now(timezone_co)
                        fecha_ahora = ahora_bq.strftime("%Y-%m-%d %H:%M")
                        
                        metros_por_asignar = nuevos_metros
                        indices_pant = df[(df['ID'] == id_editar) & (df['Pantalones'] > 0)].index
                        
                        actualizado_algo = False
                        
                        for idx in indices_pant:
                            if metros_por_asignar <= 0:
                                break
                                
                            largo_fila_cm = df.at[idx, 'Largo Pant (cm)']
                            qty_fila = df.at[idx, 'Pantalones']
                            consumo_fila_calc = ((largo_fila_cm / 100.0) + 0.20) * qty_fila
                            consumo_fila_aprox = redondear_tela(consumo_fila_calc) 
                            
                            tiene_asignado = df.at[idx, 'Metros Tela (mts)']
                            falta_fila = consumo_fila_aprox - tiene_asignado
                            
                            if falta_fila > 0:
                                aporte = min(falta_fila, metros_por_asignar)
                                df.at[idx, 'Metros Tela (mts)'] += aporte
                                metros_por_asignar -= aporte
                                actualizado_algo = True
                                
                                # LOG CASCADA (FECHA EN CADA FILA AFECTADA)
                                log_prev = str(df.at[idx, 'Fecha Entrega Nueva Tela'])
                                if log_prev == "nan": log_prev = ""
                                nuevo_log = f"{log_prev} | {fecha_ahora} (+{aporte:.2f}mts)".strip(" | ")
                                df.at[idx, 'Fecha Entrega Nueva Tela'] = nuevo_log

                        if metros_por_asignar > 0 and len(indices_pant) > 0:
                             idx_sobrante = indices_pant[0]
                             df.at[idx_sobrante, 'Metros Tela (mts)'] += metros_por_asignar
                             actualizado_algo = True
                             
                             # Log del sobrante también
                             log_prev = str(df.at[idx_sobrante, 'Fecha Entrega Nueva Tela'])
                             if log_prev == "nan": log_prev = ""
                             nuevo_log = f"{log_prev} | {fecha_ahora} (+{metros_por_asignar:.2f}mts)".strip(" | ")
                             df.at[idx_sobrante, 'Fecha Entrega Nueva Tela'] = nuevo_log

                        if actualizado_algo:
                            df.loc[df['ID'] == id_editar, 'Entrega Tela'] = "Si"
                            actualizar_db(df)
                            st.success("Tela distribuida correctamente.")
                            time.sleep(1.5); st.rerun()
    else:
        st.warning("No hay registros.")