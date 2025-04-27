from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout

from views.componenets.customsComponents.dates_and_times.custom_time_picker import CustomTimePicker


class CustomRangeTimePicker(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.from_time_picker = CustomTimePicker()

        to_label = QLabel()
        to_label.setText("to")
        to_label.setStyleSheet("border:0;color:#757575;font-size:14px;")

        self.to_time_picker = CustomTimePicker()

        time_range_h_layout = QHBoxLayout()
        time_range_h_layout.setContentsMargins(0, 0, 0, 0)
        time_range_h_layout.setSpacing(20)
        time_range_h_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        time_range_h_layout.addWidget(self.from_time_picker)
        time_range_h_layout.addWidget(to_label)
        time_range_h_layout.addWidget(self.to_time_picker)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(time_range_h_layout)

        self.setLayout(layout)

