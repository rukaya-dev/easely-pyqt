from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from views.componenets.customsComponents.custom_scroll_area import CustomScrollArea
from views.componenets.customsComponents.table.form_componenets.custom_input import CustomLineEdit
from views.componenets.customsComponents.table.form_componenets.custom_label import CustomLabel
from views.componenets.customsComponents.table.form_componenets.custom_text_edit import CustomTextEdit


class LogForm(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.main_vertical_layout = QVBoxLayout()
        self.main_vertical_layout.setContentsMargins(0, 0, 20, 0)
        self.main_vertical_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.main_vertical_layout.setSpacing(32)

        action_type_label = CustomLabel(name="Action type")

        self.action_type_input = CustomLineEdit(placeholder_text="", parent=self)

        action_type_vertical_layout = QVBoxLayout()
        action_type_vertical_layout.setSpacing(10)

        action_type_vertical_layout.addWidget(action_type_label)
        action_type_vertical_layout.addWidget(self.action_type_input)

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

        data_before_label = CustomLabel(name="Data before")

        self.data_before_input = CustomTextEdit(border_radius=2,placeholder_text="", parent=self)

        data_before_vertical_layout = QVBoxLayout()
        data_before_vertical_layout.setContentsMargins(0, 0, 0, 0)
        data_before_vertical_layout.setSpacing(10)

        data_before_vertical_layout.addWidget(data_before_label)
        data_before_vertical_layout.addWidget(self.data_before_input)

        data_after_label = CustomLabel(name="Data after")

        self.data_after_input = CustomTextEdit(border_radius=2,placeholder_text="", parent=self)

        data_after_vertical_layout = QVBoxLayout()
        data_after_vertical_layout.setContentsMargins(0, 0, 0, 0)
        data_after_vertical_layout.setSpacing(10)

        data_after_vertical_layout.addWidget(data_after_label)
        data_after_vertical_layout.addWidget(self.data_after_input)

        details_label = CustomLabel(name="Details")

        self.details_input = CustomTextEdit(border_radius=2,placeholder_text="", parent=self)

        details_vertical_layout = QVBoxLayout()
        details_vertical_layout.setContentsMargins(0, 0, 0, 0)
        details_vertical_layout.setSpacing(10)

        details_vertical_layout.addWidget(details_label)
        details_vertical_layout.addWidget(self.details_input)

        central_widget = QWidget()
        central_widget.setMaximumWidth(1200)
        central_widget.setLayout(self.main_vertical_layout)

        self.main_vertical_layout.addLayout(action_type_vertical_layout)
        self.main_vertical_layout.addLayout(changed_by_vertical_layout)
        self.main_vertical_layout.addLayout(change_date_vertical_layout)
        self.main_vertical_layout.addLayout(data_before_vertical_layout)
        self.main_vertical_layout.addLayout(data_after_vertical_layout)
        self.main_vertical_layout.addLayout(details_vertical_layout)

        scroll_area = CustomScrollArea(self)
        scroll_area.setWidget(central_widget)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll_area)

        self.setLayout(layout)
