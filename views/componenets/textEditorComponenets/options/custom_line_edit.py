from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QLineEdit, QToolButton


class CustomLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setEnabled(True)
        self.setPlaceholderText("Search...")
        self.setObjectName("templates_management_table_search_bar")
        self.setStyleSheet(
            "padding-left:40px; padding-right:15px; border:1px solid #DCE0E3; border-radius:5px;font-size:14px;color:#a6a6a6;")
        self.setFixedSize(QSize(350, 40))

        search_icon = QIcon(":/resources/icons/search.svg")
        search_icon_button = QToolButton(self)
        search_icon_button.setIcon(search_icon)
        search_icon_button.setIconSize(QSize(18, 18))
        search_icon_button.setCursor(Qt.CursorShape.ArrowCursor)  # optional, for better cursor appearance
        search_icon_button.setStyleSheet(
            "border: none; padding-bottom:2px; padding-top:10px; padding-left:10px; background-color:transparent;")

