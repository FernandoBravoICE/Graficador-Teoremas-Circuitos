#Ecuaciones predefinidas del estado transitorio: subamortiguado, críticamente amortiguado, sobreamortiguado
# circuit_models.py
import numpy as np

class CircuitSimulator:
    """Modelos analíticos estrictos para respuestas de un circuito RL y RC de primer orden."""
    
    @staticmethod
    def get_tau_rl(R_th, L):
        return L / R_th if R_th > 0 else float('inf')

    @staticmethod
    def get_tau_rc(R_th, C):
        return R_th * C if R_th > 0 else 0

    # ================= MODELOS RL =================
    @staticmethod
    def rl_free_response(t, R_th, L, i0):
        tau = CircuitSimulator.get_tau_rl(R_th, L)
        i_t = i0 * np.exp(-t / tau) if tau != float('inf') else np.zeros_like(t)
        return i_t, tau

    @staticmethod
    def rl_forced_response(t, R_th, L, iN):
        tau = CircuitSimulator.get_tau_rl(R_th, L)
        i_t = iN * (1 - np.exp(-t / tau)) if tau != float('inf') else np.zeros_like(t)
        return i_t, tau

    @staticmethod
    def rl_total_response(t, R_th, L, i0, iN):
        tau = CircuitSimulator.get_tau_rl(R_th, L)
        if tau == float('inf'): return np.zeros_like(t), tau
        i_t = i0 * np.exp(-t / tau) + iN * (1 - np.exp(-t / tau))
        return i_t, tau

    # ================= MODELOS RC =================
    @staticmethod
    def rc_free_response(t, R_th, C, v0):
        tau = CircuitSimulator.get_tau_rc(R_th, C)
        v_t = v0 * np.exp(-t / tau) if tau > 0 else np.zeros_like(t)
        return v_t, tau

    @staticmethod
    def rc_forced_response(t, R_th, C, vTh):
        tau = CircuitSimulator.get_tau_rc(R_th, C)
        v_t = vTh * (1 - np.exp(-t / tau)) if tau > 0 else np.zeros_like(t)
        return v_t, tau

    @staticmethod
    def rc_total_response(t, R_th, C, v0, vTh):
        tau = CircuitSimulator.get_tau_rc(R_th, C)
        if tau <= 0: return np.zeros_like(t), tau
        v_t = v0 * np.exp(-t / tau) + vTh * (1 - np.exp(-t / tau))
        return v_t, tau
    
    # ================= MODELOS RLC =================
    @staticmethod
    def rlc_series_critically_damped(t, R, L, C, i0, di0_dt):
        """
        Modelo analítico estricto para circuito RLC serie críticamente amortiguado.
        Implementa: i(t) = i(0)e^(-αt) + (di(0)/dt + α*i(0)) * t * e^(-αt)
        """
        if L <= 0 or C <= 0: return np.zeros_like(t), 0
        alpha = R / (2 * L)
        
        # Evaluación vectorial de la respuesta transitoria
        term1 = i0 * np.exp(-alpha * t)
        term2 = (di0_dt + alpha * i0) * t * np.exp(-alpha * t)
        i_t = term1 + term2
        
        tau_eq = 1 / alpha if alpha > 0 else float('inf')
        return i_t, tau_eq