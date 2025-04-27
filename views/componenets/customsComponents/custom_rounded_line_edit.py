from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLineEdit


class CustomRoundedLineEdit(QLineEdit):
    def __init__(self, placeholder_text, parent=None):
        super().__init__(parent)

        self.placeholder_text = placeholder_text

        # self.setFixedSize(self.size)
        self.setFixedHeight(40)
        self.setPlaceholderText(self.placeholder_text)

        self.focus_in_stylesheet = """
        QLineEdit {
            border:1px solid #8D8D8D;
            border-radius:7px;
            background-color:white;
            color:black;
            padding-left:10px;
            padding-right:5px;
        }
        """
        self.base_style_sheet = """
        QLineEdit {
            border:1px solid #C7C7C7;
            border-radius:7px;
            background-color:white;
            color:#2C2D33;
            padding-left:10px;
            padding-right:5px;
        }
        """

        self.setStyleSheet(self.base_style_sheet)

    def focusInEvent(self, event):
        self.setStyleSheet(self.focus_in_stylesheet)
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        self.setStyleSheet(self.base_style_sheet)
        super().focusOutEvent(event)
