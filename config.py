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
# Kuvaus:          Keskitetty konfiguraatiomoduuli (config.py) koko TektonAI-järjestelmälle.
#                  Käyttää Pydantic-malleja validoituihin asetuksiin: määrittelee ANFIS-
#                  mallin hyperparametrit (epochit, oppimisnopeus, piilokerrokset), MARL-
#                  koulutuksen parametrit (episodejen määrä, alpha, gamma, epsilon), 
#                  järjestelmän yleiset asetukset (koneiden lukumäärä) sekä hakemistopolut 
#                  (results/, models/). Luo automaattisesti tarvittavat kansiot ja 
#                  alustaa globaalin konfiguraatio-olion cfg, jota käyttävät orkestrointi, 
#                  simulaatio, koulutus ja dashboard. 
#                  Osa opinnäytetyötä "Moniagenttinen tekoälyarkkitehtuuri...".
#
# Käyttö:          Tuodaan muissa moduuleissa: from config import cfg
# =============================================================================

import os
from pathlib import Path
from pydantic import BaseModel, Field

class AnfisConfig(BaseModel):
    epochs: int = 100
    lr: float = 0.007
    hidden_layers: list[int] = [32, 16]

class MarlConfig(BaseModel):
    episodes: int = 80
    alpha: float = 0.1
    gamma: float = 0.95
    epsilon: float = 0.1

class SystemConfig(BaseModel):
    # Polut
    BASE_DIR: Path = Path(__file__).parent
    RESULTS_DIR: Path = BASE_DIR / "results"
    MODELS_DIR: Path = BASE_DIR / "models"
    
    # Järjestelmä
    num_machines: int = Field(4, ge=1)
    anfis: AnfisConfig = AnfisConfig()
    marl: MarlConfig = MarlConfig()

    def setup_dirs(self):
        self.RESULTS_DIR.mkdir(exist_ok=True, parents=True)
        self.MODELS_DIR.mkdir(exist_ok=True, parents=True)

# Alustetaan globaali konfiguraatio
cfg = SystemConfig()