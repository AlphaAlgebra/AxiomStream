import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

st.set_page_config(layout="wide")

# 🧠 HYPER-SPACE MANIFOLD ENGINE
def generate_hyper_manifold(t, perturbation_scale=0.15):
    p, q = 3, 7
    r = 4.0 + 2.0 * np.cos(q * t)
    x = r * np.cos(p * t)
    y = r * np.sin(p * t)
    z = 2.0 * np.sin(q * t)
    
    np.random.seed(1337)
    x += np.random.normal(0, perturbation_scale, size=t.shape)
    y += np.random.normal(0, perturbation_scale, size=t.shape)
    z += np.random.normal(0, perturbation_scale, size=t.shape)
    
    scalar_field = np.sin(x) * np.cos(y) * np.sin(z)
    return x, y, z, scalar_field

# 🕹️ SIDEBAR CONTROLS
st.sidebar.markdown("### ⚡ QUANTUM MATRIX CONTROL")
density = st.sidebar.slider("PARTICLE FIELD DENSITY", 500, 5000, 2500, step=250)
noise = st.sidebar.slider("ANOMALOUS DISTORTION SCALE", 0.0, 1.0, 0.2, step=0.05)
spin_speed = st.sidebar.slider("MATRIX REVOLUTION SPEED", 0.0, 5.0, 1.5, step=0.1)

t_vector = np.linspace(0, 2 * np.pi, density)
X, Y, Z, color_map = generate_hyper_manifold(t_vector, perturbation_scale=noise)

st.markdown("## 🔮 AXIOMSTREAM // REAL-TIME TOPOLOGY HARVESTER")

if "mesh_theta" not in st.session_state:
    st.session_state.mesh_theta = 0.0

st.session_state.mesh_theta += (spin_speed * 0.05)
camera_x = 1.5 * np.cos(st.session_state.mesh_theta)
camera_y = 1.5 * np.sin(st.session_state.mesh_theta)

fig = go.Figure(data=[go.Scatter3d(
    x=X, y=Y, z=Z,
    mode='markers',
    marker=dict(
        size=4,
        color=color_map,
        colorscale=[
            [0.0, '#00f3ff'],  # Fluorescent Cyan
            [0.5, '#bd00ff'],  # Antimatter Purple
            [1.0, '#ff007f']   # High-Voltage Magenta
        ],
        opacity=0.9,
        line=dict(width=0)
    ),
    hovertemplate="<b>🌌 NODE ENCODING</b><br>X: %{x:.4f}<br>Y: %{y:.4f}<br>Z: %{z:.4f}<extra></extra>"
)])

fig.update_layout(
    template='plotly_dark',
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(l=0, r=0, b=0, t=0),
    scene=dict(
        xaxis=dict(gridcolor='rgba(0, 243, 255, 0.08)', zerolinecolor='rgba(255, 255, 255, 0.1)'),
        yaxis=dict(gridcolor='rgba(0, 243, 255, 0.08)', zerolinecolor='rgba(255, 255, 255, 0.1)'),
        zaxis=dict(gridcolor='rgba(0, 243, 255, 0.08)', zerolinecolor='rgba(255, 255, 255, 0.1)'),
        camera=dict(
            eye=dict(x=camera_x, y=camera_y, z=1.0),
            up=dict(x=0, y=0, z=1)
        ),
        aspectmode='cube'
    ),
    height=700
)

plot_placeholder = st.empty()
plot_placeholder.plotly_chart(fig, use_container_width=True)

if spin_speed > 0:
    time.sleep(0.05)
    st.rerun()
