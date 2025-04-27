from PyQt6.QtWidgets import QWidget, QHBoxLayout, QStackedWidget, QPushButton

from views.componenets.customsComponents.custom_tab_widget import CustomTabWidget
from views.activity_center.logs.logs_management_view import LogsManagementView


class ActivityCenterLayoutView(QWidget):
    def __init__(self):
        super().__init__()

        self.first_tab_button = None

        self.tab_buttons = CustomTabWidget([
            {"button_name": "Logs", "page_name": "logs_management_view"},

        ])

        self.stacked_widget = QStackedWidget()

        self.logs_management_view = LogsManagementView()

        self.views = {
            "logs_management_view": self.logs_management_view,
        }

        for name, view in self.views.items():
            view.setObjectName(name)
            self.stacked_widget.addWidget(view)

        layout = QHBoxLayout()
        layout.addWidget(self.stacked_widget)

        self.setLayout(layout)
        self.tab_buttons.set_up_buttons()

        self.set_main_content("logs_management_view")

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
