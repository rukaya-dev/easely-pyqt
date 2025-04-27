import json

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QStackedWidget, QPushButton, QMessageBox

from services.supabase.controllers.settings.user_auth_controller import UserAuthController
from views.componenets.customsComponents.custom_tab_widget import CustomTabWidget
from views.settings.clinic.clinic_view import ClinicView
from views.settings.roles.roles_management_view import RolesManagementView
from views.settings.services.services_management_view import ServicesManagementView
from views.settings.users.users_management_view import UsersManagementView


class SettingsLayoutView(QWidget):
    def __init__(self):
        super().__init__()

        self.first_tab_button = None

        self.tab_buttons = CustomTabWidget([
            {"button_name": "Services", "page_name": "services_management_view"},
            {"button_name": "Clinic", "page_name": "clinic_management_view"}
        ]
        )

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setContentsMargins(0, 0, 0, 0)

        self.clinic_management_view = ClinicView()
        self.users_management_view = UsersManagementView()
        self.roles_management_view = RolesManagementView()
        self.services_management_view = ServicesManagementView()

        self.views = {
            "services_management_view": self.services_management_view,
            "clinic_management_view": self.clinic_management_view
        }

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stacked_widget)

        self.setLayout(layout)
        self.get_initial_data()

        self.connect_tab_buttons_with_pages()
        self.activate_first_tab_button()

    def get_initial_data(self):
        auth_user = UserAuthController.get_user_profile_data()
        if not auth_user:
            QMessageBox.critical(self, "Error", "Could not fetch Authenticated User Data From Database")
            return
        else:
            role_data = json.loads(auth_user["role"])
            if role_data["role_name"] == "superadmin":
                self.views["users_management_view"] = self.users_management_view
                self.tab_buttons.tabs_buttons_data.insert(0,
                                                          {"button_name": "Users", "page_name": "users_management_view"}
                                                          )

                self.views["roles_management_view"] = self.roles_management_view
                self.tab_buttons.tabs_buttons_data.insert(1,
                                                          {"button_name": "Roles", "page_name": "roles_management_view"}
                                                          )

        self.tab_buttons.set_up_buttons()
        for name, view in self.views.items():
            view.setObjectName(name)
            self.stacked_widget.addWidget(view)

        if role_data["role_name"] == "superadmin":
            self.set_main_content("users_management_view")
        else:
            self.set_main_content("roles_management_view")

    def set_main_content(self, page_name):
        widget = self.views.get(page_name)
        if widget:
            self.stacked_widget.setCurrentWidget(widget)

    def connect_tab_buttons_with_pages(self):
        tab_buttons = self.tab_buttons.findChildren(QPushButton)
        for i, button in enumerate(tab_buttons):
            if i == 0:
                self.first_tab_button = button
            button.clicked.connect(lambda _, b=button.pageName: self.set_main_content(b))

    def set_tab_content(self, page_name):
        page = self.findChild(QWidget, page_name)
        self.set_main_content(page)

    def activate_first_tab_button(self):
        self.tab_buttons.change_btn_style_when_selected(self.first_tab_button)
