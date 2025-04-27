from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel, QSizePolicy


class CustomLabel(QLabel):
    def __init__(self, name="Label", parent=None):
        super().__init__(parent)

        self.name = name
        self.setText(self.name)

        font = self.font()
        font.setPointSize(13)
        self.setFont(font)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        self.setStyleSheet("""
        QLabel {
            color:black;
            background-color:transparent;
        }
        """)


