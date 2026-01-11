# =============================================================================
# [tietokoneohjelma] Holonic Enterprise MAS – TektonAI
# 
# Tekijä:          Toni Miettinen
# Oppilaitos:      Metropolia Ammattikorkeakoulu, Helsinki, Suomi
# Vuosi:           2026
# Versio:          1.0
# Lisenssi:        MIT License
# Saatavuus:       https://github.com/Tekton-MAS/
# Viittaus:        Miettinen T. (2026). Moniagenttinen tekoälyarkkitehtuuri 
#                  pienyrityksen sähkö- ja automaatiojärjestelmien hallintaan.
#                  Insinöörityö, Metropolia AMK.
#
# Kuvaus: Streamlit-pohjainen reaaliaikainen käyttöliittymä ja dashboard 
#         holoniselle moniagenttijärjestelmälle (MAS). Visualisoi MARL-
#         koulutuksen (Q-learning) tuloksia reaaliaikaisena oppimiskäyränä 
#         (raakadata + liukuva 5-episodin keskiarvo MA5), näyttää keskeiset 
#         KPI-mittarit (nykyinen suorituskyky, kokonaisparannusprosentti, 
#         episodejen määrä, viimeisin päivitysaika), järjestelmän tilan 
#         (koulutetut mallit, konfiguraatio) sekä tukee teemavaihtoa (vaalea/
#         tumma). Lataa tulokset training_data.csv-tiedostosta, joka tuotetaan 
#         main_orchestrator.py:ssä. Sisältää automaattisen päivityksen 
#         15 sekunnin välein ja modernin glassmorphism-tyylin.
#         Osa opinnäytetyötä "Moniagenttinen tekoälyarkkitehtuuri...".
#
# Käynnistys: streamlit run dashboard.py
# =============================================================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import time
import sys
from typing import Optional

# --- Polku & config ---
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
from config import cfg

# === TEEMAT ===
THEME = st.sidebar.radio("Teema", ["Light", "Dark"], horizontal=True, index=0)
is_dark = THEME == "Dark"

# Värit
colors = {
    "bg": "#0E1117" if is_dark else "#F8FAFC",
    "surface": "#1A1F2C" if is_dark else "#FFFFFF",
    "surface2": "#262A36" if is_dark else "#F1F5F9",
    "primary": "#3B82F6",
    "green": "#10B981",
    "red": "#EF4444",
    "text": "#E2E8F0" if is_dark else "#1E293B",
    "text_secondary": "#94A3B8" if is_dark else "#64748B",
    "border": "#2D3748" if is_dark else "#E2E8F0",
    # Uusi: selkeä väri KPI-otsikoille (teeman mukaan)
    "kpi_label": "#000000" if not is_dark else "#E2E8F0",
}

# === Streamlit page config ===
st.set_page_config(
    page_title="TektonAI • Holonic Enterprise MAS",
    page_icon="Factory",
    layout="wide",
    initial_sidebar_state="expanded",
)

# === CSS (päivitetty) ===
st.markdown(f"""
<style>
    .main {{background: {colors['bg']};}}
    .block-container {{padding: 2rem;}}
    
    /* Glass-kortti */
    .glass-card {{
        background: rgba({'30,30,40' if is_dark else '255,255,255'}, 0.7);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: 20px;
        border: 1px solid {colors['border']};
        padding: 1.8rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.2);
        transition: all 0.4s ease;
    }}
    .glass-card:hover {{transform: translateY(-4px); box-shadow: 0 20px 40px rgba(0,0,0,0.3);}}

    /* Header */
    .header {{
        background: linear-gradient(135deg, {colors['primary']}, #6366F1);
        padding: 3rem 2rem;
        border-radius: 24px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 20px 40px rgba(59,130,246,0.3);
    }}

    /* KPI-tyylit */
    .kpi-big {{font-size: 3rem; font-weight: 800; margin: 0.5rem 0;}}
    .kpi-label-bold {{
        font-size: 1.15rem !important;
        font-weight: 900 !important;
        color: {colors['kpi_label']} !important;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        margin: 0 0 0.4rem 0 !important;
        opacity: 0.95;
    }}
</style>
""", unsafe_allow_html=True)

# === DATA ===
@st.cache_data(ttl=15, show_spinner="Päivitetään dataa...")
def load_data() -> Optional[pd.DataFrame]:
    path = cfg.RESULTS_DIR / "training_data.csv"
    if not path.exists():
        return None
    try:
        df = pd.read_csv(path)
        return df.dropna() if not df.empty else None
    except Exception:
        return None

df = load_data()

# === HEADER ===
st.markdown(f"""
<div class="header">
    <h1 style="margin:0; font-size:3.5rem; font-weight:900;">TektonAI</h1>
    <p style="margin:5px; font-size:1.5rem; opacity:0.95;">Holonic Enterprise MAS</p>
    <p style="margin:0; font-size:1.1rem;">Distributed Intelligent Manufacturing System</p>
</div>
""", unsafe_allow_html=True)

if df is None:
    st.markdown(f"<div class='glass-card'><h2>Odotetaan koulutustietoja...</h2><p>Käynnistä <code>python main_orchestrator.py</code></p></div>", unsafe_allow_html=True)
    st.stop()

# === KPI-KORTIT (teemakohtainen väri + bold) ===
latest = df["Reward_Smoothed"].iloc[-1]
start = df["Reward_Smoothed"].iloc[0]
improvement = latest - start
pct_change = (improvement / abs(start)) * 100 if start != 0 else 0

cols = st.columns(4)
kpis = [
    ("Nykyinen suorituskyky", f"{latest:.3f}", f"{improvement:+.3f}", improvement > 0),
    ("Kokonaisparannus", f"{pct_change:+.1f}%", None, pct_change > 0),
    ("Episodeja", f"{len(df):,}", None, True),
    ("Päivitetty", time.strftime("%H:%M:%S"), None, True),
]

for col, (label, value, delta, positive) in zip(cols, kpis):
    with col:
        st.markdown(f"""
        <div class="glass-card">
            <p class="kpi-label-bold">{label}</p>
            <h2 class="kpi-big" style="color:{colors['text']}; margin:0.8rem 0 0.5rem 0;">{value}</h2>
            {f'<p style="color: {"#10B981" if positive else "#EF4444"}; font-weight: bold; font-size:1.1rem; margin:0;">{delta}</p>' if delta else ''}
        </div>
        """, unsafe_allow_html=True)

# === PÄÄKÄYRÄ ===
st.markdown("### Oppimiskäyrä – Reaaliaikainen suorituskyky")

fig = go.Figure()
fig.add_trace(go.Scatter(x=df["Episode"], y=df["Reward_Raw"], mode="lines", name="Raakadata",
                         line=dict(color="#64748B", width=1.5), opacity=0.5))
fig.add_trace(go.Scatter(x=df["Episode"], y=df["Reward_Smoothed"], mode="lines", name="Trendi (MA5)",
                         line=dict(color=colors["green"], width=5), fill='tonexty', fillcolor="rgba(16,185,129,0.1)"))

fig.update_layout(
    height=650, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color=colors["text"]), hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                bgcolor="rgba(0,0,0,0.4)", bordercolor=colors["border"], borderwidth=1),
    xaxis=dict(title="Episode", gridcolor=colors["border"], zeroline=False),
    yaxis=dict(title="Reward per Step", gridcolor=colors["border"], zeroline=False),
    transition_duration=500
)

st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": True, "displaylogo": False})

# === SIDEBAR ===
with st.sidebar:
    st.markdown(f"<h2 style='color:{colors['primary']};'>TektonAI</h2>", unsafe_allow_html=True)
    st.markdown("**Järjestelmän tila**")
    models = len(list(cfg.MODELS_DIR.glob("*.pt")))
    st.markdown(f"**{'Active' if models else 'Waiting'}** • {models} mallia koulutettu")
    st.markdown("**Konfiguraatio**")
    st.caption(f"Koneita: **{cfg.num_machines}**")
    st.caption(f"MARL-episodeja: **{cfg.marl.episodes}**")
    st.caption(f"ANFIS-epochit: **{cfg.anfis.epochs}**")
    
    if st.button("Päivitä näkymä", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    st.markdown(f"<small style='color:{colors['text_secondary']};'>© 2025 TektonAI</small>", unsafe_allow_html=True)

# === AUTOMAATTINEN PÄIVITYS ===
if st.checkbox("Automaattipäivitys 15s", value=True):
    time.sleep(15)
    st.rerun()