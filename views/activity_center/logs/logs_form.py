from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from utils.validator import AgeIntValidator, PhoneNumberValidator
from views.componenets.customsComponents.table.form_componenets.custom_input import CustomLineEdit
from views.componenets.customsComponents.table.form_componenets.custom_label import CustomLabel
from views.componenets.customsComponents.table.form_componenets.custom_text_edit import CustomTextEdit


class LogForm(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.int_validator = AgeIntValidator()
        self.phone_number_validator = PhoneNumberValidator()

        self.main_vertical_layout = QVBoxLayout()
        self.main_vertical_layout.setContentsMargins(0, 0, 0, 0)
        self.main_vertical_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.main_vertical_layout.setSpacing(32)

        action_type_label = CustomLabel(name="Action type")

        self.action_type_input = CustomLineEdit(placeholder_text="", parent=self)

        action_type_vertical_layout = QVBoxLayout()
        action_type_vertical_layout.setSpacing(10)

        action_type_vertical_layout.addWidget(action_type_label)
        action_type_vertical_layout.addWidget(self.action_type_input)

        # Patient Age
        self.model_name = CustomLabel(name="Model name")

        self.model_name_input = CustomLineEdit(placeholder_text="", parent=self)
        self.model_name_input.setValidator(self.int_validator)

        model_name_vertical_layout = QVBoxLayout()
        model_name_vertical_layout.setContentsMargins(0, 0, 0, 0)
        model_name_vertical_layout.setSpacing(10)
        model_name_vertical_layout.addWidget(self.model_name)
        model_name_vertical_layout.addWidget(self.model_name_input)

        changed_by_label = CustomLabel(name="Changed by")

        self.changed_by_input = CustomLineEdit(placeholder_text="", parent=self)

        changed_by_vertical_layout = QVBoxLayout()
        changed_by_vertical_layout.setContentsMargins(0, 0, 0, 0)
        changed_by_vertical_layout.setSpacing(10)

        changed_by_vertical_layout.addWidget(changed_by_label)
        changed_by_vertical_layout.addWidget(self.changed_by_input)

        change_date_label = CustomLabel(name="Change date")

        self.change_date_input = CustomLineEdit(placeholder_text="", parent=self)

        change_date_vertical_layout = QVBoxLayout()
        change_date_vertical_layout.setContentsMargins(0, 0, 0, 0)
        change_date_vertical_layout.setSpacing(10)

        change_date_vertical_layout.addWidget(change_date_label)
        change_date_vertical_layout.addWidget(self.change_date_input)

        data_label = CustomLabel(name="Data")

        self.data_input = CustomTextEdit(border_radius=2,placeholder_text="", parent=self)

        data_vertical_layout = QVBoxLayout()
        data_vertical_layout.setContentsMargins(0, 0, 0, 0)
        data_vertical_layout.setSpacing(10)

        data_vertical_layout.addWidget(data_label)
        data_vertical_layout.addWidget(self.data_input)

        status_label = CustomLabel(name="Status")

        self.status_input = CustomLineEdit(placeholder_text="", parent=self)

        status_vertical_layout = QVBoxLayout()
        status_vertical_layout.setContentsMargins(0, 0, 0, 0)
        status_vertical_layout.setSpacing(10)

        status_vertical_layout.addWidget(status_label)
        status_vertical_layout.addWidget(self.status_input)

        central_widget = QWidget()
        central_widget.setMinimumWidth(400)
        central_widget.setLayout(self.main_vertical_layout)

        self.main_vertical_layout.addLayout(action_type_vertical_layout)
        self.main_vertical_layout.addLayout(model_name_vertical_layout)
        self.main_vertical_layout.addLayout(changed_by_vertical_layout)
        self.main_vertical_layout.addLayout(change_date_vertical_layout)
        self.main_vertical_layout.addLayout(status_vertical_layout)
        self.main_vertical_layout.addLayout(data_vertical_layout)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(central_widget)

        self.setLayout(layout)
