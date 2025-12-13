# Lotka-Volterra predator-prey model simulation with graphical output [computer program].
# Miettinen T. Metropolia University of Applied Sciences, Helsinki, Finland; 2025.
# Version: 1.0
# Available from: https://github.com/Tekton-MAS/Lotka-Volterra.git
# Accessed: 2025 Dec 13.

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from scipy import integrate

# --- MATEMAATTINEN MALLI (TEORIA) ---
# Yhtälöt:
# dx/dt = alpha*x - beta*x*y   (Saalis)
# dy/dt = delta*x*y - gamma*y  (Peto)

def derivative(X, t, alpha, beta, delta, gamma):
    x, y = X
    dotx = x * (alpha - beta * y)
    doty = y * (delta * x - gamma)
    return [dotx, doty]

def simulate_lv(x0, y0, t_max, nt, alpha, beta, delta, gamma):
    t = np.linspace(0, t_max, nt)
    X0 = [x0, y0]
    res = integrate.odeint(derivative, X0, t, args=(alpha, beta, delta, gamma))
    x, y = res.T
    return t, x, y

# --- GUI ASETUKSET ---
plt.style.use('seaborn-v0_8-whitegrid')
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 8)) # Hieman korkeampi ikkuna

# ASETTELU:
plt.subplots_adjust(left=0.1, bottom=0.35, right=0.95, top=0.85)

# --- PÄÄOTSIKKO ---
fig.suptitle('Lotka–Volterra-simulaatio', fontsize=24, fontweight='bold', y=0.95)

# Alkuarvot
t_max = 50
nt = 2000
x0_init, y0_init = 10.0, 5.0

# Parametrien alkuarvot
init_alpha = 1.0
init_beta = 0.1
init_delta = 0.075
init_gamma = 1.5

t, x, y = simulate_lv(x0_init, y0_init, t_max, nt, init_alpha, init_beta, init_delta, init_gamma)

# --- KUVAAJA 1: AIKASARJA ---
l1, = ax1.plot(t, x, 'g-', lw=2, label='Saalis (x)')
l2, = ax1.plot(t, y, 'r-', lw=2, label='Peto (y)')
ax1.set_title(r'Aikasarja: $\alpha x - \beta xy$ ja $\delta xy - \gamma y$', fontsize=14)
ax1.set_xlabel('Aika')
ax1.set_ylabel('Populaatio')
ax1.legend(loc='upper right')
ax1.grid(True, alpha=0.3)
ax1.set_ylim(0, max(np.max(x), np.max(y)) * 1.5)

# --- KUVAAJA 2: FAASIAVARUUS ---
l_phase, = ax2.plot(x, y, 'b-', lw=1.5)
eq_x = init_gamma / init_delta
eq_y = init_alpha / init_beta
scat_eq = ax2.scatter([eq_x], [eq_y], color='black', zorder=5, s=100, label='Tasapainopiste')

ax2.set_title('Faasiavaruus (Phase Portrait)', fontsize=14)
ax2.set_xlabel('Saaliiden määrä (x)')
ax2.set_ylabel('Petoeläinten määrä (y)')
ax2.grid(True, alpha=0.3)
ax2.legend()
ax2.set_xlim(0, max(x) * 1.5)
ax2.set_ylim(0, max(y) * 1.5)

# --- LIUKUSÄÄTIMET ---
axcolor = 'lightgoldenrodyellow'
ax_alpha = plt.axes([0.15, 0.22, 0.3, 0.03], facecolor=axcolor)
ax_beta  = plt.axes([0.15, 0.17, 0.3, 0.03], facecolor=axcolor)
ax_delta = plt.axes([0.60, 0.22, 0.3, 0.03], facecolor=axcolor)
ax_gamma = plt.axes([0.60, 0.17, 0.3, 0.03], facecolor=axcolor)

s_alpha = Slider(ax_alpha, r'$\alpha$ (Saalis kasvu)', 0.1, 5.0, valinit=init_alpha)
s_beta = Slider(ax_beta, r'$\beta$ (Saalistus)', 0.01, 1.0, valinit=init_beta)
s_delta = Slider(ax_delta, r'$\delta$ (Pedon hyöty)', 0.01, 1.0, valinit=init_delta)
s_gamma = Slider(ax_gamma, r'$\gamma$ (Pedon kuolema)', 0.1, 5.0, valinit=init_gamma)

# --- PÄIVITYS ---
def update(val):
    a = s_alpha.val
    b = s_beta.val
    d = s_delta.val
    g = s_gamma.val
    _, x_new, y_new = simulate_lv(x0_init, y0_init, t_max, nt, a, b, d, g)
    
    l1.set_ydata(x_new)
    l2.set_ydata(y_new)
    l_phase.set_data(x_new, y_new)
    
    new_eq_x = g / d
    new_eq_y = a / b
    scat_eq.set_offsets(np.c_[[new_eq_x], [new_eq_y]])
    
    max_pop = max(np.max(x_new), np.max(y_new))
    ax1.set_ylim(0, max_pop * 1.2)
    ax2.set_xlim(0, np.max(x_new) * 1.2)
    ax2.set_ylim(0, np.max(y_new) * 1.2)
    fig.canvas.draw_idle()

s_alpha.on_changed(update)
s_beta.on_changed(update)
s_delta.on_changed(update)
s_gamma.on_changed(update)

# --- RESET-NAPPI ---
resetax = plt.axes([0.8, 0.06, 0.1, 0.04]) 
button = Button(resetax, 'Reset', color=axcolor, hovercolor='0.975')
def reset(event):
    s_alpha.reset()
    s_beta.reset()
    s_delta.reset()
    s_gamma.reset()
button.on_clicked(reset)

# --- CREDIT-TEKSTI ---
fig.text(0.99, 0.01, '(Miettinen T, Metropolia AMK, 2026)',
         ha='right', va='bottom', fontsize=11, color='dimgray', style='italic')

plt.show()