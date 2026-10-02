import numpy as np
from scipy.interpolate import interp1d
import streamlit as st
import plotly.graph_objects as go

# Configuración de la página web
st.set_page_config(page_title="Simulador de Consumo Dinámico", layout="centered")

# Título de la app
st.title("📱 Simulador en Tiempo Real: Desgaste de Batería")
st.write("Mueve la barra deslizante hacia la derecha para ir descubriendo y dibujando la curva de consumo a medida que agregas aplicaciones.")

# 1. Datos reales de la simulación (CANTIDAD)
x_puntos_totales = np.array([0, 2, 5, 10, 15])
y_puntos_totales = np.array([24.0, 12.0, 5.5, 2.1, 0.8])
estados_totales = ["Reposo Total", "Uso Ligero", "Uso Moderado", "Uso Intenso", "Colapso del Sistema"]

# Modelo matemático completo de fondo
modelo_bateria = interp1d(x_puntos_totales, y_puntos_totales, kind='cubic', bounds_error=False, fill_value="extrapolate")

# --- PANEL INTERACTIVO ---
st.subheader("🎛️ Configuración del Celular")

# Slider para seleccionar la cantidad de apps
cantidad_apps = st.slider(
    label="Incrementa la cantidad de aplicaciones abiertas simultáneamente:",
    min_value=0,
    max_value=15,
    value=0, # Iniciamos en cero para que descubran todo desde el principio
    step=1
)

# Calcular horas restantes actuales
horas_calculadas = float(np.clip(modelo_bateria(cantidad_apps), 0.5, 24.0))

# Mostrar métricas en pantalla
col1, col2 = st.columns(2)
with col1:
    st.metric(label="Cantidad de Apps Abiertas", value=f"{cantidad_apps} apps")
with col2:
    st.metric(label="Duración de la Batería", value=f"{horas_calculadas:.1f} horas")

# --- FILTRADO EN TIEMPO REAL (Aquí ocurre la magia) ---
# Creamos la línea suave SOLO hasta la cantidad de apps seleccionada por el usuario
x_suave_dinamica = np.linspace(0, cantidad_apps, max(2, cantidad_apps * 10))
y_suave_dinamica = np.clip(modelo_bateria(x_suave_dinamica), 0.5, 24.0)

# Filtramos los puntos de referencia para que solo aparezcan si el usuario ya los pasó
mascara_puntos = x_puntos_totales <= cantidad_apps
x_puntos_visibles = x_puntos_totales[mascara_puntos]
y_puntos_visibles = y_puntos_totales[mascara_puntos]
estados_visibles = [estados_totales[i] for i, visible in enumerate(mascara_puntos) if visible]

# --- GRÁFICO DINÁMICO ---
fig = go.Figure()

# 1. Línea de tendencia que se dibuja en tiempo real (solo hasta el valor actual)
if cantidad_apps > 0:
    fig.add_trace(go.Scatter(
        x=x_suave_dinamica, y=y_suave_dinamica,
        mode='lines',
        name='Curva Revelada',
        line=dict(color='#d90429', width=3),
        hoverinfo='skip'
    ))

# 2. Puntos de referencia anatómicos/físicos que van apareciendo
if len(x_puntos_visibles) > 0:
    fig.add_trace(go.Scatter(
        x=x_puntos_visibles, y=y_puntos_visibles,
        mode='markers',
        name='Hitos de Consumo',
        marker=dict(color='#2b2d42', size=10, symbol='circle'),
        text=estados_visibles,
        hovertemplate="<b>%{text}</b><br>Cantidad de Apps: %{x}<br>Duración: %{y} hrs<extra></extra>"
    ))

# 3. Marcador del estado actual del paciente/teléfono
fig.add_trace(go.Scatter(
    x=[cantidad_apps],
    y=[horas_calculadas],
    mode='markers+text',
    name='Estado Actual',
    marker=dict(color='#ef233c', size=16, symbol='square'),
    text=[f"{horas_calculadas:.1f} hrs"],
    textposition="top right",
    hovertemplate="<b>Tu Teléfono</b><br>Apps: %{x}<br>Duración: %{y:.1f} hrs<extra></extra>"
))

# Formato estético fijo para que el plano cartesiano no se mueva
fig.update_layout(
    xaxis_title="Variable Independiente (X): Cantidad de Aplicaciones Abiertas",
    yaxis_title="Variable Dependiente (Y): Duración de la Batería (Horas)",
    xaxis=dict(range=[-0.5, 15.5], tickmode='linear', tick0=0, dtick=1, fixedrange=True),
    yaxis=dict(range=[-1, 26], fixedrange=True),
    hovermode="closest",
    template="plotly_white",
    showlegend=False
)

st.plotly_chart(fig, use_container_width=True)
