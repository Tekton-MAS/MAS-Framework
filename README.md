**Holonic Enterprise MAS – TektonAI**
Moniagenttinen tekoälyarkkitehtuuri pienyrityksen sähkö- ja automaatiojärjestelmien hallintaan

Tämä projekti kehittää holoniseen (holonic) moniagenttijärjestelmään (MAS) perustuvaa älykästä ohjaus- ja optimointiratkaisua pienille ja keskisuurille valmistusyrityksille. Järjestelmä yhdistää multi-agent reinforcement learning (MARL) -menetelmiä, ANFIS-neuro-fuzzy-säätimiä sekä hajautettua laskentaa (Ray) tavoitteenaan parantaa tuotantoprosessien tehokkuutta, adaptiivisuutta ja vikasietoisuutta.

Projekti on osa Toni Miettisen insinöörityötä Metropolia Ammattikorkeakoulussa (valmistuu 2026).

**Ominaisuudet (nykyinen tila – prototyyppivaihe)**
• Hajautettu ANFIS-koulutus yksittäisille koneagenteille (Ray)
• Streamlit-pohjainen dashboard oppimiskäyrien ja suorituskykymetriikoiden visualisointiin
• Simuloitu data + konekohtaiset fyysiset erot (bias + noise)
• Modulaarinen rakenne → helppo laajentaa oikeaan MARL-koulutukseen

**Tulevaisuudessa (suunniteltu jatkokehitys)**
• Täysi MARL-koulutus usealle agentille samanaikaisesti
• Integraatio oikeisiin automaatiojärjestelmiin (PLC, OPC UA)
• Reaaliaikainen päätöksenteko ja dynaaminen konfiguraatio
• Laajennettu holoninen rakenne itseorganisoituviin tuotantojärjestelmiin

**Teknologiapino**
• Python 3.10+
• Ray – hajautettu laskenta & parallel training
• PyTorch – custom ANFIS-implementaatio
• Streamlit – käyttöliittymä & visualisointi
• Plotly – interaktiiviset käyrät
• Pandas, NumPy

**Asennusohjeet**
1. Kloonaa repositorio:
git clone https://github.com/Tekton-MAS/MAS-Framework.git

2. Siirry projektikansioon:
cd MAS-Framework

3. Luo virtuaaliympäristö:
python -m venv .venv

4. Aktivoi ympäristö:
Windows
.venv\Scripts\activate

5. Linux/macOS
source .venv/bin/activate

5. Asenna riippuvuudet:
pip install -r requirements.txt

Tyypillisiä riippuvuuksia:
ray, torch, numpy, pandas, streamlit, plotly

**Konfiguraatio**
Asetukset löytyvät tiedostoista:
• config.py
• config.yaml

**ANFIS-mallien koulutus**
Peruskäynnistys
python src/train_anfis.py

**Hajautettu koulutus neljälle koneelle (Ray)**
python -c "import ray; ray.init();
from src.train_anfis import train_anfis_remote;
futures = [train_anfis_remote.remote(i) for i in range(4)];
print(ray.get(futures))"
Mallien tulokset tallentuvat models/-kansioon.

**Dashboard**
Käynnistä Streamlit-sovellus:

bash
streamlit run src/app.py

**Avaa selaimessa:**

Code
http://localhost:8501

**Projektin rakenne**
Code
MAS-Framework/
│
├── src/
│   ├── app.py              # Streamlit-dashboard
│   ├── train_anfis.py      # ANFIS-koulutus
│   ├── models/
│   │   └── anfis.py        # ANFIS-toteutus
│   └── config.py           # Asetukset
│
├── models/                 # Tallennetut mallit
├── results/                # Tulokset ja lokit
└── requirements.txt

**Lisenssi**
**MIT License**

Tekijä: **Toni Miettinen**, Metropolia Ammattikorkeakoulu, 2026
Insinöörityö:
Moniagenttinen tekoälyarkkitehtuuri pienyrityksen sähkö- ja automaatiojärjestelmien hallintaan
