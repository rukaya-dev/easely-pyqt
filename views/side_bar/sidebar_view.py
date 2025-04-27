import json
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QSpacerItem, \
    QGraphicsOpacityEffect, QButtonGroup

from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QIcon, QCursor, QPixmap

import os

from services.supabase.controllers.settings.user_auth_controller import UserAuthController
from signals import SignalRepositorySingleton


class Sidebar(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedWidth(66)
        self.setStyleSheet("background-color:white;")

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.setContentsMargins(0, 0, 0, 0)

        # Controller
        self.user_auth_controller = UserAuthController()
        self.user_roles = []

        # Signal
        self.signals = SignalRepositorySingleton.instance()
        self.signals.setSideBarButtonActive.connect(lambda object_name: self.on_button_clicked(object_name),
                                                    Qt.ConnectionType.UniqueConnection)

        vertical_widget = QWidget()
        vertical_widget.setFixedWidth(66)
        vertical_widget.setObjectName("MainSideBarVerticalWidget")

        vertical_widget.setStyleSheet("""
            QWidget#MainSideBarVerticalWidget {
               background-color:#F6F8FA;
               border-right:1px solid #F0F2F0;
            }
          """)

        self.sidebar_layout = QVBoxLayout(vertical_widget)
        self.sidebar_layout.setContentsMargins(0, 30, 0, 30)
        self.sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.spacer = QSpacerItem(0, 30)

        self.sidebar_group_buttons = QButtonGroup()

        self.allowed_button_data = []

        self.all_buttons = {
            "dashboard_access": {"object_name": "dashboard_button",
                                 "active_svg": ":/resources/icons/active_dashboard.svg",
                                 "original_svg": ":/resources/icons/dashboard.svg",
                                 "tool_tip": "Dashboard"},

            "appointments_access": {"object_name": "appointments_button",
                                    "active_svg": ":/resources/icons/active_appointment.svg",
                                    "original_svg": ":/resources/icons/appointment.svg",
                                    "tool_tip": "Appointments Management"},

            "patients_access": {"object_name": "patients_button", "active_svg": ":/resources/icons/active_patients.svg",
                                "original_svg": ":/resources/icons/patients.svg",
                                "tool_tip": "Patients Management"},

            "reports_access": {"object_name": "reports_button", "active_svg": ":/resources/icons/active_reports.svg",
                               "original_svg": ":/resources/icons/reports.svg",
                               "tool_tip": "Reports Management"},

            "report_workshop_access": {"object_name": "report_workshop_button",
                                       "active_svg": ":/resources/icons/active_layout.svg",
                                       "original_svg": ":/resources/icons/layout.svg",
                                       "tool_tip": "Report WorkShop"},

            "billings_access": {"object_name": "billings_button",
                                "active_svg": ":/resources/icons/active_billing.svg",
                                "original_svg": ":/resources/icons/billing.svg",
                                "tool_tip": "Billing Management"},


            "staff_access": {"object_name": "staff_button", "active_svg": ":/resources/icons/active_staff.svg",
                             "original_svg": ":/resources/icons/staff.svg",
                             "tool_tip": "Staff Management"},

            "activity_center_access": {"object_name": "activity_center_button",
                                       "active_svg": ":/resources/icons/active_activity_center.svg",
                                       "original_svg": ":/resources/icons/activity_center.svg",
                                       "tool_tip": "Logs"},

            "settings_access": {"object_name": "settings_button",
                                "active_svg": ":/resources/icons/active_settings.svg",
                                "original_svg": ":/resources/icons/settings.svg",
                                "tool_tip": "Settings"},
        }

        user = self.user_auth_controller.user_auth_store.get_user()
        role_json_data = json.loads(user["role"])
        self.user_roles = role_json_data

        self.permissions = [permission.get("permissions", {}).get("permission_slug", "") for permission in
                            self.user_roles.get("roles_permissions", [])]

        print(self.permissions)

        # Filter allowed buttons based on permissions
        for permission_key, button_info in self.all_buttons.items():
            if permission_key in self.permissions:
                self.allowed_button_data.append(button_info)

        for index, item in enumerate(self.allowed_button_data):
            button = self.create_button(item["original_svg"], item["object_name"], item["tool_tip"])

            self.sidebar_group_buttons.addButton(button)

            self.sidebar_layout.addWidget(button, alignment=Qt.AlignmentFlag.AlignCenter)

            if item["object_name"] == "dashboard_button":
                self.dashboard_button = button
            if item["object_name"] == "add_reports_button":
                self.add_reports_button = button
            if item["object_name"] == "files_button":
                self.files_button = button
            if item["object_name"] == "report_workshop_button":
                self.report_workshop_button = button
            if item["object_name"] == "category_button":
                self.category_button = button
            if item["object_name"] == "options_button":
                self.options_button = button
            if item["object_name"] == "template_button":
                self.template_button = button
            if item["object_name"] == "layout_button":
                self.layout_button = button
            if item["object_name"] == "activity_center_button":
                self.activity_center_button = button
            if item["object_name"] == "patients_button":
                self.patients_button = button
            if item["object_name"] == "settings_button":
                self.settings_button = button
            if item["object_name"] == "staff_button":
                self.settings_button = button
            if item["object_name"] == "appointments_button":
                self.appointments_button = button
            if item["object_name"] == "billings_button":
                self.billings_button = button
            if item["object_name"] == "reports_button":
                self.reports_button = button

            if index < len(self.allowed_button_data) - 1:
                self.sidebar_layout.addItem(self.spacer)

        self.activate_first_button()

        self.sidebar_layout.addStretch(1)

        layout.addWidget(vertical_widget, 1)
        self.setLayout(layout)

    def create_button(self, icon_path, object_name, tool_tip):
        button = QPushButton()
        button.setToolTip(tool_tip)
        button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        button.setIcon(QIcon(icon_path))
        button.setIconSize(QSize(23, 23))
        button.setObjectName(object_name)
        button.setStyleSheet(
            "QPushButton { background-color: transparent; border: 0px; border-radius: 10px;}"
            "QPushButton:hover { background-color: #F6F8FA; border-radius: 5px; }"
        )
        button.setProperty("id", object_name)
        button.setFixedSize(QSize(45, 37))
        button.clicked.connect(lambda: self.on_button_clicked(object_name))
        self.sidebar_layout.addWidget(button)
        return button

    def on_button_clicked(self, object_name):

        self.reset_button_icons()

        self.set_button_icon_active(object_name)

        self.signals.signalParentViewStackedChange.emit(object_name)

    @staticmethod
    def change_button_icon_with_animation(button, new_icon_path):
        """
        Change the button icon with a fade-out, change, fade-in animation.
        """
        effect = QGraphicsOpacityEffect(button)
        button.setGraphicsEffect(effect)

        button.fade_out = QPropertyAnimation(effect, b"opacity")
        button.fade_out.setDuration(150)
        button.fade_out.setStartValue(1)
        button.fade_out.setEndValue(0)
        button.fade_out.setEasingCurve(QEasingCurve.Type.OutCurve)

        button.fade_in = QPropertyAnimation(effect, b"opacity")
        button.fade_in.setDuration(150)
        button.fade_in.setStartValue(0)
        button.fade_in.setEndValue(1)
        button.fade_in.setEasingCurve(QEasingCurve.Type.InCurve)

        button.setStyleSheet("""
            QPushButton {
                  background-color: #DFE4E8;
                  border-radius: 5px;
                  border: none;
            }
        """)

        button.setStyleSheet("""
                QPushButton {
                          background-color: #DFE4E8;
                          color: white;
                          border-radius: 5px;
                          border: none;
                }
                """)

        def on_fade_out_finished():
            button.setIcon(QIcon(QPixmap(new_icon_path)))
            button.setStyleSheet("""
                QPushButton {
                          background-color: #DFE4E8;
                          color: white;
                          border-radius: 5px;
                          border: none;
                }
                """)
            button.fade_in.start()

        button.fade_out.finished.connect(on_fade_out_finished)

        button.fade_out.start()

    def reset_button_icons(self):
        for index, item in enumerate(self.allowed_button_data):
            button = self.findChild(QPushButton, item["object_name"])
            original_svg_image = QPixmap(item["original_svg"])
            button.setIcon(QIcon(original_svg_image))
            button.setStyleSheet(
                "QPushButton { background-color: transparent; border: 0px; border-radius: 5px;}"
                "QPushButton:hover { background-color: #DFE4E8; border-radius: 10px; }"
            )

    def set_button_icon_active(self, object_name):
        data_of_button = self.find_button_by_object_name(object_name)
        button = self.findChild(QPushButton, object_name)
        self.change_button_icon_with_animation(button, data_of_button["active_svg"])

    def find_button_by_object_name(self, object_name):
        for button_info in self.allowed_button_data:
            if button_info.get("object_name") == object_name:
                return button_info

        return None

    def activate_first_button(self):
        for permission_key, button_info in self.all_buttons.items():
            if permission_key in self.permissions:
                data_of_button = self.find_button_by_object_name(button_info["object_name"])
                for btn in self.sidebar_group_buttons.buttons():
                    if btn.property("id") == button_info["object_name"]:
                        self.change_button_icon_with_animation(btn, data_of_button["active_svg"])
                break
