#Ui_main
import os
import numpy as np
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QGroupBox, 
                            QMessageBox, QFormLayout, QFileDialog, QCheckBox, QComboBox)
from PyQt6.QtCore import Qt
from circuits_models import CircuitSimulator
from plot_engine import PlotCanvas

class TransientSimulatorUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Analizador de Circuitos - Estado Transitorio")
        self.setGeometry(50, 50, 1250, 800)
        self._last_topo = None
        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setMaximumWidth(420)

        self.title_label = QLabel("ANÁLISIS DE TRANSITORIOS")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: 800; color: #ffffff; margin: 10px 0;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(self.title_label)

        self.combo_type = QComboBox()
        self.combo_type.addItems(["Circuito RL", "Circuito RC", "Circuito RLC Serie"])
        self.combo_type.setStyleSheet("font-size: 13px; font-weight: bold;")
        #self.combo_type.currentIndexChanged.connect(self.update_param_visibility)
        left_layout.addWidget(self.combo_type)
        
        self.group_topo = QGroupBox("Comportamientos Simultáneos")
        layout_topo = QVBoxLayout()
        
        self.chk_free = QCheckBox("Respuesta Libre")
        self.chk_forced = QCheckBox("Respuesta Forzada")
        self.chk_total = QCheckBox("Respuesta Total")
        
        self.chk_free.setChecked(True)
        self.chk_forced.setChecked(True)
        self.chk_total.setChecked(True)
        
        self.chk_free.toggled.connect(self.update_param_visibility)
        self.chk_forced.toggled.connect(self.update_param_visibility)
        self.chk_total.toggled.connect(self.update_param_visibility)

        layout_topo.addWidget(self.chk_free)
        layout_topo.addWidget(self.chk_forced)
        layout_topo.addWidget(self.chk_total)
        
        self.chk_taus = QCheckBox("Activar marcadores de τ (1τ - 5τ)")
        self.chk_taus.setChecked(True)
        layout_topo.addWidget(self.chk_taus)
        self.group_topo.setLayout(layout_topo)

        self.group_params = QGroupBox("Parámetros del Sistema")
        self.layout_params = QFormLayout()
        
        self.input_Rth = QLineEdit()     
        self.input_tmax = QLineEdit()  
        self.layout_params.addRow("Resistencia R_th (Ω):", self.input_Rth)
        self.layout_params.addRow("Tiempo Máximo (s):", self.input_tmax)

        self.input_L = QLineEdit()      
        self.row_L_label = QLabel("Inductancia L (H):")
        self.layout_params.addRow(self.row_L_label, self.input_L)

        self.input_i0 = QLineEdit()
        self.row_i0_label = QLabel("Corriente Inicial i_L(0) [A]:")
        self.layout_params.addRow(self.row_i0_label, self.input_i0)

        self.input_C = QLineEdit()
        self.row_C_label = QLabel("Capacitancia C (F):")
        self.layout_params.addRow(self.row_C_label, self.input_C)

        self.input_v0 = QLineEdit()
        self.row_v0_label = QLabel("Voltaje Inicial V_c(0) [V]:")
        self.layout_params.addRow(self.row_v0_label, self.input_v0)

        
        self.input_di0 = QLineEdit()
        self.row_di0_label = QLabel("Derivada Inicial di(0)/dt [A/s]:")
        self.layout_params.addRow(self.row_di0_label, self.input_di0)
        
        # Excitación
        self.input_Vth = QLineEdit()
        self.row_Vth_label = QLabel("Voltaje Thévenin V_th [V]:")
        self.layout_params.addRow(self.row_Vth_label, self.input_Vth)

        self.input_iN = QLineEdit()
        self.row_iN_label = QLabel("...Ó Corriente Norton I_N [A]:")
        self.layout_params.addRow(self.row_iN_label, self.input_iN)

        self.input_Vth.textChanged.connect(self.toggle_norton_inputs)
        self.input_iN.textChanged.connect(self.toggle_norton_inputs)

        self.group_params.setLayout(self.layout_params)

        group_info = QGroupBox("Estado Analítico")
        layout_info = QVBoxLayout()
        self.label_tau = QLabel("Constante de tiempo (τ): -")
        self.label_tau.setStyleSheet("font-weight: 600; color: #4cc2ff; font-size: 13px;")
        layout_info.addWidget(self.label_tau)
        group_info.setLayout(layout_info)
        
        self.btn_simulate = QPushButton("Ejecutar Simulación Matemática")
        self.btn_simulate.setStyleSheet("background-color: #005a9e; color: white; font-weight: bold; border: 1px solid #004578;")
        self.btn_simulate.clicked.connect(self.run_simulation)

        self.btn_export = QPushButton("Exportar Gráfica HD")
        self.btn_export.setStyleSheet("background-color: #1e4620; color: white; font-weight: bold; border: 1px solid #122b14;")
        self.btn_export.clicked.connect(self.export_plot)

        left_layout.addWidget(self.group_topo)
        left_layout.addWidget(self.group_params)
        left_layout.addWidget(group_info)
        left_layout.addStretch() 
        left_layout.addWidget(self.btn_simulate)
        left_layout.addWidget(self.btn_export)
        
        
        self.canvas = PlotCanvas(self, width=8, height=6, dpi=110)
        main_layout.addWidget(left_panel)
        main_layout.addWidget(self.canvas)
        
        self.combo_type.currentIndexChanged.connect(self.update_param_visibility)
        
        self.update_param_visibility()

    def toggle_norton_inputs(self):
        sender = self.sender()
        if sender == self.input_Vth:
            has_text = bool(self.input_Vth.text().strip())
            self.input_iN.setEnabled(not has_text)
        elif sender == self.input_iN:
            has_text = bool(self.input_iN.text().strip())
            self.input_Vth.setEnabled(not has_text)

    def set_ideal_parameters(self, current_topo):
        self.input_Vth.setText("10.0")
        self.input_iN.setText("")
        if current_topo == "Circuito RL":
            self.input_Rth.setText("50")       
            self.input_L.setText("0.1")        
            self.input_tmax.setText("0.01")    
            self.input_i0.setText("0.05")      
        elif current_topo == "Circuito RC":
            self.input_Rth.setText("1000")     
            self.input_C.setText("0.00001")    
            self.input_tmax.setText("0.05")    
            self.input_v0.setText("2.0")       
        elif current_topo == "Circuito RLC Serie":
            # Parámetros para forzar amortiguamiento crítico (R = 2*sqrt(L/C))
            self.input_Rth.setText("2")     
            self.input_L.setText("1")    
            self.input_C.setText("1")    
            self.input_tmax.setText("10")    
            self.input_i0.setText("0")
            self.input_di0.setText("5")
    
    def update_param_visibility(self):
        current_topo = self.combo_type.currentText()
        is_rl = current_topo == "Circuito RL"
        is_rc = current_topo == "Circuito RC"
        is_rlc = current_topo == "Circuito RLC Serie"
        
        # 1. Mutación Dinámica de los Checkboxes
        if is_rlc:
            self.group_topo.setTitle("Tipos de Amortiguamiento")
            self.chk_free.setText("Sobreamortiguado (Próximamente)")
            self.chk_forced.setText("Críticamente Amortiguado")
            self.chk_total.setText("Subamortiguado (Próximamente)")
            
            # Bloquear señales para evitar bucles recursivos en UI
            self.chk_free.blockSignals(True)
            self.chk_total.blockSignals(True)
            
            self.chk_free.setChecked(False)
            self.chk_free.setEnabled(False)
            
            self.chk_total.setChecked(False)
            self.chk_total.setEnabled(False)
            
            self.chk_forced.setChecked(True) # Activamos Críticamente Amortiguado por defecto
            self.chk_forced.setEnabled(True)
            
            self.chk_free.blockSignals(False)
            self.chk_total.blockSignals(False)
            
            needs_init = self.chk_forced.isChecked()
            needs_excit = False # RLC actual no tiene fuente externa en t>0
        else:
            self.group_topo.setTitle("Comportamientos Simultáneos")
            self.chk_free.setText("Respuesta Libre")
            self.chk_forced.setText("Respuesta Forzada")
            self.chk_total.setText("Respuesta Total")
            
            self.chk_free.setEnabled(True)
            self.chk_total.setEnabled(True)
            
            needs_init = self.chk_free.isChecked() or self.chk_total.isChecked()
            needs_excit = self.chk_forced.isChecked() or self.chk_total.isChecked()

        # 2. Gestión de Visibilidad de Parámetros
        self.row_L_label.setVisible(is_rl or is_rlc)
        self.input_L.setVisible(is_rl or is_rlc)
        self.row_C_label.setVisible(is_rc or is_rlc)
        self.input_C.setVisible(is_rc or is_rlc)

        self.row_i0_label.setVisible(needs_init and (is_rl or is_rlc))
        self.input_i0.setVisible(needs_init and (is_rl or is_rlc))
        self.row_v0_label.setVisible(needs_init and is_rc)
        self.input_v0.setVisible(needs_init and is_rc)
        
        self.row_di0_label.setVisible(needs_init and is_rlc)
        self.input_di0.setVisible(needs_init and is_rlc)

        self.row_Vth_label.setVisible(needs_excit and not is_rlc)
        self.input_Vth.setVisible(needs_excit and not is_rlc)
        self.row_iN_label.setVisible(needs_excit and not is_rlc)
        self.input_iN.setVisible(needs_excit and not is_rlc)
        
        if self._last_topo != current_topo:
            self.set_ideal_parameters(current_topo)
            self._last_topo = current_topo
            
    
    def extract_thevenin_voltage(self, R_th):
        if self.input_Vth.text().strip():
            return float(self.input_Vth.text())
        elif self.input_iN.text().strip():
            return float(self.input_iN.text()) * R_th
        raise ValueError("Falta parámetro de excitación: Ingrese V_th o I_N.")

    def extract_norton_current(self, R_th):
        if self.input_Vth.text().strip():
            return float(self.input_Vth.text()) / R_th
        elif self.input_iN.text().strip():
            return float(self.input_iN.text())
        raise ValueError("Falta parámetro de excitación: Ingrese V_th o I_N.")
    
    def run_simulation(self):
        try:
            R_th = float(self.input_Rth.text())
            tmax = float(self.input_tmax.text())
            if R_th <= 0: raise ValueError("R_th debe ser estrictamente mayor a 0.")

            t = np.linspace(0, tmax, 2500)
            curves = []
            current_topo = self.combo_type.currentText()

            if current_topo == "Circuito RL":
                L = float(self.input_L.text())
                tau_val = CircuitSimulator.get_tau_rl(R_th, L)
                
                if self.chk_free.isChecked():
                    i0 = float(self.input_i0.text())
                    i_t, _ = CircuitSimulator.rl_free_response(t, R_th, L, i0)
                    curves.append({'t': t, 'y': i_t, 'label': r'$i_{libre}(t) = i(0)e^{-\frac{R_{th}}{L}t}$', 'color': '#0072BD'})

                if self.chk_forced.isChecked():
                    iN = self.extract_norton_current(R_th)
                    i_t, _ = CircuitSimulator.rl_forced_response(t, R_th, L, iN)
                    curves.append({'t': t, 'y': i_t, 'label': r'$i_{forzada}(t) = I_N(1-e^{-\frac{R_{th}}{L}t})$', 'color': '#D95319'})

                if self.chk_total.isChecked():
                    i0 = float(self.input_i0.text())
                    iN = self.extract_norton_current(R_th)
                    i_t, _ = CircuitSimulator.rl_total_response(t, R_th, L, i0, iN)
                    curves.append({'t': t, 'y': i_t, 'label': r'$i_{total}(t) = i(0)e^{-\frac{R_{th}}{L}t} + I_N(1-e^{-\frac{R_{th}}{L}t})$', 'color': '#77AC30'})
                
                ylabel = 'Corriente i(t) [A]'

            elif current_topo == "Circuito RC":
                C = float(self.input_C.text())
                tau_val = CircuitSimulator.get_tau_rc(R_th, C)

                if self.chk_free.isChecked():
                    v0 = float(self.input_v0.text())
                    v_t, _ = CircuitSimulator.rc_free_response(t, R_th, C, v0)
                    curves.append({'t': t, 'y': v_t, 'label': r'$V_{c_{libre}}(t) = V_c(0)e^{-\frac{t}{RC}}$', 'color': '#0072BD'})

                if self.chk_forced.isChecked():
                    Vth = self.extract_thevenin_voltage(R_th)
                    v_t, _ = CircuitSimulator.rc_forced_response(t, R_th, C, Vth)
                    curves.append({'t': t, 'y': v_t, 'label': r'$V_{c_{forzada}}(t) = V_{Th}(1-e^{-\frac{t}{RC}})$', 'color': '#D95319'})

                if self.chk_total.isChecked():
                    v0 = float(self.input_v0.text())
                    Vth = self.extract_thevenin_voltage(R_th)
                    v_t, _ = CircuitSimulator.rc_total_response(t, R_th, C, v0, Vth)
                    curves.append({'t': t, 'y': v_t, 'label': r'$V_{c_{total}}(t) = V_c(0)e^{-\frac{t}{RC}} + V_{Th}(1-e^{-\frac{t}{RC}})$', 'color': '#77AC30'})
                
                ylabel = 'Voltaje $V_c(t)$ [V]'

            elif current_topo == "Circuito RLC Serie":
                L = float(self.input_L.text())
                C = float(self.input_C.text())
                
                # Análisis de convergencia asintótica
                alpha = R_th / (2 * L)
                omega0 = 1 / np.sqrt(L * C)

                if self.chk_forced.isChecked():
                    if not np.isclose(alpha, omega0, rtol=1e-2):
                        QMessageBox.warning(self, "Desviación Topológica", "Los parámetros ingresados no producen un sistema estrictamente críticamente amortiguado (R ≠ 2√(L/C)). La gráfica asume que α rige la envolvente.")
                    
                    i0 = float(self.input_i0.text())
                    di0 = float(self.input_di0.text())
                    i_t, tau_val = CircuitSimulator.rlc_series_critically_damped(t, R_th, L, C, i0, di0)
                    curves.append({'t': t, 'y': i_t, 'label': r'$i(t) = \left[i(0) + \left(\frac{di(0)}{dt} + \alpha i(0)\right)t\right]e^{-\alpha t}$', 'color': '#900C3F'})
                
                ylabel = 'Corriente i(t) [A]'

            if not curves:
                QMessageBox.warning(self, "Advertencia", "Seleccione al menos un comportamiento a graficar.")
                return

            self.label_tau.setText(f"Constante Asintótica Equivalente (τ): {tau_val*1000:.4f} ms")
            self.canvas.plot_simulation(curves, tau_val, show_taus=self.chk_taus.isChecked(), ylabel=ylabel)
            
        except Exception as e:
            QMessageBox.critical(self, "Error de Simulación", str(e))
    
    
    
    def export_plot(self):
        save_dir = os.path.join(os.getcwd(), "Imagenes")
        os.makedirs(save_dir, exist_ok=True)
        default_path = os.path.join(save_dir, "analisis_transitorio.png")
        
        filepath, _ = QFileDialog.getSaveFileName(self, "Guardar Gráfica HD", default_path, "PNG Files (*.png);;PDF Files (*.pdf)")
        if filepath:
            self.canvas.export_hd(filepath)