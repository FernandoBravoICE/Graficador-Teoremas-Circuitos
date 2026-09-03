#Ecuaciones predefinidas del estado transitorio: subamortiguado, críticamente amortiguado, sobreamortiguado
import numpy as np

class CircuitSimulator:
    """Modelo analítico para la respuesta libre de un circuito RL de primer orden."""
    
    @staticmethod
    def rl_free_response(t, R_th, L, i0):
        tau = L / R_th if R_th > 0 else float('inf')
        i_t = i0 * np.exp(-t / tau)
        return i_t, tau