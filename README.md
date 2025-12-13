[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# Lotka-Volterra Predator-Prey Simulation

A graphical and interactive simulation of the classic Lotka-Volterra predator-prey model.  
The program numerically solves the differential equations and plots both the time evolution of prey and predator populations as well as the phase space trajectory. Users can adjust model parameters in real time using sliders, and reset to default values with a button.

## Description

The Lotka-Volterra model describes the interaction between two species: one prey and one predator.  
It consists of two first-order differential equations:

- dx/dt = αx - βxy  
- dy/dt = δxy - γy  

where  
- x = prey population  
- y = predator population  
- α, β, δ, γ = model parameters

This repository contains a Python script that implements the simulation using `scipy.integrate.odeint` and visualizes the results with `matplotlib`.  
The graphical interface includes sliders for adjusting parameters (α, β, δ, γ) and a reset button to restore defaults.

## Preview

![Simulation example](https://github.com/Tekton-MAS/Lotka-Volterra/blob/main/Lotka-Volterra_sample.jpg) 
*Example output of the simulation with default parameters*

## Installation and Usage

### Requirements
- Python 3.8 or newer
- Libraries: `numpy`, `scipy`, `matplotlib`

### Installation
Clone the repository and install dependencies:

```bash
pip install numpy scipy matplotlib
git clone https://github.com/Tekton-MAS/Lotka-Volterra.git
cd Lotka-Volterra

Run the simulation
python lotka_volterra.py
