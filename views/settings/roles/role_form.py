from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QCheckBox

from loggers.logger_configs import set_up_logger
from services.supabase.controllers.settings.role_controller import RoleController
from signals import SignalRepositorySingleton
from utils.validator import  role_validator
from views.componenets.customsComponents.custom_checkbox import CustomCheckBox
from views.componenets.customsComponents.table.form_componenets.custom_input import CustomLineEdit
from views.componenets.customsComponents.table.form_componenets.custom_label import CustomLabel

logger = set_up_logger('main.views.settings.roles_management_view.role_form')


class RoleForm(QWidget):
    def __init__(self):
        super().__init__()
        # API model
        self.role_controller = RoleController()
        # Signals
        self.signals = SignalRepositorySingleton.instance()

        self.permissions_data = []
        self.permissions = []
        self.checkbox_layout = None

        # Main Vertical Layout that contains children widgets
        self.main_vertical_layout = QVBoxLayout()
        self.main_vertical_layout.setContentsMargins(0, 0, 0, 0)
        self.main_vertical_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.main_vertical_layout.setSpacing(32)

        role_name_label = CustomLabel(name="Name")

        self.role_name_input = CustomLineEdit(placeholder_text="Admin ", parent=self)
        self.role_name_input.setValidator(role_validator)

        # Patient’s Visit Date Vertical Layout
        role_name_vertical_layout = QVBoxLayout()
        role_name_vertical_layout.setSpacing(10)
        role_name_vertical_layout.addWidget(role_name_label)
        role_name_vertical_layout.addWidget(self.role_name_input)

        # Address & Phone Number
        desc_label = CustomLabel(name="Description")

        self.desc_input = CustomLineEdit(placeholder_text="", parent=self)

        desc_vertical_layout = QVBoxLayout()
        desc_vertical_layout.setSpacing(10)
        desc_vertical_layout.addWidget(desc_label)
        desc_vertical_layout.addWidget(self.desc_input)

        # Check box
        self.checkbox_layout = QVBoxLayout()
        self.checkbox_layout.setSpacing(10)

        # Create and add the label
        self.label = CustomLabel(name="Select Role Permissions")

        self.checkbox_layout.addWidget(self.label)

        self.main_vertical_layout.addLayout(role_name_vertical_layout)
        self.main_vertical_layout.addLayout(desc_vertical_layout)
        self.main_vertical_layout.addLayout(self.checkbox_layout)

        self.setLayout(self.main_vertical_layout)
        self.setMinimumWidth(500)

    @pyqtSlot(int, QCheckBox)
    def on_check_box_state_changed(self, state, checkbox: CustomCheckBox):
        permission_status = {"permission_id": checkbox.property("permissionId"), "granted": True if state else False}
        # Check if the permission status needs to be updated or added
        index = next(
            (index for (index, d) in enumerate(self.permissions_data) if d["permission_id"] == checkbox.property("permissionId")),
            None)
        if index is not None:
            self.permissions_data[index] = permission_status
        else:
            self.permissions_data.append(permission_status)

    def render_permissions(self, permissions):
        if permissions:
            for permission in permissions:
                check_box = CustomCheckBox(permission["permission_name"])

                check_box.permissionId = permission["permission_id"]
                check_box.setProperty("permissionId", permission["permission_id"])
                check_box.stateChanged.connect(
                    lambda state, checkbox=check_box: self.on_check_box_state_changed(state, checkbox))
                self.checkbox_layout.addWidget(check_box)
