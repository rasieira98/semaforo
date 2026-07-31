import streamlit as st
import datetime
import time
from zoneinfo import ZoneInfo
import requests
import json
import base64

# ---------------------------------------------------------
# 1. ZONA HORARIA Y CONFIGURACIÓN DE LA PÁGINA (NAVEGADOR)
# ---------------------------------------------------------
TZ_MADRID = ZoneInfo("Europe/Madrid")

# Configuración de la pestaña del navegador
st.set_page_config(
    page_title="Paso Alternativo LR-115 | Arnedillo", # Nombre en la pestaña del navegador
    page_icon="🚗",                                    # Icono/Emoji en la pestaña
    layout="centered"
)

# ---------------------------------------------------------
# 2. CONFIGURACIÓN PWA (NOMBRE E ICONO DE LA APP EN MÓVIL)
# ---------------------------------------------------------
# Nombre e icono que aparecerán cuando el usuario instale la App en su teléfono
APP_NOMBRE_COMPLETO = "Tráfico Arnedillo"
APP_NOMBRE_CORTO = "Paso Arnedillo"

# Puedes cambiar esta URL por cualquier imagen PNG propia (ej. alojada en GitHub o Imgur)
APP_ICONO_URL = "https://em-content.zobj.net/source/apple/391/traffic-light_1f8a5.png"

manifest_data = {
    "name": APP_NOMBRE_COMPLETO,
    "short_name": APP_NOMBRE_CORTO,
    "start_url": "/",
    "display": "standalone",
    "background_color": "#0e1117",
    "theme_color": "#0e1117",
    "icons": [
        {
            "src": APP_ICONO_URL,
            "sizes": "192x192",
            "type": "image/png"
        },
        {
            "src": APP_ICONO_URL,
            "sizes": "512x512",
            "type": "image/png"
        }
    ]
}

# Codificar manifest en Base64 para inyección HTML
manifest_base64 = base64.b64encode(json.dumps(manifest_data).encode()).decode()

# ---------------------------------------------------------
# 3. ESTILOS CSS PERSONALIZADOS + META ETIQUETAS PWA
# ---------------------------------------------------------
st.markdown(f"""
    <!-- Metatags para compatibilidad PWA en iOS y Android -->
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="{APP_NOMBRE_CORTO}">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="theme-color" content="#0e1117">
    <link rel="apple-touch-icon" href="{APP_ICONO_URL}">
    <link rel="manifest" href="data:application/json;base64,{manifest_base64}">

    <style>
    .stApp {{
        background-color: #0e1117;
    }}
    .traffic-box {{
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
    }}
    .traffic-light {{
        width: 80px;
        height: 80px;
        border-radius: 50%;
        margin: 0 auto 15px auto;
        box-shadow: 0 0 20px rgba(0,0,0,0.5);
    }}
    .green-glow {{
        background-color: #2ea043;
        box-shadow: 0 0 30px #2ea043;
    }}
    .amber-glow {{
        background-color: #d29922;
        box-shadow: 0 0 30px #d29922;
    }}
    .red-glow {{
        background-color: #f85149;
        box-shadow: 0 0 30px #f85149;
    }}
    
    /* Animación de parpadeo cuando quedan <= 10 segundos */
    @keyframes warning-blink {{
        0% {{ opacity: 1; transform: scale(1); }}
        50% {{ opacity: 0.5; transform: scale(0.98); }}
        100% {{ opacity: 1; transform: scale(1); }}
    }}
    .blink-alert {{
        animation: warning-blink 1s infinite;
    }}

    /* Contenedor del selector centrado */
    div[data-testid="stSegmentedControlContainer"] {{
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
        margin-bottom: 25px !important;
    }}

    /* Selector Entrada/Salida grande */
    div[data-testid="stSegmentedControl"] {{
        width: 100% !important;
        max-width: 600px !important;
    }}

    div[data-testid="stSegmentedControl"] button {{
        font-size: 1.4rem !important;
        padding: 16px 28px !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
    }}
    
    /* Barra de progreso personalizada más grande */
    .stProgress > div > div > div > div {{
        height: 18px !important;
        border-radius: 9px !important;
    }}
    .progress-label {{
        display: flex;
        justify-content: space-between;
        font-size: 0.95rem;
        font-weight: 600;
        margin-bottom: 4px;
        opacity: 0.9;
    }}
    
    .centered-title {{
        text-align: center;
        margin-bottom: 15px;
    }}
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. TÍTULO Y GUÍA DE INSTALACIÓN
# ---------------------------------------------------------
st.title("🚦 Control del Semáforo de Arnedillo")
st.caption("Paso alternativo unidireccional en tiempo real")

with st.expander("📲 ¿Cómo instalar esta App en tu teléfono?"):
    st.markdown("""
    **En iPhone / iPad (Safari):**
    1. Pulsa el botón **Compartir** (el icono del cuadrado con la flecha hacia arriba ⎋).
    2. Selecciona **"Añadir a la pantalla de inicio"** ➕.

    **En Android (Chrome / Edge):**
    1. Pulsa los **3 puntos** de la esquina superior derecha ⋮.
    2. Selecciona **"Añadir a la pantalla de inicio"** o **"Instalar aplicación"** 📲.
    """)

# ---------------------------------------------------------
# 5. CONFIGURACIÓN DEL CICLO Y TIEMPOS
# ---------------------------------------------------------
DURACION_VERDE = 67    # 1 min 7 seg
DURACION_AMBAR = 3     # 3 seg
DURACION_ROJO = 590    # 9 min 50 seg
CICLO_TOTAL = DURACION_VERDE + DURACION_AMBAR + DURACION_ROJO

# Referencias horarias
REF_ENTRADA = datetime.time(18, 0, 59)
REF_SALIDA = datetime.time(18, 6, 28)

# API del clima
@st.cache_data(ttl=600)
def obtener_clima_arnedillo():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=42.2136&longitude=-2.2356&current=temperature_2m,weather_code&timezone=Europe%2FBerlin"
        res = requests.get(url, timeout=3).json()
        temp = round(res["current"]["temperature_2m"])
        code = res["current"]["weather_code"]
        
        clima_dict = {
            0: ("☀️", "Despejado"),
            1: ("🌤️", "Casi despejado"),
            2: ("⛅", "Parcialmente nublado"),
            3: ("☁️", "Nublado"),
            45: ("🌫️", "Niebla"), 48: ("🌫️", "Cencellada"),
            51: ("🌧️", "Llovizna suave"), 53: ("🌧️", "Llovizna"), 55: ("🌧️", "Llovizna intensa"),
            61: ("🌧️", "Lluvia ligera"), 63: ("🌧️", "Lluvia moderada"), 65: ("🌧️", "Lluvia fuerte"),
            71: ("❄️", "Nieve ligera"), 73: ("❄️", "Nieve moderada"), 75: ("❄️", "Nieve fuerte"),
            80: ("🌦️", "Chubascos"), 81: ("🌦️", "Chubascos fuertes"),
            95: ("⛈️", "Tormenta")
        }
        icono, desc = clima_dict.get(code, ("🌡️", "Variable"))
        return f"{icono} {temp}°C ({desc})"
    except Exception:
        return "🌡️ No disponible"

# ---------------------------------------------------------
# 6. SELECTOR CENTRADO Y CÁLCULO DE ESTADO
# ---------------------------------------------------------
st.markdown("<h3 class='centered-title'>Selecciona el sentido de circulación:</h3>", unsafe_allow_html=True)

opcion = st.segmented_control(
    "Selecciona el sentido de circulación:",
    options=["Entrada a Arnedillo", "Salida de Arnedillo"],
    default="Entrada a Arnedillo",
    label_visibility="collapsed"
)

def calcular_estado(hora_referencia):
    ahora = datetime.datetime.now(TZ_MADRID)
    inicio_ref = datetime.datetime.combine(ahora.date(), hora_referencia).replace(tzinfo=TZ_MADRID)
    
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
    return estado, int(restante), glow, bg_color, border_color, mensaje, progreso, ahora

hora_ref = REF_ENTRADA if opcion == "Entrada a Arnedillo" else REF_SALIDA

# ---------------------------------------------------------
# 7. RENDERIZADO DINÁMICO DE LA INTERFAZ
# ---------------------------------------------------------
placeholder = st.empty()

with placeholder.container():
    estado, restante, glow, bg_color, border_color, mensaje, progreso, ahora_madrid = calcular_estado(hora_ref)
    
    mins = restante // 60
    segs = restante % 60
    tiempo_formateado = f"{mins:02d}:{segs:02d}"
    porcentaje_texto = f"{int(progreso * 100)}%"
    
    # Hora exacta del próximo cambio de estado
    hora_proximo_cambio = ahora_madrid + datetime.timedelta(seconds=restante)
    
    # Clase CSS para parpadeo cuando queden <= 10s
    clase_animacion = "blink-alert" if restante <= 10 else ""
    
    # Alerta flotante toast
    if estado == "ROJO" and restante <= 10:
        st.toast(f"🔔 ¡Atención! Semáforo cambiando a VERDE en {restante}s", icon="🟢")
    elif estado == "VERDE" and restante <= 10:
        st.toast(f"⚠️ El semáforo se pondrá en ROJO en {restante}s", icon="🔴")
    
    # Tarjeta Principal
    st.markdown(
        f"""
        <div class="traffic-box {clase_animacion}" style="background-color: {bg_color}; border: 2px solid {border_color};">
            <div class="traffic-light {glow}"></div>
            <h1 style="margin: 0; font-size: 2.8em; letter-spacing: 2px;">{estado}</h1>
            <h2 style="margin: 10px 0 0 0; font-size: 3.2em; font-family: monospace;">{tiempo_formateado}</h2>
            <p style="margin-top: 5px; opacity: 0.8; font-size: 0.9em;">TIEMPO RESTANTE EN ESTE ESTADO</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Barra de progreso
    st.markdown(
        f"""
        <div class="progress-label">
            <span>Progreso de la fase actual</span>
            <span>{porcentaje_texto}</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.progress(progreso)
    
    # Mensaje de estado
    if estado == "VERDE":
        st.success(mensaje)
    elif estado == "ÁMBAR":
        st.warning(mensaje)
    else:
        st.error(mensaje)
        
    # Métricas inferiores
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            label="🕒 Hora Local", 
            value=ahora_madrid.strftime("%H:%M:%S")
        )
    with col2:
        st.metric(
            label="⏱️ Próximo Cambio", 
            value=hora_proximo_cambio.strftime("%H:%M:%S")
        )
    with col3:
        st.metric(
            label="🏔️ Clima Arnedillo", 
            value=obtener_clima_arnedillo()
        )

# Actualización en bucle cada 1 segundo
time.sleep(1)
st.rerun()
