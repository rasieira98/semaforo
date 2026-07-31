import streamlit as st
import datetime
import time

# Configuración de la página
st.set_page_config(
    page_title="Semáforo Arnedillo",
    page_icon="🚦",
    layout="centered"
)

# Estilos CSS personalizados para tarjetas, luces y sombras
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
    }
    .traffic-box {
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
    }
    .traffic-light {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        margin: 0 auto 15px auto;
        box-shadow: 0 0 20px rgba(0,0,0,0.5);
    }
    .green-glow {
        background-color: #2ea043;
        box-shadow: 0 0 30px #2ea043;
    }
    .amber-glow {
        background-color: #d29922;
        box-shadow: 0 0 30px #d29922;
    }
    .red-glow {
        background-color: #f85149;
        box-shadow: 0 0 30px #f85149;
    }
    </style>
""", unsafe_allow_html=True)

# Título de la aplicación
st.title("🚦 Control del Semáforo de Arnedillo")
st.caption("Paso alternativo unidireccional en tiempo real")

# Configuración del ciclo (en segundos)
DURACION_VERDE = 67    # 1 min 7 seg
DURACION_AMBAR = 3     # 3 seg
DURACION_ROJO = 590    # 9 min 50 seg
CICLO_TOTAL = DURACION_VERDE + DURACION_AMBAR + DURACION_ROJO

# Referencias horarias
REF_ENTRADA = datetime.time(18, 0, 59)
REF_SALIDA = datetime.time(18, 6, 28)

# Selección de sentido
opcion = st.segmented_control(
    "Selecciona el sentido de circulación:",
    options=["Entrada a Arnedillo", "Salida de Arnedillo"],
    default="Entrada a Arnedillo"
)

def calcular_estado(hora_referencia):
    ahora = datetime.datetime.now()
    inicio_ref = datetime.datetime.combine(ahora.date(), hora_referencia)
    
    diferencia_seg = (ahora - inicio_ref).total_seconds()
    segundos_en_ciclo = diferencia_seg % CICLO_TOTAL
    
    if segundos_en_ciclo < DURACION_VERDE:
        estado = "VERDE"
        restante = DURACION_VERDE - segundos_en_ciclo
        duracion_fase = DURACION_VERDE
        glow = "green-glow"
        bg_color = "rgba(46, 160, 67, 0.15)"
        border_color = "#2ea043"
        mensaje = "🟢 VÍA LIBRE: Puedes cruzar el tramo con seguridad."
    elif segundos_en_ciclo < (DURACION_VERDE + DURACION_AMBAR):
        estado = "ÁMBAR"
        restante = (DURACION_VERDE + DURACION_AMBAR) - segundos_en_ciclo
        duracion_fase = DURACION_AMBAR
        glow = "amber-glow"
        bg_color = "rgba(210, 153, 34, 0.15)"
        border_color = "#d29922"
        mensaje = "⚠️ PRECAUCIÓN: Semáforo cambiando a rojo. Detente si es seguro."
    else:
        estado = "ROJO"
        restante = CICLO_TOTAL - segundos_en_ciclo
        duracion_fase = DURACION_ROJO
        glow = "red-glow"
        bg_color = "rgba(248, 81, 73, 0.15)"
        border_color = "#f85149"
        mensaje = "🔴 ESPERA: El sentido contrario tiene la vía libre."
        
    progreso = max(0.0, min(1.0, 1.0 - (restante / duracion_fase)))
    return estado, int(restante), glow, bg_color, border_color, mensaje, progreso

# Seleccionar la hora de referencia
hora_ref = REF_ENTRADA if opcion == "Entrada a Arnedillo" else REF_SALIDA

# Contenedor dinámico
placeholder = st.empty()

with placeholder.container():
    estado, restante, glow, bg_color, border_color, mensaje, progreso = calcular_estado(hora_ref)
    
    mins = restante // 60
    segs = restante % 60
    tiempo_formateado = f"{mins:02d}:{segs:02d}"
    
    # Tarjeta Principal del Semáforo
    st.markdown(
        f"""
        <div class="traffic-box" style="background-color: {bg_color}; border: 2px solid {border_color};">
            <div class="traffic-light {glow}"></div>
            <h1 style="margin: 0; font-size: 2.8em; letter-spacing: 2px;">{estado}</h1>
            <h2 style="margin: 10px 0 0 0; font-size: 3.2em; font-family: monospace;">{tiempo_formateado}</h2>
            <p style="margin-top: 5px; opacity: 0.8; font-size: 0.9em;">TIEMPO RESTANTE EN ESTE ESTADO</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Barra de progreso del estado actual
    st.progress(progreso)
    
    # Cuadro informativo
    if estado == "VERDE":
        st.success(mensaje)
    elif estado == "ÁMBAR":
        st.warning(mensaje)
    else:
        st.error(mensaje)
        
    # Información adicional
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="🕒 Hora Actual", value=datetime.datetime.now().strftime("%H:%M:%S"))
    with col2:
        st.metric(label="🔄 Ciclo Completo", value="11 min (660s)")

# Actualización continua
time.sleep(1)
st.rerun()
