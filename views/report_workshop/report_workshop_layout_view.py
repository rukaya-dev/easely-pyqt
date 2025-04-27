from PyQt6.QtWidgets import QWidget, QHBoxLayout, QStackedWidget, \
    QPushButton

from views.report_workshop.category.categories_management_view import CategoriesManagementView
from views.componenets.customsComponents.custom_tab_widget import CustomTabWidget
from views.report_workshop.option.options_management_view import OptionsManagementView
from views.report_workshop.report_header.report_header_view import ReportHeaderView
from views.report_workshop.template.templates_management_view import TemplatesManagementView


class ReportWorkshopLayoutView(QWidget):
    def __init__(self):
        super().__init__()

        self.first_tab_button = None

        self.tab_buttons = CustomTabWidget([
                                            {"button_name": "Templates", "page_name": "templates_management_view"},
                                            {"button_name": "Options", "page_name": "options_management_view"},
                                            {"button_name": "Categories", "page_name": "categories_management_view"},
                                            {"button_name": "Report Header", "page_name": "report_header_layout_view"},

        ])

        self.stacked_widget = QStackedWidget()

        self.templates_view = TemplatesManagementView()
        self.options_view = OptionsManagementView()
        self.categories_view = CategoriesManagementView()
        self.report_header_layout_view = ReportHeaderView()

        self.views = {
            "report_header_layout_view": self.report_header_layout_view,
            "templates_management_view": self.templates_view,
            "options_management_view": self.options_view,
            "categories_management_view": self.categories_view,
        }

        for name, view in self.views.items():
            view.setObjectName(name)
            self.stacked_widget.addWidget(view)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)
        self.tab_buttons.set_up_buttons()

        self.set_main_content("templates_management_view")

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

