import sys
import numpy as np
import sympy as sp
from sympy.parsing.latex import parse_latex
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QGroupBox, QMessageBox, QFormLayout, QComboBox, 
                             QFileDialog, QTabWidget)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPainter, QPen, QColor

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class MathParser:
    """Motor matemático optimizado con SymPy."""
    def __init__(self):
        self.t, self.R, self.L, self.C = sp.symbols('t R L C', real=True)
        self.transformations = standard_transformations + (implicit_multiplication_application,)

    def parse_and_lambdify(self, expression_str, is_latex=False):
        try:
            if is_latex:
                expr = parse_latex(expression_str)
            else:
                expr = parse_expr(expression_str, transformations=self.transformations)
            
            func = sp.lambdify((self.t, self.R, self.L, self.C), expr, modules=['numpy'])
            return func, expr
        except Exception as e:
            raise ValueError(f"Error de sintaxis matemática: {str(e)}")


class DrawingCanvas(QWidget):
    """Lienzo vectorial para captura de trazos a mano alzada."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 200);
        self.setStyleSheet("background-color: white; border: 1px solid #ccc;")
        self.points = []
        self.drawing = False

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = True
            self.points.append(event.pos())

    def mouseMoveEvent(self, event):
        if self.drawing and (event.buttons() & Qt.MouseButton.LeftButton):
            self.points.append(event.pos())
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False

    def paintEvent(self, event):
        canvas = QPainter(self)
        pen = QPen(QColor(31, 119, 180), 2, Qt.PenStyle.SolidLine)
        canvas.setPen(pen)
        
        for i in range(1, len(self.points)):
            canvas.drawLine(self.points[i - 1], self.points[i])

    def clear_canvas(self):
        self.points.clear()
        self.update()


class PlotCanvas(FigureCanvas):
    """Lienzo científico Matplotlib con soporte de exportación HD."""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)
        self.configure_axis()

    def configure_axis(self):
        self.axes.set_xlabel('Tiempo (s)')
        self.axes.set_ylabel('Amplitud')
        self.axes.grid(True, linestyle='--', alpha=0.7)
        self.fig.tight_layout()

    def plot_signal(self, t_array, y_array, latex_label):
        self.axes.clear()
        self.axes.plot(t_array, y_array, color='#1f77b4', linewidth=2, label=f"${latex_label}$")
        self.configure_axis()
        self.axes.legend(loc='upper right')
        self.draw()

    def export_hd(self, filepath):
        self.fig.savefig(filepath, dpi=300, bbox_inches='tight')


class TransientAnalyzerUI(QMainWindow):
    """Interfaz Gráfica Principal Avanzada."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Análisis de Circuitos - Estado Transitorio (HD)")
        self.setGeometry(100, 100, 1100, 650)
        
        self.parser = MathParser()
        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        # Panel Izquierdo: Controles y Pestañas
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setMaximumWidth(400)

        # Parámetros del Circuito
        group_params = QGroupBox("Parámetros Físicos")
        layout_params = QFormLayout()
        
        self.input_R = QLineEdit("1000")
        self.input_L = QLineEdit("0.1")
        self.input_C = QLineEdit("0.000001")
        self.input_tmax = QLineEdit("0.05")
        
        layout_params.addRow("Resistencia (Ω):", self.input_R)
        layout_params.addRow("Inductancia (H):", self.input_L)
        layout_params.addRow("Capacitancia (F):", self.input_C)
        layout_params.addRow("Tiempo Max (s):", self.input_tmax)
        group_params.setLayout(layout_params)

        # Pestañas de Entrada (Analítico vs Trazos a Mano)
        self.tabs = QTabWidget()
        
        # Tab 1: Expresión Matemática
        tab_math = QWidget()
        layout_math = QVBoxLayout(tab_math)
        self.combo_type = QComboBox()
        self.combo_type.addItems(["Texto Plano (Standard)", "LaTeX"])
        self.input_func = QLineEdit("exp(-t/(R*C))")
        self.input_func.setPlaceholderText("Ej: exp(-t/(R*C)) o \\sqrt{2*t}")
        
        layout_math.addWidget(QLabel("Formato:"))
        layout_math.addWidget(self.combo_type)
        layout_math.addWidget(QLabel("Función f(t, R, L, C):"))
        layout_math.addWidget(self.input_func)
        
        # Tab 2: Trazos a Mano
        tab_draw = QWidget()
        layout_draw = QVBoxLayout(tab_draw)
        self.drawing_canvas = DrawingCanvas()
        btn_clear_draw = QPushButton("Limpiar Trazo")
        btn_clear_draw.clicked.connect(self.drawing_canvas.clear_canvas)
        layout_draw.addWidget(QLabel("Dibuja la señal transitoria:"))
        layout_draw.addWidget(self.drawing_canvas)
        layout_draw.addWidget(btn_clear_draw)

        self.tabs.addTab(tab_math, "Modelo Matemático")
        self.tabs.addTab(tab_draw, "Trazo Libre")

        # Botones de Acción
        self.btn_plot = QPushButton("Graficar Señal")
        self.btn_plot.setStyleSheet("background-color: #2b5b84; color: white; font-weight: bold; padding: 10px;")
        self.btn_plot.clicked.connect(self.generate_plot)

        self.btn_export = QPushButton("Exportar Gráfica HD (300 DPI)")
        self.btn_export.setStyleSheet("background-color: #2e7d32; color: white; font-weight: bold; padding: 10px;")
        self.btn_export.clicked.connect(self.export_plot)

        left_layout.addWidget(group_params)
        left_layout.addWidget(self.tabs)
        left_layout.addWidget(self.btn_plot)
        left_layout.addWidget(self.btn_export)

        # Panel Derecho: Gráfico
        self.canvas = PlotCanvas(self, width=6, height=5, dpi=100)

        main_layout.addWidget(left_panel)
        main_layout.addWidget(self.canvas)

    def generate_plot(self):
        try:
            R_val = float(self.input_R.text())
            L_val = float(self.input_L.text())
            C_val = float(self.input_C.text())
            t_max = float(self.input_tmax.text())
            
            t_array = np.linspace(0, t_max, 1000)
            
            func_str = self.input_func.text()
            is_latex = self.combo_type.currentIndex() == 1
            
            func, sympy_expr = self.parser.parse_and_lambdify(func_str, is_latex)
            latex_label = sp.latex(sympy_expr)
            
            y_array = func(t_array, R_val, L_val, C_val)
            
            if np.isscalar(y_array):
                y_array = np.ones_like(t_array) * y_array

            self.canvas.plot_signal(t_array, y_array, latex_label)

        except Exception as e:
            QMessageBox.critical(self, "Error de Ejecución", str(e))

    def export_plot(self):
        filepath, _ = QFileDialog.getSaveFileName(self, "Guardar Gráfica HD", "", "PNG Files (*.png);;PDF Files (*.pdf)")
        if filepath:
            self.canvas.export_hd(filepath)
            QMessageBox.information(self, "Exportación Exitosa", f"Archivo guardado en:\n{filepath}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = TransientAnalyzerUI()
    window.show()
    sys.exit(app.exec())