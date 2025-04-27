from PyQt6.QtWidgets import QWidget, QHBoxLayout, QStackedWidget, QPushButton

from views.componenets.customsComponents.custom_tab_widget import CustomTabWidget
from views.staff.assistants.assistants_management_view import AssistantsManagementView
from views.staff.doctors.doctors_management.doctors_management_view import DoctorsManagementView
from views.staff.referring_doctors.referring_doctors_management_view import ReferringDoctorManagementView


class StaffLayoutView(QWidget):
    def __init__(self):
        super().__init__()

        self.first_tab_button = None

        self.tab_buttons = CustomTabWidget([

            {"button_name": "Doctors", "page_name": "doctors_management_view"},
            {"button_name": "Assistants", "page_name": "assistants_management_view"},
            {"button_name": "Referring Doctors", "page_name": "referring_doctors_management_view"},

        ])

        self.stacked_widget = QStackedWidget()

        self.referring_doctors_management_view = ReferringDoctorManagementView()
        self.doctors_management_view = DoctorsManagementView()
        self.assistants_management_view = AssistantsManagementView()

        self.views = {
            "referring_doctors_management_view": self.referring_doctors_management_view,
            "doctors_management_view": self.doctors_management_view,
            "assistants_management_view": self.assistants_management_view
        }

        for name, view in self.views.items():
            view.setObjectName(name)
            self.stacked_widget.addWidget(view)

        layout = QHBoxLayout()
        layout.addWidget(self.stacked_widget)

        self.setLayout(layout)
        self.tab_buttons.set_up_buttons()

        self.set_main_content("doctors_management_view")

        self.connect_tab_buttons_with_pages()
        self.activate_first_tab_button()

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
