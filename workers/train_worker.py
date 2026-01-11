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
# =============================================================================
# Tiedosto:        train_anfis.py (tai vastaava)
#
# Kuvaus:          Rayn avulla hajautettu ANFIS-mallien koulutus yksittäisille 
#                  tuotantokoneille. Jokainen kone koulutetaan itsenäisesti 
#                  omalla konekohtaisella datasetillä (simuloitu fyysinen ero).
#                  Käytetään osana holonista moniagenttijärjestelmää (MAS),
#                  jossa jokainen "holoni" (koneagentti) oppii oman paikallisen
#                  säätömallinsa adaptiivisesti.
#
#                  Tämä moduuli vastaa konekohtaisten neuro-fuzzy-säätimien 
#                  (ANFIS) esikoulutuksesta / paikallisesta hienosäädöstä.
#
# Käynnistys-esimerkki:
#   ray.init()
#   futures = [train_anfis_remote.remote(i) for i in range(4)]
#   results = ray.get(futures)
# =============================================================================

import ray
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from models.anfis import ANFISNetwork
from config import cfg

@ray.remote(num_cpus=1)
def train_anfis_remote(machine_id: int):
    """
    Suorittaa ANFIS-koulutuksen itsenäisessä prosessissa.
    """
    try:
        # Alustus
        model = ANFISNetwork(hidden_layers=cfg.anfis.hidden_layers)
        optimizer = optim.Adam(model.parameters(), lr=cfg.anfis.lr)
        criterion = nn.MSELoss()

        # Generoi data (simulaatio)
        np.random.seed(42 + machine_id)
        n_samples = 500
        X = np.random.uniform(0, 1, (n_samples, 4)).astype(np.float32)
        
        # Konekohtainen bias (simuloi fyysisiä eroja)
        bias_map = {0: 0.18, 1: 0.02, 2: -0.10, 3: -0.25}
        bias = bias_map.get(machine_id, 0.0)
        
        noise = np.random.normal(0, 0.05, n_samples)
        y = np.clip(0.75 + bias + noise + 0.1 * np.sin(10 * X[:, 0]), 0.0, 1.0).astype(np.float32)

        # Muunnos tensoreiksi
        X_t = torch.from_numpy(X)
        y_t = torch.from_numpy(y)

        # Koulutuslooppi
        model.train()
        final_loss = 0.0
        for _ in range(cfg.anfis.epochs):
            optimizer.zero_grad()
            pred = model(X_t)
            loss = criterion(pred, y_t)
            loss.backward()
            optimizer.step()
            final_loss = loss.item()

        # Tallennus
        save_path = cfg.MODELS_DIR / f"anfis_machine_{machine_id}.pt"
        torch.save(model.state_dict(), save_path)
        
        return {
            "id": machine_id, 
            "status": "SUCCESS", 
            "loss": final_loss, 
            "path": str(save_path)
        }

    except Exception as e:
        return {"id": machine_id, "status": "ERROR", "error": str(e)}