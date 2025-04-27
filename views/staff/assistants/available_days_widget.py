from PyQt6.QtCore import Qt, QSize, pyqtSlot
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton

from views.componenets.customsComponents.table.form_componenets.custom_label import CustomLabel


class AvailableDaysWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.available_days_data = set()
        self.available_days_buttons = []

        days = [
            {
                "name": "Sun",
                "id": "Sunday"
            },
            {
                "name": "Mon",
                "id": "Monday"
            },
            {
                "name": "Tue",
                "id": "Tuesday"
            },
            {
                "name": "Wed",
                "id": "Wednesday"
            },
            {
                "name": "Thu",
                "id": "Thursday"
            },
            {
                "name": "Fri",
                "id": "Friday"
            },
            {
                "name": "Sat",
                "id": "Saturday"
            },
        ]

        days_layout = QHBoxLayout()
        days_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        days_layout.setSpacing(20)

        self.include_these_days_label = CustomLabel("Including Days")
        self.include_these_days_label.setFixedSize(QSize(150, 30))

        days_layout.addWidget(self.include_these_days_label)
        # days_layout.addWidget(self.all_days_btn)

        for day in days:
            button = QPushButton(day["name"])

            button_id = day["id"]
            button.setProperty("id", button_id)

            button.setCheckable(True)

            button.toggled.connect(lambda state, btn=button: self.change_day_button_style(state, btn))

            # if button_id != "All":
            self.available_days_buttons.append(button)

            apply_default_style(button)
            button.setFixedSize(QSize(50, 50))

            days_layout.addWidget(button)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.setSpacing(20)

        layout.addLayout(days_layout)

        self.setLayout(layout)

    @pyqtSlot(bool, QPushButton)
    def change_day_button_style(self, state, button: QPushButton):
        color_scheme = "#2563EB; color:white;" if state else "#EDF1F5; color:#4B4E58;"
        button.setStyleSheet(f"""
            QPushButton {{
                border: 0;
                border-radius:25px;
                background-color:{color_scheme}
            }}
            """)

        if state:
            self.available_days_data.add(button.property("id"))
            # Reset All days Button
            # if self.all_days_btn.isChecked():
            #     apply_default_style(self.all_days_btn)
        else:
            if button.property("id") in self.available_days_data:
                self.available_days_data.remove(button.property("id"))


def apply_default_style(button: QPushButton):
    button.setStyleSheet("""
            QPushButton {
                border:0;
                border-radius:25px;
                background-color:#EDF1F5;
                color:#4B4E58;
            }
            """)
    button.setChecked(False)

