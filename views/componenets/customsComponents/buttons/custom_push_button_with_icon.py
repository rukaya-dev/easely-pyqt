from PyQt6.QtWidgets import QPushButton
from PyQt6.QtGui import QIcon, QFont, QPixmap
from PyQt6.QtCore import QSize


class CustomAddButton(QPushButton):

    def __init__(self, icon_path, text, parent=None):
        super().__init__(text, parent)

        font = self.font()
        font.setPointSize(12)
        font.setWeight(QFont.Weight.Medium)
        self.setFont(font)

        self.setStyleSheet(""" 
            border-radius: 3px; 
            background-color: #2563EB; 
            color: white;
        """)

        icon_pixmap = QPixmap(icon_path)
        icon = QIcon(icon_pixmap)

        self.setIcon(icon)
        self.setIconSize(QSize(22, 22))
        self.setFixedSize(QSize(107, 30))
        self.setCheckable(True)
