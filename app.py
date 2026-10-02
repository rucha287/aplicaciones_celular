import numpy as np
from scipy.interpolate import interp1d
import streamlit as st
import plotly.graph_objects as go

# Configuración de la página web
st.set_page_config(page_title="Simulador de Consumo de Energía", layout="centered")

# Título de la app
st.title("📱 Simulador Interactiva: Cantidad de Apps vs. Duración de Batería")
st.write("Mueve la barra deslizante para cambiar la cantidad de aplicaciones abiertas y observa cómo se agota el tiempo de vida de la batería.")

# 1. Datos reales de la simulación (CANTIDAD)
x_puntos = np.array()
y_puntos = np.array()
estados = ["Reposo Total", "Uso Ligero", "Uso Moderado", "Uso Intenso", "Colapso del Sistema"]

# Modelo matemático de decaimiento
modelo_bateria = interp1d(x_puntos, y_puntos, kind='cubic', bounds_error=False, fill_value="extrapolate")

# Generar línea suave de fondo
x_suave = np.linspace(x_puntos.min(), x_puntos.max(), 300)
y_suave = np.clip(modelo_bateria(x_suave), 0.5, 24.0)

# --- PANEL INTERACTIVO ---
st.subheader("🎛️ Configuración del Celular")

# Slider para seleccionar la cantidad de apps
cantidad_apps = st.slider(
    label="Selecciona la cantidad de aplicaciones abiertas simultáneamente:",
    min_value=0,
    max_value=15,
    value=4, # Inicia en 4 apps
    step=1
)

# Calcular horas restantes en tiempo real
horas_calculadas = float(np.clip(modelo_bateria(cantidad_apps), 0.5, 24.0))

# Mostrar métricas en pantalla
col1, col2 = st.columns(2)
with col1:
    st.metric(label="Cantidad de Apps Abiertas", value=f"{cantidad_apps} apps")
with col2:
    st.metric(label="Duración Estimada", value=f"{horas_calculadas:.1f} horas")

# --- GRÁFICO INTERACTIVO ---
fig = go.Figure()

# Linea de tendencia
fig.add_trace(go.Scatter(
    x=x_suave, y=y_suave,
    mode='lines',
    name='Curva de Desgaste',
    line=dict(color='#d90429', width=2, dash='dash'),
    hoverinfo='skip'
))

# Puntos de referencia
fig.add_trace(go.Scatter(
    x=x_puntos, y=y_puntos,
    mode='markers',
    name='Puntos de Referencia',
    marker=dict(color='#2b2d42', size=10, symbol='circle-open'),
    text=estados,
    hovertemplate="<b>%{text}</b><br>Cantidad de Apps: %{x}<br>Duración: %{y} hrs<extra></extra>"
))

# Punto del usuario en tiempo real
fig.add_trace(go.Scatter(
    x=[cantidad_apps],
    y=[horas_calculadas],
    mode='markers+text',
    name='Tu Teléfono',
    marker=dict(color='#ef233c', size=16, symbol='square'),
    text=[f"{horas_calculadas:.1f} hrs"],
    textposition="top right",
    hovertemplate="<b>Estado Actual</b><br>Apps Abiertas: %{x}<br>Duración: %{y:.1f} hrs<extra></extra>"
))

# Formato estético
fig.update_layout(
    xaxis_title="Variable Independiente (X): Cantidad de Aplicaciones Abiertas",
    yaxis_title="Variable Dependiente (Y): Duración de la Batería (Horas)",
    xaxis=dict(range=[-0.5, 15.5], tickmode='linear', tick0=0, dtick=1),
    yaxis=dict(range=[-1, 26]),
    hovermode="closest",
    template="plotly_white",
    showlegend=True,
    legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99)
)

st.plotly_chart(fig, use_container_width=True)
