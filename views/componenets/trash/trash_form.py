from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from views.componenets.customsComponents.table.form_componenets.custom_input import CustomLineEdit
from views.componenets.customsComponents.table.form_componenets.custom_label import CustomLabel
from views.componenets.customsComponents.table.form_componenets.custom_text_edit import CustomTextEdit


class TrashForm(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.main_vertical_layout = QVBoxLayout()
        self.main_vertical_layout.setContentsMargins(0, 0, 0, 0)
        self.main_vertical_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.main_vertical_layout.setSpacing(32)

        deleted_by_label = CustomLabel(name="Deleted by")

        self.deleted_by_input = CustomLineEdit(placeholder_text="", parent=self)

        deleted_by_vertical_layout = QVBoxLayout()
        deleted_by_vertical_layout.setContentsMargins(0, 0, 0, 0)
        deleted_by_vertical_layout.setSpacing(10)

        deleted_by_vertical_layout.addWidget(deleted_by_label)
        deleted_by_vertical_layout.addWidget(self.deleted_by_input)

        deleted_at_label = CustomLabel(name="Deleted At")

        self.deleted_at_input = CustomLineEdit(placeholder_text="", parent=self)

        deleted_at_vertical_layout = QVBoxLayout()
        deleted_at_vertical_layout.setContentsMargins(0, 0, 0, 0)
        deleted_at_vertical_layout.setSpacing(10)

        deleted_at_vertical_layout.addWidget(deleted_at_label)
        deleted_at_vertical_layout.addWidget(self.deleted_at_input)

        patient_info_label = CustomLabel(name="Patient Info")

        self.patient_info_input = CustomTextEdit(border_radius=2,placeholder_text="", parent=self)

        patient_info_vertical_layout = QVBoxLayout()
        patient_info_vertical_layout.setContentsMargins(0, 0, 0, 0)
        patient_info_vertical_layout.setSpacing(10)

        patient_info_vertical_layout.addWidget(patient_info_label)
        patient_info_vertical_layout.addWidget(self.patient_info_input)

        central_widget = QWidget()
        central_widget.setMinimumWidth(400)
        central_widget.setLayout(self.main_vertical_layout)

        self.main_vertical_layout.addLayout(deleted_by_vertical_layout)
        self.main_vertical_layout.addLayout(deleted_at_vertical_layout)
        self.main_vertical_layout.addLayout(patient_info_vertical_layout)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(central_widget)

        self.setLayout(layout)
