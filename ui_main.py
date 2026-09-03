# ui_main.py
import numpy as np
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QGroupBox, 
                             QMessageBox, QFormLayout, QFileDialog, QComboBox)
from PyQt6.QtCore import Qt
from circuits_models import CircuitSimulator
from plot_engine import PlotCanvas, SchematicCanvas

class TransientSimulatorUI(QMainWindow):
    def __init__(self):
        super().__init__()
        # Expansión de resolución base
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

        group_topo = QGroupBox("Tipo de Análisis")
        layout_topo = QVBoxLayout()
        self.combo_circuit = QComboBox()
        self.combo_circuit.addItems([
            "Respuesta Libre RL (Vth = 0)", 
            "Próximamente: Respuesta Libre RC", 
            "Próximamente: Respuesta Forzada"
        ])
        layout_topo.addWidget(self.combo_circuit)
        group_topo.setLayout(layout_topo)

        group_params = QGroupBox("Parámetros del Sistema (RL)")
        layout_params = QFormLayout()
        
        self.input_Rth = QLineEdit("50")     
        self.input_L = QLineEdit("0.1")      
        self.input_i0 = QLineEdit("2.0")     
        self.input_tmax = QLineEdit("0.015")  
        
        layout_params.addRow("Resistencia Thévenin R_th (Ω):", self.input_Rth)
        layout_params.addRow("Inductancia L (H):", self.input_L)
        layout_params.addRow("Corriente Inicial i_L(0) (A):", self.input_i0)
        layout_params.addRow("Tiempo Máximo (s):", self.input_tmax)
        
        group_params.setLayout(layout_params)

        group_info = QGroupBox("Resultados Analíticos (τ = L / R_th)")
        layout_info = QVBoxLayout()
        self.label_tau = QLabel("Constante de tiempo (τ): -")
        self.label_tau.setStyleSheet("font-weight: bold; color: #333; font-size: 13px;")
        layout_info.addWidget(self.label_tau)
        group_info.setLayout(layout_info)

        # Inserción del lienzo del esquemático en el panel izquierdo
        self.schematic_canvas = SchematicCanvas(self, width=3, height=2.5, dpi=100)
        
        self.btn_simulate = QPushButton("Ejecutar Simulación Matemática")
        self.btn_simulate.setStyleSheet("background-color: #2b5b84; color: white; font-weight: bold; padding: 10px;")
        self.btn_simulate.clicked.connect(self.run_simulation)

        self.btn_export = QPushButton("Exportar Gráfica HD")
        self.btn_export.setStyleSheet("background-color: #2e7d32; color: white; font-weight: bold; padding: 10px;")
        self.btn_export.clicked.connect(self.export_plot)

        left_layout.addWidget(group_topo)
        left_layout.addWidget(group_params)
        left_layout.addWidget(group_info)
        left_layout.addWidget(self.schematic_canvas) # Diagrama de circuito aquí
        left_layout.addStretch() # Empuja botones al fondo o agrupa
        left_layout.addWidget(self.btn_simulate)
        left_layout.addWidget(self.btn_export)

        # Lienzo principal dedicado únicamente a la gráfica
        self.canvas = PlotCanvas(self, width=8, height=6, dpi=110)
        main_layout.addWidget(left_panel)
        main_layout.addWidget(self.canvas)

    def run_simulation(self):
        try:
            if self.combo_circuit.currentIndex() != 0:
                QMessageBox.information(self, "Aviso", "Módulo en desarrollo. Seleccione 'Respuesta Libre RL'.")
                self.combo_circuit.setCurrentIndex(0)
                return

            R_th = float(self.input_Rth.text())
            L = float(self.input_L.text())
            i0 = float(self.input_i0.text())
            tmax = float(self.input_tmax.text())
            
            t = np.linspace(0, tmax, 2500)
            i_t, tau = CircuitSimulator.rl_free_response(t, R_th, L, i0)
            
            self.label_tau.setText(f"Constante de tiempo (τ): {tau*1000:.4f} ms")
            self.canvas.plot_simulation(t, i_t, tau, i0)
        except Exception as e:
            QMessageBox.critical(self, "Error de Simulación", str(e))

    def export_plot(self):
        filepath, _ = QFileDialog.getSaveFileName(self, "Guardar Gráfica HD", "", "PNG Files (*.png);;PDF Files (*.pdf)")
        if filepath:
            self.canvas.export_hd(filepath)