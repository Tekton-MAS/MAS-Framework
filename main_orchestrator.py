# =============================================================================
# [tietokoneohjelma] Holonic Enterprise MAS – TektonAI
# 
# Tekijä:          Toni Miettinen
# Oppilaitos:      Metropolia Ammattikorkeakoulu, Helsinki, Suomi
# Vuosi:           2026
# Versio:          1.0
# Lisenssi:        MIT License
# Saatavuus:       https://github.com/Tekton-MAS/MAS-Framework
# Viittaus:        Miettinen T. (2026). Moniagenttinen tekoälyarkkitehtuuri 
#                  pienyrityksen sähkö- ja automaatiojärjestelmien hallintaan.
#                  Insinöörityö, Metropolia AMK.
#
# Kuvaus: Pääorkestrointiskripti (main_orchestrator.py) holoniselle 
#         moniagenttijärjestelmälle (MAS). Käynnistää Ray-klusterin, 
#         suorittaa hajautetun ANFIS-koulutuksen koneagenttien neuro-sumeille 
#         malleille, ajaa moniagenttista vahvistusoppimista (MARL, Q-learning) 
#         PettingZoo-ympäristössä (HolonicFactoryEnv), tuottaa reaaliaikaiset 
#         CSV-tulokset ja staattiset raportit Streamlit-dashboardille. 
#         Sisältää vikasietoiset importit ja konsoliraportoinnin Rich-kirjastolla.
#
# Käynnistys: python main_orchestrator.py
# =============================================================================

import os
import sys
import time
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# --- ASETUS 1: Estetään Rayn FutureWarning GPU-hallinnasta ---
os.environ["RAY_ACCEL_ENV_VAR_OVERRIDE_ON_ZERO"] = "0"

# --- ASETUS 2: Varmistetaan moduulien löytyminen ---
sys.path.append(str(Path(__file__).parent))

import ray
from rich.console import Console
from rich.panel import Panel
from rich.progress import track, Progress, SpinnerColumn, TextColumn
from rich.table import Table

# Tuodaan omat moduulit
from config import cfg
from workers.train_worker import train_anfis_remote

# Alustetaan Rich-konsoli
console = Console()

# Dynaamiset importit vikasietoisuudella
try:
    from factory_simulation import HolonicFactoryEnv
    ENV_AVAILABLE = True
except ImportError:
    ENV_AVAILABLE = False

try:
    from ontology import onto
except ImportError:
    onto = None

class HolonicOrchestrator:
    def __init__(self):
        self.start_time = time.time()
        cfg.setup_dirs()
        self._print_header()
        self._init_ray()

    def _print_header(self):
        console.print(Panel.fit(
            "[bold cyan]TektonAI Holonic Enterprise MAS[/bold cyan]\n"
            "[dim]Distributed Intelligent Manufacturing System[/dim]",
            border_style="cyan"
        ))

    def _init_ray(self):
        if ray.is_initialized():
            ray.shutdown()
        
        with console.status("[bold green]Käynnistetään Ray-klusteria...[/bold green]", spinner="dots"):
            ray.init(ignore_reinit_error=True, log_to_driver=False)
            resources = ray.cluster_resources()
            cpu_count = int(resources.get("CPU", 0))
            gpu_count = int(resources.get("GPU", 0))
        
        console.print(f"✓ Ray Runtime valmis: [bold]{cpu_count} CPU[/bold] ytimet, [bold]{gpu_count} GPU[/bold]")

    def run_checks(self):
        console.print("\n[bold]1. Järjestelmän tarkistus[/bold]")
        
        # Ontologia
        if onto:
            cls_count = len(list(onto.classes()))
            console.print(f"  ✓ Ontologia: [green]OK[/green] ({cls_count} luokkaa)")
        else:
            console.print("  ! Ontologia: [red]PUUTTUU[/red] (Ajo jatkuu ilman semantiikkaa)")

        # Ympäristö
        if ENV_AVAILABLE:
            console.print("  ✓ Simulaatioympäristö: [green]OK[/green]")
        else:
            console.print("  ! Simulaatioympäristö: [red]PUUTTUU[/red] (Käytetään Mock-dataa)")

    def run_parallel_training(self):
        console.print("\n[bold]2. Hajautettu ANFIS-koulutus (Parallel)[/bold]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True
        ) as progress:
            task = progress.add_task("Lähetetään työt klusterille...", total=cfg.num_machines)
            
            # Asynkroninen lähetys
            futures = [train_anfis_remote.remote(i) for i in range(cfg.num_machines)]
            progress.update(task, description=f"Koulutetaan {cfg.num_machines} mallia rinnakkain...")
            
            # Odotetaan tuloksia
            results = ray.get(futures)
        
        # Tulosten taulukointi
        table = Table(title="Koulutustulokset")
        table.add_column("Machine ID", justify="center", style="cyan")
        table.add_column("Status", justify="center")
        table.add_column("Loss", justify="right")
        table.add_column("Path", style="dim")

        success_count = 0
        for res in results:
            if res["status"] == "SUCCESS":
                status = "[green]VALMIS[/green]"
                loss = f"{res['loss']:.5f}"
                success_count += 1
            else:
                status = "[red]VIRHE[/red]"
                loss = "N/A"
            
            path_str = str(Path(res.get('path', '')).name)
            table.add_row(str(res['id']), status, loss, path_str)

        console.print(table)
        console.print(f"-> [bold green]{success_count}/{cfg.num_machines}[/bold green] mallia päivitetty.")

    def run_marl_simulation(self):
        console.print("\n[bold]3. Multi-Agent Reinforcement Learning (MARL)[/bold]")
        
        rewards_history = []
        if not ENV_AVAILABLE:
            console.print("[yellow]Varoitus: Oikeaa ympäristöä ei löydy. Ajetaan demo-moodissa.[/yellow]")
            return

        env = HolonicFactoryEnv()
        
        # Q-learning alustus
        Q_tables = {agent: np.zeros((env.action_spaces[agent].n)) for agent in env.possible_agents}
        alpha, gamma, epsilon = 0.1, 0.9, 0.2
        
        # Silmukka
        for ep in track(range(cfg.marl.episodes), description="Simuloidaan episodeja..."):
            obs, _ = env.reset()
            ep_reward = 0
            terminated = False
            steps = 0
            
            current_epsilon = max(0.01, epsilon * (1 - ep / cfg.marl.episodes))

            while not terminated and steps < 100:
                actions = {}
                for agent in env.agents:
                    if np.random.rand() < current_epsilon:
                        act = env.action_spaces[agent].sample()
                    else:
                        act = np.argmax(Q_tables[agent])
                    actions[agent] = act
                
                _, rewards, dones, _, _ = env.step(actions)
                
                for agent in actions:
                    r = rewards[agent]
                    best_next = np.max(Q_tables[agent])
                    old_q = Q_tables[agent][actions[agent]]
                    Q_tables[agent][actions[agent]] = old_q + alpha * (r + gamma * best_next - old_q)
                    ep_reward += r

                terminated = any(dones.values())
                steps += 1
            
            rewards_history.append(ep_reward / max(1, steps))

        # Kutsutaan päivitettyä plot-funktiota
        self._plot_results(rewards_history)
        
        # Loppuraportti
        if rewards_history:
            start_avg = np.mean(rewards_history[:5])
            end_avg = np.mean(rewards_history[-5:])
            improvement = ((end_avg - start_avg) / abs(start_avg)) * 100
            
            console.print(Panel(
                f"Alkupään keskiarvo: {start_avg:.2f}\n"
                f"Loppupään keskiarvo: {end_avg:.2f}\n"
                f"[bold green]Suorituskyvyn parannus: {improvement:+.1f}%[/bold green]",
                title="MARL Analyysi",
                expand=False
            ))

    def _plot_results(self, rewards):
        # --- UUSI OMINAISUUS: CSV-TALLENNUS DASHBOARDIA VARTEN ---
        try:
            import pandas as pd
            window = 5
            # Lasketaan liukuva keskiarvo
            smoothed = np.convolve(rewards, np.ones(window)/window, mode='valid')
            # Täytetään array saman mittaiseksi kuin rewards (lisätään NaN loppuun/alkuun)
            # Yksinkertainen tapa: tehdään listasta yhtä pitkä täyttämällä nan:lla lopusta
            smoothed_padded = smoothed.tolist() + [np.nan] * (len(rewards) - len(smoothed))
            
            df = pd.DataFrame({
                "Episode": range(1, len(rewards) + 1),
                "Reward_Raw": rewards,
                "Reward_Smoothed": smoothed_padded
            })
            
            csv_path = cfg.RESULTS_DIR / "training_data.csv"
            df.to_csv(csv_path, index=False)
            console.print(f"✓ Data tallennettu: [blue]{csv_path}[/blue]")
            
        except ImportError:
            console.print("[yellow]Varoitus: Pandas puuttuu, CSV-tiedostoa ei luotu.[/yellow]")
        except Exception as e:
            console.print(f"[red]Virhe CSV-tallennuksessa: {e}[/red]")

        # --- VANHA OMINAISUUS: STAATTINEN KUVA ---
        plt.figure(figsize=(10, 6))
        window = 5
        smoothed_plot = np.convolve(rewards, np.ones(window)/window, mode='valid')
        plt.plot(rewards, color="#bdc3c7", alpha=0.4, label="Raaka")
        plt.plot(smoothed_plot, color="#27ae60", linewidth=2.5, label="Trendi (MA5)")
        plt.title("Holonic Factory Performance")
        plt.xlabel("Episode")
        plt.ylabel("Reward / Step")
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        output_path = cfg.RESULTS_DIR / "final_report.png"
        plt.savefig(output_path)
        plt.close()
        console.print(f"✓ Raportti tallennettu: [blue]{output_path}[/blue]")

    def shutdown(self):
        ray.shutdown()
        elapsed = time.time() - self.start_time
        console.print(f"\n[bold inverse] Järjestelmäajo valmis ({elapsed:.2f}s) [/bold inverse]")

if __name__ == "__main__":
    orchestrator = HolonicOrchestrator()
    try:
        orchestrator.run_checks()
        orchestrator.run_parallel_training()
        orchestrator.run_marl_simulation()
    except KeyboardInterrupt:
        console.print("\n[red]Keskeytetty käyttäjän toimesta.[/red]")
    except Exception as e:
        console.print_exception()
    finally:
        orchestrator.shutdown()