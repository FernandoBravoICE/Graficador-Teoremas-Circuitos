#plot engine
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

class PlotCanvas(FigureCanvas):
    """Lienzo analítico con renderizado estricto estilo MATLAB."""
    def __init__(self, parent=None, width=8, height=6, dpi=110):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig.patch.set_facecolor('#ffffff')
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)
        self.configure_plot_axis()
        self.fig.tight_layout(pad=2.0)

    def configure_plot_axis(self, ylabel='Amplitud'):
        ax = self.axes
        ax.set_xlabel('Tiempo (s)', fontsize=10, fontweight='medium')
        ax.set_ylabel(ylabel, fontsize=10, fontweight='medium')
        
        ax.grid(True, which='major', linestyle='-', linewidth=0.6, color='#d3d3d3')
        ax.grid(True, which='minor', linestyle=':', linewidth=0.4, color='#e0e0e0')
        ax.minorticks_on()
        
        # Emulación MATLAB: Ticks internos y bordes negros sólidos
        ax.tick_params(direction='in', top=True, right=True, length=6, width=1.0)
        ax.tick_params(which='minor', direction='in', top=True, right=True, length=3, width=0.8)
        
        for spine in ax.spines.values():
            spine.set_linewidth(1.0)
            spine.set_color('black')

    def plot_simulation(self, curves_data, tau, show_taus, ylabel='Amplitud'):
        ax = self.axes
        ax.clear()
        
        y_min_global = float('inf')
        y_max_global = float('-inf')
        
        for curve in curves_data:
            t_array = curve['t']
            y_array = curve['y']
            label = curve['label']
            color = curve['color']

            y_min_global = min(y_min_global, np.min(y_array))
            y_max_global = max(y_max_global, np.max(y_array))

            t_pre = np.linspace(-t_array[-1]*0.15, 0, 100)
            y0 = y_array[0]
            y_pre = np.full_like(t_pre, y0)
            
            ax.plot(t_pre, y_pre, color=color, linewidth=1.5, linestyle=':')
            ax.plot(t_array, y_array, color=color, linewidth=1.5, label=label)
            
            if show_taus and tau > 0:
                tau_multipliers = [1, 2, 3, 4, 5]
                for mult in tau_multipliers:
                    t_val = mult * tau
                    if t_val <= t_array[-1]:
                        y_val = np.interp(t_val, t_array, y_array)
                        ax.plot(t_val, y_val, 'ro', markersize=4.5, markeredgecolor='black', markeredgewidth=0.5)
                        ax.annotate(f"{mult}τ", (t_val, y_val), 
                                    textcoords="offset points", xytext=(6, 4), ha='left', 
                                    fontsize=9, fontweight='normal', color='#333333')

        ax.axvline(0, color='black', linestyle='--', linewidth=1.0, alpha=0.5)
        self.configure_plot_axis(ylabel)

        if curves_data:
            margen_y = (y_max_global - y_min_global) * 0.1
            if margen_y == 0: 
                margen_y = abs(y_max_global) * 0.1 if y_max_global != 0 else 0.1
            
            # Límites de eje fijados estrictamente
            ax.set_ylim(y_min_global - margen_y, y_max_global + margen_y)
            ax.set_xlim(t_pre[0], t_array[-1])
            
            ax.legend(loc='best', frameon=True, edgecolor='black', fancybox=False, fontsize=9)
            
        self.fig.tight_layout(pad=2.0)
        self.draw()

    def export_hd(self, filepath):
        self.fig.savefig(filepath, dpi=300, bbox_inches='tight')