from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLineEdit

from utils.validator import normal_input_validator


class CustomLineEdit(QLineEdit):
    def __init__(self, placeholder_text, parent=None):
        super().__init__(parent)

        self.placeholder_text = placeholder_text

        self.setFixedHeight(40)
        self.setPlaceholderText(self.placeholder_text)

        font = self.font()
        font.setPointSize(12)
        font.setWeight(font.Weight.Normal)
        self.setFont(font)

        self.focus_in_stylesheet = """
            QLineEdit {
                border:1px solid #8D8D8D;
                border-radius:2px;
                background-color:white;
                color:black;
                padding-left:10px;
                padding-right:5px;
            }
        """
        self.base_style_sheet = """
            QLineEdit {
                border:1px solid #C7C7C7;
                border-radius:2px;
                background-color:white;
                color:black;
                padding-left:10px;
                padding-right:5px;
            }
        """

        self.setStyleSheet(self.base_style_sheet)
        self.setValidator(normal_input_validator)

    def focusInEvent(self, event):
        self.setStyleSheet(self.focus_in_stylesheet)
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        self.setStyleSheet(self.base_style_sheet)
        super().focusOutEvent(event)
