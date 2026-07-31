import streamlit as st
import datetime
import time

st.set_page_config(page_title="Semáforo Arnedillo", page_icon="🚦", layout="centered")

st.title("🚦 Estado del Semáforo de Arnedillo")
st.markdown("Consulta en tiempo real el estado y tiempo de espera para cruzar la zona unidireccional.")

# Configuración de duraciones en segundos
DURACION_VERDE = 67    # 1 min 7 seg
DURACION_AMBAR = 3     # 3 seg
DURACION_ROJO = 590    # 9 min 50 seg
CICLO_TOTAL = DURACION_VERDE + DURACION_AMBAR + DURACION_ROJO  # 660 seg (11 min)

# Horas de referencia fijas
REF_ENTRADA = datetime.time(18, 0, 59)
REF_SALIDA = datetime.time(18, 6, 28)

# Selección de semáforo
opcion = st.radio(Dirección:, [Entrada a Arnedillo, Salida de Arnedillo], horizontal=True)

# Contenedor para refresco dinámico
placeholder = st.empty()

def calcular_estado(hora_referencia):
    ahora = datetime.datetime.now()
    inicio_ref = datetime.datetime.combine(ahora.date(), hora_referencia)
    
    # Calcular desfase respecto al inicio de ciclo más cercano
    diferencia_seg = (ahora - inicio_ref).total_seconds()
    segundos_en_ciclo = diferencia_seg % CICLO_TOTAL
    
    if segundos_en_ciclo < DURACION_VERDE:
        estado = "VERDE"
        restante = DURACION_VERDE - segundos_en_ciclo
        mensaje = "¡Puedes pasar! Tiempo restante de verde:"
        color = "#28a745"
    elif segundos_en_ciclo < (DURACION_VERDE + DURACION_AMBAR):
        estado = "ÁMBAR"
        restante = (DURACION_VERDE + DURACION_AMBAR) - segundos_en_ciclo
        mensaje = "Precaución / Deteniéndose. Tiempo restante de ámbar:"
        color = "#ffc107"
    else:
        estado = "ROJO"
        restante = CICLO_TOTAL - segundos_en_ciclo
        mensaje = "Esperando verde. Tiempo restante de espera:"
        color = "#dc3545"
        
    return estado, int(restante), mensaje, color

# Bucle de actualización automática
hora_ref = REF_ENTRADA if opcion == "Entrada a Arnedillo" else REF_SALIDA

with placeholder.container():
    estado, restante, mensaje, color = calcular_estado(hora_ref)
    
    mins = restante // 60
    segs = restante % 60
    
    st.markdown(
        f"""
        <div style="background-color: {color}; padding: 25px; border-radius: 12px; text-align: center; color: white;">
            <h1 style="margin: 0; font-size: 3em;">{estado}</h1>
            <p style="font-size: 1.2em; margin-top: 10px;">{mensaje}</p>
            <h2 style="margin: 0; font-size: 2.5em;">{mins:02d}:{segs:02d}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.caption(f"Hora actual: {datetime.datetime.now().strftime('%H:%M:%S')}")

# Auto-refresco cada segundo
time.sleep(1)
st.rerun()
