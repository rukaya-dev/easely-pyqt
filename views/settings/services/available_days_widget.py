from PyQt6.QtCore import Qt, QSize, pyqtSlot
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton

class AvailableDaysWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.available_days_data = []
        self.available_days_buttons = []

        self.days = [
            {
                "name": "Sunday",
            },
            {
                "name": "Monday",

            },
            {
                "name": "Tuesday",

            },
            {
                "name": "Wednesday",

            },
            {
                "name": "Thursday",

            },
            {
                "name": "Friday",

            },
            {
                "name": "Saturday",

            },
        ]

        days_layout = QHBoxLayout()
        days_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        days_layout.setSpacing(20)

        font = QFont()
        font.setPixelSize(18)
        font.setWeight(QFont.Weight.Bold)

        for day in self.days:
            button = QPushButton(day["name"][:3])
            self.configure_button(button, day)
            self.available_days_buttons.append(button)
            days_layout.addWidget(button)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.setSpacing(20)

        layout.addLayout(days_layout)

        self.setLayout(layout)

    @pyqtSlot(bool, QPushButton)
    def change_day_button_style(self, state, button: QPushButton):
        if state:
            apply_active_button_style(button)
            self.available_days_data.append(button.objectName())
        else:
            if button.objectName() in self.available_days_data:
                self.available_days_data.remove(button.objectName())
            apply_default_style(button)

    def configure_button(self, button, day):
        button.setCheckable(True)
        button.setFixedSize(QSize(50, 50))
        apply_default_style(button)

        button.setObjectName(day["name"])

        button.toggled.connect(lambda state, btn=button: self.change_day_button_style(state, btn))

    def connect_day_button_toggled_signal(self, state, day_button: QPushButton):
        return lambda: self.change_day_button_style(state, day_button)


def apply_active_button_style(button: QPushButton):
    font = button.font()
    font.setPixelSize(14)
    font.setWeight(QFont.Weight.DemiBold)
    button.setFont(font)

    button.setStyleSheet("""
            QPushButton {
                border:0;
                border-radius:24px;
                background-color:#fbbf24;
                color:white;
            }
            """)
    button.setProperty("is_active", True)


def apply_default_style(button: QPushButton):
    button.setStyleSheet("""
            QPushButton {
                border:1px solid #E3E3E3;
                border-radius:25px;
                background-color:white;
                color:#4B4E58;
            }
            """)
    button.setChecked(False)


