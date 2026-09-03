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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = TransientSimulatorUI()
    window.show()
    sys.exit(app.exec())