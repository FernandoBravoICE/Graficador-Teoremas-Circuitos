#Punto de entrada  y ejecución de la aplicación. 
# main.py
import sys
import os
import warnings
from PyQt6.QtWidgets import QApplication
from ui_main import TransientSimulatorUI

os.environ["NO_ALBUMENTATIONS_UPDATE"] = "1"
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

WINDOWS_11_DARK_QSS = """
QMainWindow, QWidget { 
    background-color: #202020; 
    color: #ffffff; 
    font-family: 'Segoe UI', system-ui; 
    font-size: 10pt; 
}
QGroupBox {
    background-color: #2b2b2b;
    border: 1px solid #333333;
    border-radius: 8px;
    margin-top: 1.5ex;
    padding: 10px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 5px;
    color: #4cc2ff;
    font-weight: bold;
}
QLineEdit, QComboBox {
    background-color: #333333;
    border: 1px solid #444444;
    border-radius: 4px;
    padding: 6px;
    selection-background-color: #0078D4;
}
QLineEdit:disabled { 
    background-color: #1c1c1c; 
    color: #666666; 
    border: 1px solid #2a2a2a; 
}
QLineEdit:focus, QComboBox:focus { 
    border: 1px solid #4cc2ff; 
    background-color: #3a3a3a;
}
QPushButton {
    background-color: #333333;
    border: 1px solid #444444;
    border-radius: 4px;
    padding: 8px;
}
QPushButton:hover { background-color: #3d3d3d; }
QPushButton:pressed { background-color: #222222; }
QCheckBox::indicator {
    width: 16px; height: 16px;
    border: 1px solid #555555;
    border-radius: 4px;
    background-color: #2b2b2b;
}
QCheckBox::indicator:checked { 
    background-color: #4cc2ff; 
    border: 1px solid #4cc2ff; 
}
"""

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(WINDOWS_11_DARK_QSS)
    window = TransientSimulatorUI()
    window.show()
    sys.exit(app.exec())