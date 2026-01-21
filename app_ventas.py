import streamlit as st
import pandas as pd
import os
from datetime import datetime
import time

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Gestión de Ventas Uniformes", layout="wide")
ARCHIVO_DB = 'base_datos_ventas.xlsx'

# --- ESTILOS CSS PARA DARK MODE Y CONTRASTE ---
st.markdown("""
<style>
    /* Ajuste para tablas en modo oscuro/claro con transparencia */
    .stDataFrame { font-size: 14px; }
</style>
""", unsafe_allow_html=True)

# --- FUNCIONES DE BASE DE DATOS ---
def cargar_datos():
    if os.path.exists(ARCHIVO_DB):
        try:
            # Convertimos IDs y Celulares a string para evitar decimales extraños
            df = pd.read_excel(ARCHIVO_DB, dtype={'ID': str, 'Celular Principal': str, 'Celular Adicional': str})
            return df
        except:
            return pd.DataFrame()
    else:
        return pd.DataFrame()

def guardar_venta(filas_venta):
    df = cargar_datos()
    df_nuevo = pd.DataFrame(filas_venta)
    # Concatenar y guardar
    df_final = pd.concat([df, df_nuevo], ignore_index=True)
    df_final.to_excel(ARCHIVO_DB, index=False)

def actualizar_db(df):
    df.to_excel(ARCHIVO_DB, index=False)

# --- INICIALIZACIÓN DE ESTADO ---
if 'carrito_ninos' not in st.session_state:
    st.session_state.carrito_ninos = []
if 'carrito_ninas' not in st.session_state:
    st.session_state.carrito_ninas = []

# Formularios empiezan en 1
if 'num_forms_ninos' not in st.session_state:
    st.session_state.num_forms_ninos = 1
if 'num_forms_ninas' not in st.session_state:
    st.session_state.num_forms_ninas = 1

# --- BARRA LATERAL: CONFIGURACIÓN Y DESCARGA ---
st.sidebar.header("⚙️ Configuración")

# SECCIÓN DE DESCARGA
st.sidebar.markdown("### 📥 Respaldo de Datos")
if os.path.exists(ARCHIVO_DB):
    with open(ARCHIVO_DB, "rb") as f:
        bytes_data = f.read()
    
    # Capturar hora actual para el mensaje
    hora_generacion = datetime.now().strftime("%Y-%m-%d %I:%M %p")
    
    st.sidebar.download_button(
        label="Descargar Excel",
        data=bytes_data,
        file_name=f"Ventas_Uniformes_{datetime.now().strftime('%Y-%m-%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    st.sidebar.caption(f"📅 Archivo generado: {hora_generacion}")
else:
    st.sidebar.warning("Sin base de datos aún.")

st.sidebar.markdown("---")
st.sidebar.header("💰 Precios")
st.sidebar.info("Modificar precios no afecta ventas ya guardadas.")

tallas = ["4", "6", "8", "10", "12", "14", "16", "S", "M", "L", "XL"]

st.sidebar.markdown("#### 👦 Precios Camisas NIÑO")
precios_camisas_nino = {}
for talla in tallas:
    # format="%d" elimina decimales visuales, step=1000 mantiene enteros
    precios_camisas_nino[talla] = st.sidebar.number_input(f"Costo Niño Talla {talla}", value=30000, step=1000, format="%d", key=f"p_nino_{talla}")

st.sidebar.markdown("#### 👖 Precio Pantalón NIÑO")
costo_pantalon = st.sidebar.number_input("Costo Pantalón (Valor único)", value=45000, step=1000, format="%d")

st.sidebar.markdown("---")
st.sidebar.markdown("#### 👧 Precios Camisas NIÑA")
precios_camisas_nina = {}
for talla in tallas:
    precios_camisas_nina[talla] = st.sidebar.number_input(f"Costo Niña Talla {talla}", value=30000, step=1000, format="%d", key=f"p_nina_{talla}")


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
        # Campos de Cliente
        nombre_cliente = st.text_input("Nombre Cliente (Obligatorio)")
        celular_principal = st.text_input("Celular Principal (Obligatorio)")
        celular_adicional = st.text_input("Celular Adicional (Opcional)")
        
    with col2:
        descripcion = st.text_area("Descripción")
        colegio = st.text_input("Colegio", value="NCP") 

    st.markdown("---")
    
    col_main_nino, col_main_nina = st.columns(2)
    
    # ------------------------------------------------
    # LÓGICA DE NIÑOS (Inicia en 1)
    # ------------------------------------------------
    with col_main_nino:
        st.markdown("### 👦 Niño")
        
        for i in range(st.session_state.num_forms_ninos):
            # i arranca en 0, visualmente mostramos i+1
            num_nino = i + 1
            with st.expander(f"Detalles Niño {num_nino}", expanded=True):
                nombre_alumno_m = st.text_input(f"Nombre Alumno", key=f"nom_nino_{i}")
                
                # 1. Cantidad Camisa
                cant_camisa_m = st.number_input("Cant. Camisa", min_value=0, value=0, key=f"cant_cam_nino_{i}")
                
                talla_camisa_m = "4" 
                if cant_camisa_m > 0:
                    talla_camisa_m = st.selectbox("Talla Camisa", tallas, key=f"talla_nino_{i}")
                
                st.markdown("---")
                
                # 2. Cantidad Pantalón
                cant_pantalon = st.number_input("Cant. Pantalón", min_value=0, value=0, key=f"cant_pant_nino_{i}")
                
                cintura, cadera, pierna = 0, 0, 0 # Enteros
                if cant_pantalon > 0:
                    st.caption("Medidas Pantalón (Sin decimales):")
                    # step=1 y format="%d" para enteros
                    cintura = st.number_input("Cintura", min_value=0, step=1, format="%d", key=f"cint_nino_{i}")
                    cadera = st.number_input("Cadera", min_value=0, step=1, format="%d", key=f"cad_nino_{i}")
                    pierna = st.number_input("Pierna", min_value=0, step=1, format="%d", key=f"pier_nino_{i}")

                # Botón de acción
                es_actualizacion = i < len(st.session_state.carrito_ninos)
                texto_boton = "🔄 Actualizar pedido" if es_actualizacion else "✅ Confirmar pedido"
                
                if st.button(texto_boton, key=f"btn_nino_{i}"):
                    precio_camisa = precios_camisas_nino[talla_camisa_m] if cant_camisa_m > 0 else 0
                    subtotal = (cant_camisa_m * precio_camisa) + (cant_pantalon * costo_pantalon)
                    
                    item_data = {
                        "ID_Temp": i, 
                        "Tipo_Visual": f"Niño {num_nino}", # Para mostrar en pantalla
                        "Tipo_Base": "Niño",
                        "Nombre Alumno": nombre_alumno_m,
                        "Camisas": cant_camisa_m,
                        "Talla Camisa": talla_camisa_m if cant_camisa_m > 0 else "N/A",
                        "Pantalones": cant_pantalon,
                        "Medidas Cin": cintura if cant_pantalon > 0 else 0,
                        "Medidas Cad": cadera if cant_pantalon > 0 else 0,
                        "Medidas Pier": pierna if cant_pantalon > 0 else 0,
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

    # ------------------------------------------------
    # LÓGICA DE NIÑAS
    # ------------------------------------------------
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
                
                es_actualizacion_f = i < len(st.session_state.carrito_ninas)
                texto_boton_f = "🔄 Actualizar pedido" if es_actualizacion_f else "✅ Confirmar pedido"

                if st.button(texto_boton_f, key=f"btn_nina_{i}"):
                    precio_camisa = precios_camisas_nina[talla_camisa_f] if cant_camisa_f > 0 else 0
                    subtotal = (cant_camisa_f * precio_camisa)
                    
                    item_data = {
                        "ID_Temp": i,
                        "Tipo_Visual": f"Niña {num_nina}",
                        "Tipo_Base": "Niña",
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

    # ------------------------------------------------
    # LÓGICA GLOBAL DE TELA
    # ------------------------------------------------
    st.markdown("---")
    
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
                # Se permiten decimales al digitar, pero en BD se guardará redondeado o como float
                metros_tela_global = st.number_input("Metros totales de tela entregados:", min_value=0.0, step=0.1, format="%.2f")

    # --- RESUMEN Y TOTALES ---
    st.markdown("---")
    st.subheader("🧾 Resumen Final")
    
    total_nino = sum(item['Subtotal'] for item in st.session_state.carrito_ninos)
    total_nina = sum(item['Subtotal'] for item in st.session_state.carrito_ninas)
    gran_total = total_nino + total_nina

    # Visualización mejorada del resumen (Tipo Niño 1, Niño 2...)
    col_res1, col_res2 = st.columns(2)
    with col_res1:
        if st.session_state.carrito_ninos:
            df_ninos_view = pd.DataFrame(st.session_state.carrito_ninos)
            if not df_ninos_view.empty:
                st.markdown("**Lista Niños:**")
                st.dataframe(df_ninos_view[['Tipo_Visual', 'Nombre Alumno', 'Subtotal']])
    with col_res2:
        if st.session_state.carrito_ninas:
            df_ninas_view = pd.DataFrame(st.session_state.carrito_ninas)
            if not df_ninas_view.empty:
                st.markdown("**Lista Niñas:**")
                st.dataframe(df_ninas_view[['Tipo_Visual', 'Nombre Alumno', 'Subtotal']])

    st.markdown(f"## Total General: ${gran_total:,.0f}")

    # --- PAGO Y CIERRE ---
    st.markdown("### Registro de Pago")
    col_pay1, col_pay2 = st.columns(2)
    with col_pay1:
        # Sin decimales en valores monetarios
        valor_recibido = st.number_input("Valor Recibido", min_value=0, step=1000, format="%d")
    with col_pay2:
        tipo_pago = st.selectbox("Tipo de Pago", ["-Seleccionar-", "Efectivo", "Transferencia"])

    estado_pago = "Pendiente"
    if valor_recibido == 0:
        estado_pago = "Pendiente"
        st.info("Estado: Pendiente de pago")
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
        # VALIDACIONES
        errores = []
        if not nombre_cliente: errores.append("Falta Nombre Cliente")
        if not celular_principal: errores.append("Falta Celular Principal")
        if gran_total == 0: errores.append("El pedido está vacío")
        
        # Validar tipo de pago obligatorio SOLO si hay dinero recibido
        if valor_recibido > 0 and tipo_pago == "-Seleccionar-":
            errores.append("Seleccione un Tipo de Pago válido (Efectivo/Transferencia)")

        if errores:
            for e in errores:
                st.error(f"⚠️ {e}")
        else:
            # GENERAR FECHAS
            fecha_hoy = datetime.now().strftime("%Y-%m-%d %H:%M")
            id_venta = datetime.now().strftime("%Y%m%d%H%M%S") # Numérico string
            
            fecha_abono = fecha_hoy if (estado_pago == "Abono") else ""
            fecha_total = fecha_hoy if (estado_pago == "Pago Total") else ""
            
            # Fecha entrega tela: Si la entregan YA (Si) se pone la fecha, sino vacía
            fecha_entrega_tela = fecha_hoy if entrega_tela_global == "Si" else ""

            # PREPARAR FILAS (DESGLOSE UNICO POR NIÑO)
            filas_a_guardar = []
            
            # Datos comunes de la cabecera (Cliente y Totales)
            datos_cabecera = {
                "ID": id_venta,
                "Fecha Venta": fecha_hoy,
                "Cliente": nombre_cliente,
                "Celular Principal": str(celular_principal).strip(), # Limpiar espacios
                "Celular Adicional": str(celular_adicional).strip() if celular_adicional else "",
                "Colegio": colegio,
                "Descripción": descripcion,
                "Total General": int(gran_total),
                "Pagado": int(valor_recibido),
                "Saldo Pendiente": int(gran_total - valor_recibido),
                "Estado Pago": estado_pago,
                "Medio Pago": tipo_pago if valor_recibido > 0 else "",
                
                # Fechas
                "Fecha Abono": fecha_abono,
                "Fecha Total Pago": fecha_total,
                
                # Tela
                "Entrega Tela": entrega_tela_global,
                "Metros Tela": round(metros_tela_global, 2) if entrega_tela_global == "Si" else 0,
                "Fecha Entrega Tela": fecha_entrega_tela,
                "Fecha Entrega Nueva Tela": "" # Campo para adiciones futuras
            }
            
            # Procesar Niños
            for nino in st.session_state.carrito_ninos:
                fila = datos_cabecera.copy()
                # Campos específicos del niño
                fila.update({
                    "Tipo Detalle": nino["Tipo_Visual"], # Niño 1, Niño 2...
                    "Nombre Alumno": nino["Nombre Alumno"],
                    "Camisas": nino["Camisas"],
                    "Talla Camisa": nino["Talla Camisa"],
                    "Pantalones": nino["Pantalones"],
                    "Medidas Cin": nino.get("Medidas Cin", 0),
                    "Medidas Cad": nino.get("Medidas Cad", 0),
                    "Medidas Pier": nino.get("Medidas Pier", 0),
                    "Subtotal Item": nino["Subtotal"]
                })
                filas_a_guardar.append(fila)

            # Procesar Niñas
            for nina in st.session_state.carrito_ninas:
                fila = datos_cabecera.copy()
                fila.update({
                    "Tipo Detalle": nina["Tipo_Visual"], # Niña 1...
                    "Nombre Alumno": nina["Nombre Alumno"],
                    "Camisas": nina["Camisas"],
                    "Talla Camisa": nina["Talla Camisa"],
                    "Pantalones": 0,
                    "Medidas Cin": 0,
                    "Medidas Cad": 0,
                    "Medidas Pier": 0,
                    "Subtotal Item": nina["Subtotal"]
                })
                filas_a_guardar.append(fila)
            
            guardar_venta(filas_a_guardar)
            
            # LIMPIEZA COMPLETA DEL FORMULARIO
            st.session_state.carrito_ninos = []
            st.session_state.carrito_ninas = []
            st.session_state.num_forms_ninos = 1
            st.session_state.num_forms_ninas = 1
            # Para limpiar inputs de texto, la forma más efectiva en Streamlit es rerun
            # ya que no están vinculados a session_state persistentes fuera del loop
            
            st.balloons()
            st.success("Venta guardada y formulario limpiado.")
            time.sleep(2) # Pausa para ver el mensaje
            st.rerun()

# ==========================================
# SECCIÓN 2: BUSCAR / EDITAR / POST-VENTA
# ==========================================
elif menu == "Buscar / Editar Ventas":
    st.header("Base de Datos")
    df = cargar_datos()
    
    if not df.empty:
        # --- FILTRO AVANZADO ---
        col_filtro1, col_filtro2 = st.columns([1, 2])
        with col_filtro1:
            criterio = st.selectbox("Buscar por:", [
                "Cliente", 
                "Celular Principal", 
                "Celular Adicional", 
                "Colegio", 
                "Nombre Alumno", 
                "Clientes con SALDO pendiente",
                "Clientes con TELA pendiente"
            ])
        
        with col_filtro2:
            if "pendiente" in criterio:
                st.info(f"Mostrando filtro automático: {criterio}")
                valor_busqueda = ""
            else:
                valor_busqueda = st.text_input(f"Escriba dato para {criterio}...")

        # Aplicar Filtros
        df_filtrado = df.copy()
        
        if "SALDO pendiente" in criterio:
            df_filtrado = df[df['Saldo Pendiente'] > 0]
        elif "TELA pendiente" in criterio:
            # Lógica: Tiene pantalones, dijo NO entrega tela inicialmente, y no tiene fecha de entrega completa
            # O simplemente buscamos donde "Entrega Tela" sea No y haya Pantalones > 0
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
        
        # VISUALIZACIÓN DE LA TABLA CON COLORES ADAPTADOS (RGBA para contraste)
        # Rojo transparente: rgba(255, 0, 0, 0.2) | Verde transparente: rgba(0, 128, 0, 0.2)
        def color_rows(row):
            styles = []
            # Condición Saldo
            if row['Saldo Pendiente'] > 0:
                return ['background-color: rgba(255, 0, 0, 0.2)'] * len(row)
            # Condición Tela (Si debe tela)
            elif row['Entrega Tela'] == 'No' and row['Pantalones'] > 0:
                return ['background-color: rgba(255, 0, 0, 0.2)'] * len(row)
            else:
                return ['background-color: rgba(0, 128, 0, 0.2)'] * len(row)

        st.dataframe(df_filtrado.style.apply(color_rows, axis=1))

        st.markdown("---")
        st.subheader("Gestión Post-Venta")
        
        # --- SELECCIONADORES (VACÍOS INICIALMENTE) ---
        col_sel1, col_sel2 = st.columns(2)
        
        # Lista de clientes únicos para buscador
        lista_clientes = df['Cliente'].unique().tolist()
        cliente_sel = col_sel1.selectbox("Seleccione Cliente:", options=[""] + lista_clientes)
        
        # Lista de IDs (filtrada por cliente si se selecciona)
        if cliente_sel:
            ids_disponibles = df[df['Cliente'] == cliente_sel]['ID'].unique().tolist()
        else:
            ids_disponibles = df['ID'].unique().tolist()
            
        id_editar = col_sel2.selectbox("Seleccione ID Venta:", options=[""] + ids_disponibles)
        
        if id_editar:
            # Obtenemos todas las filas de esa venta (porque ahora son varias filas por venta)
            filas_venta = df[df['ID'] == id_editar]
            # Tomamos la primera fila para sacar los datos generales (Totales, Cliente, etc)
            venta_gral = filas_venta.iloc[0]
            
            st.info(f"Cliente: **{venta_gral['Cliente']}** | Total Venta: ${venta_gral['Total General']:,.0f} | Saldo Actual: ${venta_gral['Saldo Pendiente']:,.0f}")
            
            col_post1, col_post2 = st.columns(2)
            
            # --- ACTUALIZACIÓN DE PAGO ---
            with col_post1:
                st.markdown("#### 💸 Actualizar Pagos")
                if venta_gral['Saldo Pendiente'] > 0:
                    abono_extra = st.number_input("Ingresar Nuevo Abono ($):", min_value=0, step=1000, format="%d")
                    medio_abono = st.selectbox("Medio de Pago del Abono:", ["-Seleccionar-", "Efectivo", "Transferencia"], key="pay_method_post")
                    
                    if st.button("Registrar Pago"):
                        if medio_abono == "-Seleccionar-" and abono_extra > 0:
                            st.error("Seleccione el medio de pago.")
                        else:
                            nuevo_pagado = venta_gral['Pagado'] + abono_extra
                            nuevo_saldo = venta_gral['Total General'] - nuevo_pagado
                            fecha_ahora = datetime.now().strftime("%Y-%m-%d %H:%M")
                            
                            # Actualizar TODAS las filas que tengan ese ID
                            df.loc[df['ID'] == id_editar, 'Pagado'] = nuevo_pagado
                            df.loc[df['ID'] == id_editar, 'Saldo Pendiente'] = nuevo_saldo
                            
                            # Logica Fechas
                            if venta_gral['Pagado'] == 0: # Era el primer abono
                                df.loc[df['ID'] == id_editar, 'Fecha Abono'] = fecha_ahora
                                
                            if nuevo_saldo <= 0:
                                df.loc[df['ID'] == id_editar, 'Estado Pago'] = "Pago Total"
                                df.loc[df['ID'] == id_editar, 'Fecha Total Pago'] = fecha_ahora
                            else:
                                df.loc[df['ID'] == id_editar, 'Estado Pago'] = "Abono"
                            
                            actualizar_db(df)
                            st.success("Pago registrado correctamente.")
                            time.sleep(1.5)
                            st.rerun()
                else:
                    st.success("Este cliente está PAZ Y SALVO.")

            # --- ACTUALIZACIÓN DE TELA ---
            with col_post2:
                st.markdown("#### 🧵 Gestión de Tela")
                st.write(f"Estado Entrega Inicial: {venta_gral['Entrega Tela']}")
                st.write(f"Metros Registrados: {venta_gral['Metros Tela']}")
                
                nuevos_metros = st.number_input("Adicionar nuevos metros entregados:", min_value=0.0, step=0.1, format="%.2f")
                
                if st.button("Registrar Entrega Tela"):
                    if nuevos_metros > 0:
                        fecha_ahora = datetime.now().strftime("%Y-%m-%d %H:%M")
                        
                        # Sumar metros
                        total_metros = venta_gral['Metros Tela'] + nuevos_metros
                        df.loc[df['ID'] == id_editar, 'Metros Tela'] = total_metros
                        
                        # Si estaba en "No", ahora es "Si"
                        df.loc[df['ID'] == id_editar, 'Entrega Tela'] = "Si"
                        
                        # Registrar Fecha Entrega Nueva (Concatenar si ya existe o crear nueva)
                        log_anterior = str(venta_gral['Fecha Entrega Nueva Tela']) if pd.notna(venta_gral['Fecha Entrega Nueva Tela']) else ""
                        nuevo_log = f"{log_anterior} | {fecha_ahora} (+{nuevos_metros}m)".strip(" | ")
                        
                        df.loc[df['ID'] == id_editar, 'Fecha Entrega Nueva Tela'] = nuevo_log
                        
                        # Si no tenía fecha inicial de entrega, se la ponemos
                        if pd.isna(venta_gral['Fecha Entrega Tela']) or venta_gral['Fecha Entrega Tela'] == "":
                             df.loc[df['ID'] == id_editar, 'Fecha Entrega Tela'] = fecha_ahora

                        actualizar_db(df)
                        st.success("Tela adicionada correctamente.")
                        time.sleep(1.5)
                        st.rerun()

    else:
        st.warning("No hay registros en la base de datos.")