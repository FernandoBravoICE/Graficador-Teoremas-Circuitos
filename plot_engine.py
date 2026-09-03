# plot_engine.py (Actualización para integrar el esquemático al tema oscuro de la UI)

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

class SchematicCanvas(FigureCanvas):
    """Lienzo estático adaptado al tema oscuro de la interfaz para eliminar el contraste por ruido visual."""
    def __init__(self, parent=None, width=4, height=2.5, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        # Sincronización exacta con el fondo gris oscuro de la aplicación PyQt6
        self.fig.patch.set_facecolor('#2b2b2b') 
        self.axes = self.fig.add_subplot(111)
        self.axes.set_facecolor('#2b2b2b')
        super().__init__(self.fig)
        self.setParent(parent)
        self.draw_circuit()

    def draw_circuit(self):
        ax = self.axes
        ax.clear()
        ax.set_axis_off()
        
        lw = 1.0 
        line_color = '#e0e0e0'  # Gris claro para alta legibilidad sin contraste agresivo
        text_color = '#ffffff'  # Texto blanco integrado
        
        # Resistencia Thévenin
        ax.plot([1.0, 1.3], [2.0, 2.0], color=line_color, lw=lw)
        rx = [1.3, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6, 2.7]
        ry = [2.0, 2.15, 1.85, 2.15, 1.85, 2.15, 1.85, 2.15, 2.0]
        ax.plot(rx, ry, color=line_color, lw=lw)
        ax.plot([2.7, 3.0], [2.0, 2.0], color=line_color, lw=lw)
        ax.text(2.0, 2.3, "$R_{th}$", ha='center', fontsize=10, color=text_color)

        # Inductor
        ax.plot([3.0, 3.0], [2.0, 1.8], color=line_color, lw=lw)
        t_ind = np.linspace(0, 5*np.pi, 200)
        x_ind = 3.0 + 0.12 * np.sin(t_ind)
        y_ind = 1.8 - 0.6 * (t_ind / (5*np.pi))
        ax.plot(x_ind, y_ind, color=line_color, lw=lw)
        ax.plot([3.0, 3.0], [1.2, 0.5], color=line_color, lw=lw)
        ax.text(3.3, 1.5, "$L$", va='center', fontsize=10, color=text_color)

        # Bus Inferior
        ax.plot([1.0, 3.0], [0.5, 0.5], color=line_color, lw=lw)

        # Interruptor en t=0 (con tonos de acento armónicos)
        ax.plot([1.0, 1.0], [0.5, 1.1], color=line_color, lw=lw)
        ax.plot([1.0, 1.0], [1.5, 2.0], color=line_color, lw=lw)
        ax.plot([1.0, 0.7], [1.5, 1.1], color='#58a6ff', lw=lw) 
        ax.plot(1.0, 1.1, color=line_color, marker='o', markersize=3)
        ax.plot(1.0, 1.5, color=line_color, marker='o', markersize=3)
        ax.annotate("", xy=(0.95, 1.15), xytext=(0.5, 1.3), arrowprops=dict(arrowstyle="->", color="#ff7b72", lw=0.8))
        ax.text(0.2, 1.35, "$t=0$", color="#ff7b72", fontsize=9)

        # Ecuación Diferencial
        eq_text = r"$L\frac{di(t)}{dt} + R_{th}i(t) = 0$"
        ax.text(2.0, 0.0, eq_text, ha='center', fontsize=11, color=text_color)
        
        ax.set_xlim(-0.2, 3.8)
        ax.set_ylim(-0.2, 2.6)
        self.fig.tight_layout(pad=0)


class PlotCanvas(FigureCanvas):
    """Lienzo analítico con estética científica tipo MATLAB (Mantiene exportación HD independiente)."""
    def __init__(self, parent=None, width=8, height=6, dpi=110):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)
        self.configure_plot_axis()
        self.fig.tight_layout(pad=2.0)

    def configure_plot_axis(self):
        ax = self.axes
        ax.set_xlabel('Tiempo (s)', fontsize=10)
        ax.set_ylabel('Corriente i(t) [A]', fontsize=10)
        
        ax.grid(True, which='major', linestyle='-', linewidth=0.6, color='#d3d3d3')
        ax.grid(True, which='minor', linestyle=':', linewidth=0.4, color='#e0e0e0')
        ax.minorticks_on()
        
        ax.tick_params(direction='in', top=True, right=True, length=5)
        ax.tick_params(which='minor', direction='in', top=True, right=True, length=2.5)

    def plot_simulation(self, t_array, i_array, tau, i0):
        ax = self.axes
        ax.clear()
        
        c_blue = '#0072BD'
        c_green = '#77AC30'

        t_pre = np.linspace(-t_array[-1]*0.15, 0, 100)
        i_pre = np.full_like(t_pre, i0)
        ax.plot(t_pre, i_pre, color=c_green, linewidth=1.5, label=r"$i(0^-) = i_L(0)$ (Estable)")
        
        ax.axvline(0, color='black', linestyle='--', linewidth=1.0, alpha=0.4)
        ax.plot(t_array, i_array, color=c_blue, linewidth=1.5, label=r"$i(t) = i_L(0)e^{-\frac{R_{th}}{L}t}$")
        
        tau_multipliers = [1, 2, 3, 4, 5]
        percentages = [36.0, 13.5, 4.4, 1.83, 0.67]
        
        for mult, pct in zip(tau_multipliers, percentages):
            t_val = mult * tau
            if t_val <= t_array[-1]:
                i_val = i0 * np.exp(-mult)
                ax.plot(t_val, i_val, 'ro', markersize=4)
                
                # Transparencia estricta a 0.3 y fuente ligera
                ax.annotate(f"{mult}τ ({pct}%)", (t_val, i_val), 
                            textcoords="offset points", xytext=(6, 4), ha='left', 
                            fontsize=8, fontweight='normal', alpha=0.3)

        self.configure_plot_axis()
        ax.legend(loc='upper right', frameon=True, edgecolor='black', fancybox=False, fontsize=10)
        self.fig.tight_layout(pad=2.0)
        self.draw()

    def export_hd(self, filepath):
        self.fig.savefig(filepath, dpi=300, bbox_inches='tight')