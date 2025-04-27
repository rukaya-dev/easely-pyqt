from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel, QWidget, QHBoxLayout


class CustomLabelWithIcon(QWidget):
    def __init__(self, name, icon_path, icon_size, parent=None):
        super().__init__(parent)

        self.label = QLabel(name)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
         QLabel {
                  border:0;
                  background-color:transparent;
                  color:black;
              }
        """)

        pixmap = QPixmap(icon_path)
        scaled_pixmap = pixmap.scaled(icon_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

        self.icon_label = QLabel()
        self.icon_label.setPixmap(scaled_pixmap)
        self.icon_label.setStyleSheet("""
               QLabel {
                        border:0;
                        background-color:transparent;
                    }
              """)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(5)

        layout.addWidget(self.icon_label, 0, Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.label, 1, Qt.AlignmentFlag.AlignLeft)

        self.setLayout(layout)
