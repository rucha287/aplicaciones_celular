import numpy as np
from scipy.interpolate import interp1d
import streamlit as st
import plotly.graph_objects as go

# Configuración de la página web
st.set_page_config(page_title="Simulador de Agudeza Visual", layout="centered")

# Título y encabezado médico
st.title("👁️ Simulador Clínico Interactiva: Concentración vs. Visión")
st.write("Mueve la barra deslizante de abajo para simular una concentración de conos personalizada y evaluar la agudeza visual resultante.")

# 1. Datos reales de referencia anatómica
x_puntos = np.array([5000, 15000, 40000, 80000, 150000])
y_puntos = np.array([5, 15, 40, 70, 100])
zonas = ["Periferia Lejana", "Periferia Media", "Mácula Externa", "Fóvea (Borde)", "Fóvea Central"]

# Crear el modelo matemático (interpolación) para predecir cualquier valor intermedio
modelo_vision = interp1d(x_puntos, y_puntos, kind='cubic', bounds_error=False, fill_value="extrapolate")

# Generar la línea continua suave de fondo
x_suave = np.linspace(x_puntos.min(), x_puntos.max(), 300)
y_suave = np.clip(modelo_vision(x_suave), 0, 100) # Evitamos que matemáticamente supere el 100%

# --- ELEMENTO INTERACTIVO: BARRA DESLIZANTE (SLIDER) ---
st.subheader("🎛️ Panel de Simulación Clínica")

# Creamos el slider en Streamlit
concentracion_usuario = st.slider(
    label="Selecciona la Concentración de Conos del Paciente (células / mm²):",
    min_value=5000,
    max_value=150000,
    value=50000, # Valor con el que inicia la página
    step=1000,
    format="%d"
)

# Calcular la agudeza visual en tiempo real usando el modelo matemático
# Usamos np.clip para que por efectos de la curva no baje de 0 ni suba de 100
agudeza_calculada = float(np.clip(modelo_vision(concentracion_usuario), 0, 100))

# Mostrar los resultados clínicos en tarjetas llamativas (Métricas)
col1, col2 = st.columns(2)
with col1:
    st.metric(label="Concentración Seleccionada", value=f"{concentracion_usuario:,} cél/mm²")
with col2:
    st.metric(label="Agudeza Visual Estimada", value=f"{agudeza_calculada:.1f} %")

# --- CONSTRUCCIÓN DEL GRÁFICO INTERACTIVO ---
fig = go.Figure()

# 1. Línea de tendencia fisiológica de fondo
fig.add_trace(go.Scatter(
    x=x_suave, y=y_suave,
    mode='lines',
    name='Curva Fisiológica',
    line=dict(color='#0077b6', width=2, dash='dash'),
    hoverinfo='skip'
))

# 2. Puntos anatómicos reales de referencia
fig.add_trace(go.Scatter(
    x=x_puntos, y=y_puntos,
    mode='markers',
    name='Puntos de Referencia',
    marker=dict(color='#4a4a4a', size=10, symbol='circle-open'),
    text=zonas,
    hovertemplate="<b>%{text}</b><br>Concentración: %{x:,} cél/mm²<br>Agudeza: %{y}%<extra></extra>"
))

# 3. EL PUNTO DINÁMICO (El que se mueve con la barra deslizante)
fig.add_trace(go.Scatter(
    x=[concentracion_usuario],
    y=[agudeza_calculada],
    mode='markers+text',
    name='Paciente Simulado',
    marker=dict(color='#e63946', size=16, symbol='diamond'),
    text=[f"Tu Paciente ({agudeza_calculada:.1f}%)"],
    textposition="top left",
    hovertemplate="<b>Paciente Simulado</b><br>Concentración: %{x:,} cél/mm²<br>Agudeza: %{y:.1f}%<extra></extra>"
))

# Configuración estética del gráfico
fig.update_layout(
    xaxis_title="Variable Independiente (X): Concentración de Conos (células / mm²)",
    yaxis_title="Variable Dependiente (Y): Agudeza Visual (%)",
    xaxis=dict(range=[0, 160000], tickformat=","),
    yaxis=dict(range=[0, 110]),
    hovermode="closest",
    template="plotly_white",
    showlegend=True,
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
)

# Enviar el gráfico dinámico a Streamlit
st.plotly_chart(fig, use_container_width=True)
