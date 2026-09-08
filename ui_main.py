# ui_main.py
import numpy as np
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QGroupBox, 
                            QMessageBox, QFormLayout, QFileDialog, QCheckBox)
from PyQt6.QtCore import Qt
from circuits_models import CircuitSimulator
from plot_engine import PlotCanvas

class TransientSimulatorUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Analizador de Circuitos - Estado Transitorio (MATLAB Style)")
        self.setGeometry(50, 50, 1250, 800)
        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setMaximumWidth(400)

        title_label = QLabel("ANÁLISIS ESTADO TRANSITORIO\nCIRCUITOS RL")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #58a6ff; margin: 15px 0;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(title_label)

        group_topo = QGroupBox("Comportamientos Simultáneos")
        layout_topo = QVBoxLayout()
        
        self.chk_free = QCheckBox("Respuesta Libre")
        self.chk_forced = QCheckBox("Respuesta Forzada")
        self.chk_total = QCheckBox("Respuesta Total")
        
        # Activar los 3 por defecto para evidenciar el cambio
        self.chk_free.setChecked(True)
        self.chk_forced.setChecked(True)
        self.chk_total.setChecked(True)
        
        self.chk_free.toggled.connect(self.update_param_visibility)
        self.chk_forced.toggled.connect(self.update_param_visibility)
        self.chk_total.toggled.connect(self.update_param_visibility)

        layout_topo.addWidget(self.chk_free)
        layout_topo.addWidget(self.chk_forced)
        layout_topo.addWidget(self.chk_total)
        
        self.chk_taus = QCheckBox("Activar análisis de τ (puntos críticos)")
        self.chk_taus.setChecked(True)
        layout_topo.addWidget(self.chk_taus)

        group_topo.setLayout(layout_topo)

        group_params = QGroupBox("Parámetros del Sistema (RL)")
        self.layout_params = QFormLayout()
        
        # NUEVOS PARÁMETROS DE PRUEBA: Tmax ajustado a 5 Tau
        self.input_Rth = QLineEdit("50")     
        self.input_L = QLineEdit("0.1")      
        self.input_tmax = QLineEdit("0.01")  
        
        self.layout_params.addRow("Resistencia R_th (Ω):", self.input_Rth)
        self.layout_params.addRow("Inductancia L (H):", self.input_L)
        self.layout_params.addRow("Tiempo Máximo (s):", self.input_tmax)

        # NUEVOS PARÁMETROS DE PRUEBA: i(0) = 1.0A, I_N = 3.0A
        self.input_i0 = QLineEdit("1.0")
        self.row_i0_label = QLabel("Corriente Inicial i_L(0) [A]:")
        self.layout_params.addRow(self.row_i0_label, self.input_i0)

        self.input_iN = QLineEdit("3.0")
        self.row_iN_label = QLabel("Corriente Norton I_N [A]:")
        self.layout_params.addRow(self.row_iN_label, self.input_iN)

        self.input_Vth = QLineEdit("")
        self.row_Vth_label = QLabel("...Ó Voltaje Thévenin V_th [V]:")
        self.layout_params.addRow(self.row_Vth_label, self.input_Vth)

        self.input_iN.textChanged.connect(self.toggle_norton_inputs)
        self.input_Vth.textChanged.connect(self.toggle_norton_inputs)

        group_params.setLayout(self.layout_params)

        group_info = QGroupBox("Resultados Analíticos")
        layout_info = QVBoxLayout()
        self.label_tau = QLabel("Constante de tiempo (τ): -")
        self.label_tau.setStyleSheet("font-weight: bold; color: #333; font-size: 13px;")
        layout_info.addWidget(self.label_tau)
        group_info.setLayout(layout_info)
        
        self.btn_simulate = QPushButton("Ejecutar Simulación Matemática")
        self.btn_simulate.setStyleSheet("background-color: #2b5b84; color: white; font-weight: bold; padding: 10px;")
        self.btn_simulate.clicked.connect(self.run_simulation)

        self.btn_export = QPushButton("Exportar Gráfica HD")
        self.btn_export.setStyleSheet("background-color: #2e7d32; color: white; font-weight: bold; padding: 10px;")
        self.btn_export.clicked.connect(self.export_plot)

        left_layout.addWidget(group_topo)
        left_layout.addWidget(group_params)
        left_layout.addWidget(group_info)
        left_layout.addStretch() 
        left_layout.addWidget(self.btn_simulate)
        left_layout.addWidget(self.btn_export)

        self.canvas = PlotCanvas(self, width=8, height=6, dpi=110)
        main_layout.addWidget(left_panel)
        main_layout.addWidget(self.canvas)

        self.update_param_visibility()

    def toggle_norton_inputs(self):
        sender = self.sender()
        if sender == self.input_iN:
            has_text = bool(self.input_iN.text().strip())
            self.input_Vth.setEnabled(not has_text)
            self.input_Vth.setStyleSheet("background-color: #d3d3d3;" if has_text else "")
        elif sender == self.input_Vth:
            has_text = bool(self.input_Vth.text().strip())
            self.input_iN.setEnabled(not has_text)
            self.input_iN.setStyleSheet("background-color: #d3d3d3;" if has_text else "")

    def update_param_visibility(self):
        needs_i0 = self.chk_free.isChecked() or self.chk_total.isChecked()
        self.row_i0_label.setVisible(needs_i0)
        self.input_i0.setVisible(needs_i0)

        needs_iN = self.chk_forced.isChecked() or self.chk_total.isChecked()
        self.row_iN_label.setVisible(needs_iN)
        self.input_iN.setVisible(needs_iN)
        self.row_Vth_label.setVisible(needs_iN)
        self.input_Vth.setVisible(needs_iN)

    def extract_norton_current(self, R_th):
        if self.input_iN.text().strip():
            return float(self.input_iN.text())
        elif self.input_Vth.text().strip():
            return float(self.input_Vth.text()) / R_th
        else:
            raise ValueError("Falta parámetro de excitación: Ingrese I_N o V_th.")

    def run_simulation(self):
        try:
            R_th = float(self.input_Rth.text())
            L = float(self.input_L.text())
            tmax = float(self.input_tmax.text())
            
            if R_th <= 0:
                raise ValueError("R_th debe ser estrictamente mayor a 0.")

            t = np.linspace(0, tmax, 2500)
            curves = []
            tau_val = L / R_th
            
            if self.chk_free.isChecked():
                i0 = float(self.input_i0.text())
                i_t, _ = CircuitSimulator.rl_free_response(t, R_th, L, i0)
                curves.append({'t': t, 'i': i_t, 'label': r'$i_{libre}(t) = i(0)e^{-\frac{R_{th}}{L}t}$', 'color': '#0072BD'})

            if self.chk_forced.isChecked():
                iN = self.extract_norton_current(R_th)
                i_t, _ = CircuitSimulator.rl_forced_response(t, R_th, L, iN)
                curves.append({'t': t, 'i': i_t, 'label': r'$i_{forzada}(t) = I_N(1-e^{-\frac{R_{th}}{L}t})$', 'color': '#D95319'})

            if self.chk_total.isChecked():
                i0 = float(self.input_i0.text())
                iN = self.extract_norton_current(R_th)
                i_t, _ = CircuitSimulator.rl_total_response(t, R_th, L, i0, iN)
                # Ecuación completa implementada aquí
                curves.append({'t': t, 'i': i_t, 'label': r'$i_{total}(t) = i(0)e^{-\frac{R_{th}}{L}t} + I_N(1-e^{-\frac{R_{th}}{L}t})$', 'color': '#77AC30'})

            if not curves:
                QMessageBox.warning(self, "Advertencia", "Seleccione al menos un comportamiento a graficar.")
                return

            self.label_tau.setText(f"Constante de tiempo (τ): {tau_val*1000:.4f} ms")
            self.canvas.plot_simulation(curves, tau_val, show_taus=self.chk_taus.isChecked())
            
        except Exception as e:
            QMessageBox.critical(self, "Error de Simulación", str(e))

    def export_plot(self):
        filepath, _ = QFileDialog.getSaveFileName(self, "Guardar Gráfica HD", "", "PNG Files (*.png);;PDF Files (*.pdf)")
        if filepath:
            self.canvas.export_hd(filepath)