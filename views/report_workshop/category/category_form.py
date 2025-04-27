from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QWidget, QVBoxLayout

from utils.validator import normal_input_validator
from views.componenets.customsComponents.table.form_componenets.custom_input import CustomLineEdit
from views.componenets.customsComponents.table.form_componenets.custom_label import CustomLabel


class CategoryForm(QWidget):
    def __init__(self):
        super().__init__()

        self.main_vertical_layout = QVBoxLayout()
        self.main_vertical_layout.setContentsMargins(0, 0, 0, 0)
        self.main_vertical_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.main_vertical_layout.setSpacing(32)

        name_label = CustomLabel(name="Name")

        self.name_input = CustomLineEdit(placeholder_text="name", parent=self)
        self.name_input.setValidator(normal_input_validator)

        name_vertical_layout = QVBoxLayout()
        name_vertical_layout.setSpacing(10)

        name_vertical_layout.addWidget(name_label)
        name_vertical_layout.addWidget(self.name_input)

        desc_label = CustomLabel(name="Description")

        self.desc_input = CustomLineEdit(placeholder_text="description", parent=self)
        self.desc_input.setValidator(normal_input_validator)

        desc_vertical_layout = QVBoxLayout()
        desc_vertical_layout.setSpacing(10)

        desc_vertical_layout.addWidget(desc_label)
        desc_vertical_layout.addWidget(self.desc_input)

        self.main_vertical_layout.addLayout(name_vertical_layout)
        self.main_vertical_layout.addLayout(desc_vertical_layout)

        self.setLayout(self.main_vertical_layout)
        self.setFixedWidth(500)
