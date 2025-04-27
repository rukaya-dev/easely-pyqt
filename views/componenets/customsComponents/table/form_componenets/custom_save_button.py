from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QPushButton


class CustomSaveButton(QPushButton):
    def __init__(self, size, name, parent=None):
        super().__init__(parent)

        self.size = size
        self.name = name

        self.setFixedSize(self.size)
        self.setText(self.name)

        self.base_style_sheet = """
        QPushButton {
            border:0;
            background-color:#003445;
            color:#F5F5F5;
        }
        """

        self.setStyleSheet(self.base_style_sheet)

