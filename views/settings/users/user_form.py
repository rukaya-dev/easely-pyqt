import asyncio

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit

from loggers.logger_configs import set_up_logger
from services.supabase.controllers.settings.role_controller import RoleController
from utils.validator import normal_input_validator, email_validator
from views.componenets.customsComponents.custom_combobox import CustomComboBox
from views.componenets.customsComponents.table.form_componenets.custom_input import CustomLineEdit
from views.componenets.customsComponents.table.form_componenets.custom_label import CustomLabel

logger = set_up_logger('main.views.setting.users.user_form')


class UserForm(QWidget):
    def __init__(self):
        super().__init__()

        # API model
        self.role_controller = RoleController()
        self.current_role = ""

        # Firstname input
        firstname_vertical_layout = QVBoxLayout()
        firstname_vertical_layout.setSpacing(10)

        self.firstname_label = CustomLabel(name="First Name")

        self.firstname_input = CustomLineEdit(placeholder_text="Alexander", parent=self)
        self.firstname_input.setValidator(normal_input_validator)

        firstname_vertical_layout.addWidget(self.firstname_label)
        firstname_vertical_layout.addWidget(self.firstname_input)

        # Lastname input
        lastname_vertical_layout = QVBoxLayout()
        lastname_vertical_layout.setSpacing(10)

        self.lastname_label = CustomLabel(name="Last Name")

        self.lastname_input = CustomLineEdit(placeholder_text="Williams", parent=self)
        self.lastname_input.setValidator(normal_input_validator)

        lastname_vertical_layout.addWidget(self.lastname_label)
        lastname_vertical_layout.addWidget(self.lastname_input)

        # Email input
        email_vertical_layout = QVBoxLayout()
        email_vertical_layout.setSpacing(10)

        self.email_label = CustomLabel(name="Email")

        self.email_input = CustomLineEdit(placeholder_text="alexander@gmail.com", parent=self)
        self.email_input.setValidator(email_validator)

        email_vertical_layout.addWidget(self.email_label)
        email_vertical_layout.addWidget(self.email_input)

        # Password input
        password_vertical_layout = QVBoxLayout()
        password_vertical_layout.setSpacing(10)

        self.password_label = CustomLabel(name="Password")

        self.password_input = CustomLineEdit(placeholder_text="", parent=self)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        password_vertical_layout.addWidget(self.password_label)
        password_vertical_layout.addWidget(self.password_input)

        # Array of roles
        role_vertical_layout = QVBoxLayout()
        role_vertical_layout.setContentsMargins(0, 0, 0, 0)
        role_vertical_layout.setSpacing(10)

        self.role_label = CustomLabel(name="Role")

        self.role_comboBox = CustomComboBox(parent=self)

        role_vertical_layout.addWidget(self.role_label)
        role_vertical_layout.addWidget(self.role_comboBox)

        # Main Vertical Layout that contains children widgets
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(32)

        layout.addLayout(firstname_vertical_layout)
        layout.addLayout(lastname_vertical_layout)
        layout.addLayout(email_vertical_layout)
        layout.addLayout(password_vertical_layout)
        layout.addLayout(role_vertical_layout)

        self.setLayout(layout)
        self.setMinimumWidth(500)

        asyncio.create_task(self.get_roles_data())

    async def get_roles_data(self):
        try:
            await self.role_controller.get_items(1, 100)

        except Exception as e:
            logger.error(e)
        finally:
            data = self.role_controller.store.get_data()
            self.populateSelectDropdown(data["data"])

    def populateSelectDropdown(self, data):
        self.role_comboBox.clear()

        for item in data:
            self.role_comboBox.addItem(item["role_name"])
        self.role_comboBox.setCurrentText(self.current_role)
