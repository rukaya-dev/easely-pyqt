from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout


class CleatButton(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.icon_label = QLabel(self)
        self.icon_label.setFixedSize(QSize(20, 20))

        self.button = QPushButton(self)

        font = self.button.font()
        font.setPointSize(12)
        font.setWeight(font.Weight.Medium)
        self.setFont(font)

        self.button.setFixedWidth(50)

        self.button.setText("Clear")

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        layout.setSpacing(0)

        layout.addWidget(self.icon_label)
        layout.addWidget(self.button)

        self.active_style_sheet = """
            QWidget {
                border:0;
                background-color:transparent;
                border-right:0px;
                color:#4B4E58;
            }
            QWidget:hover {
                border:1px solid #E2E2E2;
                background-color:#e2e8f0;
                border-radius:3px;
                color:#4B4E58;
            }
            
            """

        self.central_widget = QWidget()
        self.central_widget.setLayout(layout)
        self.central_widget.setStyleSheet(self.active_style_sheet)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.central_widget)

        self.setLayout(main_layout)
        self.setFixedSize(QSize(75, 35))
        self.set_active_widget_style()

    def set_active_widget_style(self):
        self.central_widget.setStyleSheet(self.active_style_sheet)

        self.icon_label.setStyleSheet("""
            QLabel {
                border:0;
                background-color:transparent;
            }
            """)

        self.button.setStyleSheet("""
        QPushButton {
            border:0;
            color:#343434;
            background-color:transparent;
        }

        """)

        icon_pixmap = QPixmap(":resources/icons/close.svg")
        self.icon_label.setPixmap(icon_pixmap)

