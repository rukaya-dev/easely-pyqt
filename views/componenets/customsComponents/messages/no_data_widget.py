import os
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QSizePolicy, QSpacerItem
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt, QSize


class NoDataWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.imageLabel = QLabel(self)

        self.pixmap = QPixmap(":resources/icons/no_data.svg")
        scaled_pixmap = self.pixmap.scaled(QSize(275, 275), Qt.AspectRatioMode.KeepAspectRatio,
                                           Qt.TransformationMode.SmoothTransformation)

        self.imageLabel.setPixmap(scaled_pixmap)
        self.imageLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.imageLabel.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

        self.textLabel = QLabel('No data', self)
        self.textLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        font = self.textLabel.font()
        font.setPixelSize(15)
        font.setWeight(QFont.Weight.Medium)
        self.textLabel.setFont(font)

        self.textLabel.setStyleSheet("""
                QLabel {
                    color: #2C2D33;
                    padding: 5px;
                    border:0;
                }
            """)

        layout.addWidget(self.imageLabel)
        layout.addWidget(self.textLabel)

        spacer = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addItem(spacer)

        self.setLayout(layout)
