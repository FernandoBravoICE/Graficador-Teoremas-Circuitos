#Ecuaciones predefinidas del estado transitorio: subamortiguado, críticamente amortiguado, sobreamortiguado
# circuit_models.py

import numpy as np

class CircuitSimulator:
    """Modelos analíticos estrictos para respuestas de un circuito RL de primer orden."""
    
    @staticmethod
    def get_tau(R_th, L):
        return L / R_th if R_th > 0 else float('inf')

    @staticmethod
    def rl_free_response(t, R_th, L, i0):
        tau = CircuitSimulator.get_tau(R_th, L)
        i_t = i0 * np.exp(- (R_th / L) * t)
        return i_t, tau

    @staticmethod
    def rl_forced_response(t, R_th, L, iN):
        tau = CircuitSimulator.get_tau(R_th, L)
        i_t = iN * (1 - np.exp(- (R_th / L) * t))
        return i_t, tau

    @staticmethod
    def rl_total_response(t, R_th, L, i0, iN):
        tau = CircuitSimulator.get_tau(R_th, L)
        i_t = i0 * np.exp(- (R_th / L) * t) + iN * (1 - np.exp(- (R_th / L) * t))
        return i_t, tau