import os
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QSizePolicy, QSpacerItem
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt, QSize


class NotFoundSearchMessageWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.imageLabel = None
        self.textLabel = None
        self.initUI()

    def initUI(self):
        # Layout
        layout = QVBoxLayout()
        # Image Label
        self.imageLabel = QLabel(self)
        pixmap = QPixmap(":resources/icons/404.svg")
        scaled_pixmap = pixmap.scaled(QSize(350, 350), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)  # Scale the pixmap
        self.imageLabel.setPixmap(scaled_pixmap)
        self.imageLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.imageLabel.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        # Text Label
        self.textLabel = QLabel('No matches found. Consider using similar words or broadening your search.', self)
        self.textLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Set a responsive font size and style
        font = self.textLabel.font()
        font.setPointSize(15)  # Example font size
        font.setBold(True)
        self.textLabel.setFont(font)

        # Apply StyleSheet for additional styling
        self.textLabel.setStyleSheet("""
                QLabel {
                    color: #555;
                    padding: 5px;
                }
            """)

        # Adding widgets to the layout
        layout.addWidget(self.imageLabel)
        layout.addWidget(self.textLabel)
        # Spacer to push the label to the top
        spacer = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addItem(spacer)

        # Set the layout on the application's window
        self.setLayout(layout)
