from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout

from views.componenets.customsComponents.buttons.button_with_loader import ButtonWithLoader
from views.componenets.customsComponents.dates_and_times.custome_calender import CustomCalendarWidget


class CustomDateRangeSelection(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.parent = parent

        self.custom_date_calendar = CustomCalendarWidget()

        self.date_range_h_layout = QHBoxLayout()
        self.date_range_h_layout.setContentsMargins(20, 20, 20, 20)
        self.date_range_h_layout.setSpacing(30)
        self.date_range_h_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.date_range_h_layout.addWidget(self.custom_date_calendar)

        self.apply_btn = ButtonWithLoader(text="Apply", size=QSize(95, 34))

        apply_btn_layout = QHBoxLayout()
        apply_btn_layout.setContentsMargins(20, 20, 20, 20)
        apply_btn_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        apply_btn_layout.addWidget(self.apply_btn)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        layout.addLayout(self.date_range_h_layout, Qt.AlignmentFlag.AlignLeft)
        layout.addLayout(apply_btn_layout)
        self.setLayout(layout)
