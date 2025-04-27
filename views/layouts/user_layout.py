from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget

from views.componenets.noitfications.notificaiton_layout import NotificationLayout
from views.navbar.navbar_view import NavBar
from views.side_bar.sidebar_view import Sidebar


class UserLayout(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color:white;")

        self.stacked_content_widget = QStackedWidget()
        self.stacked_content_widget.setContentsMargins(0, 0, 0, 0)

        self.navigation_view = NavBar()
        self.sidebar_view = Sidebar()

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Add sidebar layout
        main_layout.addWidget(self.sidebar_view)

        # Loading
        self.notification_layout = NotificationLayout(self)

        vertical_layout = QVBoxLayout()
        vertical_layout.setContentsMargins(0, 0, 0, 0)
        vertical_layout.setSpacing(0)

        vertical_layout.addWidget(self.navigation_view)
        vertical_layout.addWidget(self.stacked_content_widget)
        main_layout.addLayout(vertical_layout)

        self.setLayout(main_layout)

        self.stacked_content_widget.currentChanged.connect(self.update_nav_bar)

    def set_main_content(self, content_widget):
        self.stacked_content_widget.addWidget(content_widget)
        self.stacked_content_widget.setCurrentWidget(content_widget)

    def update_nav_bar(self, index):
        if self.navigation_view.page_tab.count() > 0:
            item = self.navigation_view.page_tab.takeAt(0)
            if item.widget() is not None:
                item.widget().deleteLater()
            else:
                item.deleteLater()

        current_tab_widget = self.stacked_content_widget.currentWidget().tab_buttons
        if current_tab_widget:
            self.navigation_view.page_tab.addWidget(current_tab_widget, Qt.AlignmentFlag.AlignTop)

    def resizeEvent(self, event):
        # Reposition notification widget when the window is resized
        self.notification_layout.re_position_notification_widget()
        super().resizeEvent(event)
