from PyQt5.QtWidgets import QApplication
from src.mainWindow import MainWindow
import sys

app = QApplication(sys.argv)
window = MainWindow()
app.exec_()
