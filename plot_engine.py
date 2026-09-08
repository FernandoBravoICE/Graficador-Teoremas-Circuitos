#PLOT ENGINE
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

class PlotCanvas(FigureCanvas):
    """Lienzo analítico con soporte para múltiples curvas y autoajuste dinámico de escala."""
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

    def plot_simulation(self, curves_data, tau, show_taus):
        ax = self.axes
        ax.clear()
        
        y_min_global = float('inf')
        y_max_global = float('-inf')
        
        for curve in curves_data:
            t_array = curve['t']
            i_array = curve['i']
            label = curve['label']
            color = curve['color']

            # Extracción de extremos para autoajuste Y
            y_min_global = min(y_min_global, np.min(i_array))
            y_max_global = max(y_max_global, np.max(i_array))

            # Tramo estable (t < 0)
            t_pre = np.linspace(-t_array[-1]*0.15, 0, 100)
            i0 = i_array[0]
            i_pre = np.full_like(t_pre, i0)
            
            ax.plot(t_pre, i_pre, color=color, linewidth=1.5, linestyle=':')
            ax.plot(t_array, i_array, color=color, linewidth=1.5, label=label)
            
            if show_taus:
                tau_multipliers = [1, 2, 3, 4, 5]
                for mult in tau_multipliers:
                    t_val = mult * tau
                    if t_val <= t_array[-1]:
                        i_val = np.interp(t_val, t_array, i_array)
                        ax.plot(t_val, i_val, 'ro', markersize=4)
                        ax.annotate(f"{mult}τ", (t_val, i_val), 
                                    textcoords="offset points", xytext=(6, 4), ha='left', 
                                    fontsize=8, fontweight='normal', alpha=0.5)

        ax.axvline(0, color='black', linestyle='--', linewidth=1.0, alpha=0.4)
        self.configure_plot_axis()

        # Ajuste dinámico de escala Y con 10% de margen
        if curves_data:
            margen_y = (y_max_global - y_min_global) * 0.1
            if margen_y == 0:  # Prevención para respuestas constantes
                margen_y = abs(y_max_global) * 0.1 if y_max_global != 0 else 0.1
            ax.set_ylim(y_min_global - margen_y, y_max_global + margen_y)
            
            # Reducción de fontsize a 9 para acomodar ecuaciones largas
            ax.legend(loc='best', frameon=True, edgecolor='black', fancybox=False, fontsize=9)
            
        self.fig.tight_layout(pad=2.0)
        self.draw()

    def export_hd(self, filepath):
        self.fig.savefig(filepath, dpi=300, bbox_inches='tight')