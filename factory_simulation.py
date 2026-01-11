# =============================================================================
# [tietokoneohjelma] Holonic Enterprise MAS – TektonAI
# 
# Tekijä:          Toni Miettinen
# Oppilaitos:      Metropolia Ammattikorkeakoulu, Helsinki, Suomi
# Vuosi:           2026
# Versio:          1.0
# Lisenssi:        MIT License
# Saatavuus:       https://github.com/Tekton-MAS/Lotka-Volterra
# Viittaus:        Miettinen T. (2026). Moniagenttinen tekoälyarkkitehtuuri 
#                  pienyrityksen sähkö- ja automaatiojärjestelmien hallintaan.
#                  Insinöörityö, Metropolia AMK.
#
# Kuvaus: Holoninen tehdassimulaatioympäristö (HolonicFactoryEnv) PettingZoo-
#         ParallelEnv-rajapinnalla. Mallintaa pk-yrityksen tuotantoa 4–n koneella 
#         ja yhdellä supervisor-agentilla. Sisältää satunnaisten tilausten 
#         generoinnin, koneiden havainto- ja toimintatilat, yksinkertaisen 
#         palkkiorakenteen (tilauksen arvo + prosessointi) sekä supervisorin 
#         globaalin koordinaatiopalkkion. Käytetään MARL-koulutuksessa 
#         (Q-learning) ja toimii digitaalisen kaksosen ydinympäristönä.
#         Osa opinnäytetyötä "Moniagenttinen tekoälyarkkitehtuuri...".
#
# Käyttö: Tuodaan factory_simulation.py:stä main_orchestrator.py:ssä ja muissa 
#         MARL-simulaatioissa.
# =============================================================================

import numpy as np
from gymnasium.spaces import Discrete, Box
from pettingzoo import ParallelEnv

# Yritetään hakea kyvykkyydet ontologiasta, tai käytetään oletuksia
try:
    from ontology import CAPABILITIES
except ImportError:
    CAPABILITIES = ["Milling", "Turning", "Drilling", "Fast"]

class HolonicFactoryEnv(ParallelEnv):
    metadata = {"name": "holonic_sme_v1", "render_modes": []}

    def __init__(self, num_machines: int = 4):
        super().__init__()
        self.num_machines = num_machines
        self.possible_agents = [f"machine_{i}" for i in range(num_machines)] + ["supervisor"]
        self.agents = self.possible_agents[:]

        # Toimintatila: 0=Idle, 1-10=Valitse tilaus
        self.action_spaces = {
            agent: Discrete(11) for agent in self.possible_agents
        }

        # Havaintoavaruus (Datan muoto neuroverkolle)
        # Koneet: [load, queue_len, id_norm, noise]
        self.observation_spaces = {
            agent: Box(low=0.0, high=1.0, shape=(4,), dtype=np.float32) 
            for agent in self.possible_agents[:-1]
        }
        # Supervisor: [queue_len, progress]
        self.observation_spaces["supervisor"] = Box(low=0.0, high=1.0, shape=(2,), dtype=np.float32)

    def reset(self, seed=None, options=None):
        self.agents = self.possible_agents[:]
        self.current_step = 0
        # Generoidaan satunnaisia tilauksia
        self.orders = [{"value": np.random.uniform(10, 100), "time": np.random.uniform(5, 20)} for _ in range(10)]
        return self._get_obs(), {agent: {} for agent in self.agents}

    def _get_obs(self):
        obs = {}
        queue_norm = len(self.orders) / 20.0
        for agent in self.agents:
            if "machine" in agent:
                mid = int(agent.split("_")[1])
                obs[agent] = np.array([
                    np.random.rand(),   # Load
                    queue_norm,         # Global state
                    mid / 4.0,          # ID
                    np.random.normal(0, 0.1) # Noise
                ], dtype=np.float32)
            else:
                obs[agent] = np.array([queue_norm, self.current_step/100.0], dtype=np.float32)
        return obs

    def step(self, actions):
        rewards = {agent: 0.0 for agent in self.agents}
        
        # Logiikka: Jos kone valitsee validin tilauksen, saa palkkion
        processed = 0
        for agent, act in actions.items():
            if "machine" in agent:
                if 0 < act <= len(self.orders):
                    # Hyvä valinta -> Palkkio perustuu tilauksen arvoon ja nopeuteen
                    order_val = self.orders[act-1]["value"]
                    rewards[agent] = order_val / 10.0
                    processed += 1
                elif act > len(self.orders):
                    # Huono valinta (olematon tilaus) -> Sakko
                    rewards[agent] = -0.5
        
        # Supervisor saa palkkion kokonaistuotannosta
        if "supervisor" in self.agents:
            rewards["supervisor"] = processed * 1.5 - (len(self.orders) * 0.1)

        self.current_step += 1
        terminated = self.current_step >= 100
        dones = {agent: terminated for agent in self.agents}
        dones["__all__"] = terminated
        
        if terminated: self.agents = []

        return self._get_obs(), rewards, dones, dones, {a: {} for a in self.possible_agents}