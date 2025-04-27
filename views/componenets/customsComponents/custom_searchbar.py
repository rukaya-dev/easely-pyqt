from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QPalette, QPixmap
from PyQt6.QtWidgets import QLineEdit, QHBoxLayout, QWidget, QLabel

from utils.validator import search_input_validator


class CustomSearchBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.search_bar = QLineEdit()
        self.search_bar.setValidator(search_input_validator)
        self.search_bar.setMinimumSize(QSize(200, 40))
        self.search_bar.setPlaceholderText("Search ...")
        self.search_bar.setStyleSheet(
            """
            QLineEdit {
                padding-right:2px;
                border:0;
                color:#1f1f1f;
                font-size:14px;
                background-color:transparent;
            }
            """)

        search_icon = QPixmap(":/resources/icons/search.svg")
        search_icon.scaled(QSize(17, 17), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

        search_icon_label = QLabel()
        search_icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        search_icon_label.setFixedSize(QSize(30, 30))
        search_icon_label.setStyleSheet(" QLabel { border:0; }")

        search_icon_label.setPixmap(search_icon)

        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        search_layout.setSpacing(0)

        search_layout.addWidget(search_icon_label)
        search_layout.addWidget(self.search_bar)

        widget = QWidget()
        widget.setFixedHeight(40)
        widget.setStyleSheet("""
                    border:1px solid #D0D0D1;
                    border-radius:3px;
                    background-color:transparent;
                """)
        widget.setLayout(search_layout)

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(widget)

        self.setLayout(layout)


