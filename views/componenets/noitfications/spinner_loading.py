from PyQt6.QtWidgets import QWidget, QGraphicsDropShadowEffect, QHBoxLayout, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor

from views.componenets.customsComponents.loaders.internal_loader import InternalLoader


class SpinnerLoading(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.loading_spinner = None

        self.setFixedSize(QSize(150, 80))
        self.setStyleSheet("background-color: #F6F8FA;")

        # Create and apply the shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 60))
        self.setGraphicsEffect(shadow)

        # Ensure the spinner has the right window flags if floating above all widgets
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        # self.setAttribute(Qt.WindowType.WA_TranslucentBackground)

        # Label

        label = QLabel()
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setText("Loading")
        label.setStyleSheet("color: black;font-size:14pt;")

        # Loading Spinner
        self.loading_spinner = InternalLoader(height=25)

        loading_layout = QHBoxLayout()
        loading_layout.setSpacing(0)
        loading_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        loading_layout.addWidget(self.loading_spinner)
        loading_layout.addWidget(label)

        spinner_widget = QWidget()
        spinner_widget.setLayout(loading_layout)

        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)

        self.layout.addWidget(spinner_widget)
        self.setLayout(self.layout)
