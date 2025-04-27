from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QVBoxLayout, QPushButton, QWidget, QHBoxLayout, QLabel


class CustomDateMenuButton(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.icon_label = QLabel(self)
        self.icon_label.setFixedSize(QSize(15, 15))
        self.icon_label.setStyleSheet("""
        QLabel {
            border:0;
            background-color:transparent;
        }
        """)
        icon_pixmap = QPixmap(":resources/icons/clock.svg")
        self.icon_label.setPixmap(icon_pixmap)

        self.button = QPushButton(self)
        self.button.setFixedWidth(100)
        self.button.setStyleSheet("""
        QPushButton {
            border:0;
            color:#343434;
            background-color:transparent;
        }
        """)
        self.button.setText("Last 24 hours")

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        layout.setSpacing(0)

        layout.addWidget(self.icon_label)
        layout.addWidget(self.button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        central_widget.setStyleSheet("""
        QWidget {
            border:1px solid #E2E2E2;
            border-radius:7px;
            border-top-right-radius:0px;
            border-bottom-right-radius:0px;
            background-color:white;
            border-right:0px;
        }
        QWidget::hover {
            background-color:#ededed;
        }
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(central_widget)

        self.setLayout(main_layout)
        self.setFixedSize(QSize(135, 35))
