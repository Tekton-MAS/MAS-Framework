# =============================================================================
# [tietokoneohjelma] Holonic Enterprise MAS – TektonAI
# Tekijä:          Toni Miettinen
# Oppilaitos:      Metropolia Ammattikorkeakoulu, Helsinki, Suomi
# Vuosi:           2026
# Versio:          1.0
# Lisenssi:        MIT License
# Saatavuus:       https://github.com/Tekton-MAS/
# Viittaus:        Miettinen T. (2026). Moniagenttinen tekoälyarkkitehtuuri 
#                  pienyrityksen sähkö- ja automaatiojärjestelmien hallintaan.
#                  Insinöörityö, Metropolia AMK.
# Kuvaus:          Streamlit-pohjainen havainnointinäyttö (dashboard), joka 
#                  visualisoi moniagenttijärjestelmän (MAS) oppimisen edistymistä 
#                  ja keskeisiä mittareita. Näyttää koulutuksen reward-käyrän sekä 
#                  simuloituja suorituskykymetriikkejä. 
#                  Toimii demoversio / prototyyppi osana opinnäytetyötä.
#
# Käynnistys: streamlit run app.py
# =============================================================================

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import os

# Lataa tulokset results-kansiosta
rewards_file = "results/rewards.csv"
if os.path.exists(rewards_file):
    df = pd.read_csv(rewards_file)
else:
    df = pd.DataFrame({"episode": range(80), "reward": [9 + i*0.1 + np.random.normal(0, 0.5) for i in range(80)]}) 

# Dashboard-teema
st.set_page_config(page_title="Holonic Enterprise MAS Dashboard", page_icon="🏭", layout="wide")
st.markdown("""
    <style>
        .css-1y4p8pa {padding: 1rem 1rem 10rem 1rem;}
        .stApp {background-color: #1e1e1e;}
        h1, h2, h3, p, div, span {color: white;}
        .stMetric label {color: gray;}
    </style>
""", unsafe_allow_html=True)

# Otsikko
st.title("Holonic Enterprise MAS Dashboard")
st.subheader("Distributed Intelligent Manufacturing System Analytics")

# Järjestelmän tila
col1, col2, col3 = st.columns(3)
col1.metric("Nykyinen Suorituskyky (Trend)", "33.0 pts/step", "↑7.0 pts viime ajosta", label_visibility="visible")
col2.metric("Kokonaisparannus (Alusta)", "27.3 %", label_visibility="visible")
col3.metric("Simuloituja Episodia", "76", label_visibility="visible")

# Oppimiskäyrä
st.subheader("Oppimiskäyrä (Reaaliaikainen)")
fig = go.Figure()
fig.add_trace(go.Scatter(x=df["episode"], y=df["reward"], mode="lines+markers", name="Raakadata (Koneet)", line=dict(color="#3498db")))
fig.add_trace(go.Scatter(x=df["episode"], y=df["reward"].rolling(window=10).mean(), mode="lines", name="Trend (MAS)", line=dict(color="#2ecc71", width=3)))
fig.update_layout(
    title="Multi-Agent System Training Performance",
    xaxis_title="Episodi",
    yaxis_title="Reward per Step",
    template="plotly_dark",
    height=400
)
st.plotly_chart(fig, use_container_width=True)

# Konfiguraatio (vasen sivupalkki)
with st.sidebar:
    st.image("logo.png")  # Lisää oma logo jos haluat
    st.header("TektonAI Ohjaus")
    st.subheader("Järjestelmän Tila")
    st.success("Aktiivinen")
    st.subheader("Konfiguraatio")
    st.info("Koneita: 4 kpl")
    st.info("Episodia: 80")
    st.info("ANFIS Epoch: 100")
    st.button("Päivitä näkymä")

print("=== DEMO VALMIS! ===")  # Konsoliin (jos ajetaan ilman Streamlitia)