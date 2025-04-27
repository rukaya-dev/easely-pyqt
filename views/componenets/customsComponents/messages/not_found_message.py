import os
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QSizePolicy, QSpacerItem
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt, QSize


class NotFoundMessageWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.imageLabel = QLabel(self)

        self.pixmap = QPixmap(":resources/icons/empty.svg")
        scaled_pixmap = self.pixmap.scaled(QSize(350, 350), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

        self.imageLabel.setPixmap(scaled_pixmap)
        self.imageLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.imageLabel.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

        self.textLabel = QLabel('Sorry, the item you are looking for was not found.', self)
        self.textLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        font = self.textLabel.font()
        font.setPointSize(15)
        font.setBold(True)
        self.textLabel.setFont(font)

        self.textLabel.setStyleSheet("""
                QLabel {
                    color: #555;
                    padding: 5px;
                    border:0;
                }
            """)

        layout = QVBoxLayout()

        layout.addWidget(self.imageLabel)
        layout.addWidget(self.textLabel)

        spacer = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addItem(spacer)

        self.setLayout(layout)
