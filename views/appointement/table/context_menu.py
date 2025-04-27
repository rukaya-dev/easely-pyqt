import json

from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWidgets import QMenu

from services.supabase.controllers.settings.user_auth_controller import UserAuthController
from stylesheets.common_stylesheet import menu_stylesheet


class ContextMenu(QMenu):
    itemSelected = pyqtSignal(str)

    def __init__(self, controller, parent=None):
        super().__init__(parent)

        self.parent = parent
        self.controller = controller

        self.active_tab = self.controller.store.get_active_appointment_tab()

        self.user_auth_controller = UserAuthController()
        user = self.user_auth_controller.user_auth_store.get_user()
        role_json_data = json.loads(user["role"])
        self.user_roles = role_json_data

        self.setContentsMargins(5, 4, 5, 4)

        font = self.font()
        font.setPointSize(11)
        font.setWeight(font.Weight.Normal)
        self.setFont(font)

        self.setStyleSheet(menu_stylesheet)
        self.setFixedWidth(200)

        view_action = QAction(QIcon(':/resources/icons/eye.svg'), "View", self)
        view_action.setData("view")

        make_report_action = QAction(QIcon(':/resources/icons/make_report.svg'), "Make Report", self)
        make_report_action.setData("make_report")


        self.re_schedule_action = QAction(QIcon(':/resources/icons/re_schedule.svg'), "Re-schedule", self)

        self.re_schedule_action.setData("re_schedule")

        self.addAction(view_action)

        self.addSeparator()

        edit_menu = self.addMenu("Edit")
        edit_menu.setContentsMargins(10, 4, 10, 4)
        edit_menu.setStyleSheet(menu_stylesheet)
        edit_menu.setFixedWidth(150)

        edit_appointment_status_action = edit_menu.addAction(QIcon(), "Status")
        edit_appointment_status_action.setData("edit_status")

        edit_appointment_additional_data_action = edit_menu.addAction(QIcon(), "Additional Data")
        edit_appointment_additional_data_action.setData("edit_additional_data")

        self.addSeparator()
        self.addAction(self.re_schedule_action)

        if self.active_tab != "canceled":
            self.cancel_appointment_action = QAction(QIcon(':/resources/icons/cancel_appointment.svg'),
                                                     "Cancel Appointment",
                                                     self)
            self.cancel_appointment_action.setData("cancel_appointment")
            self.addAction(self.cancel_appointment_action)

        self.addAction(make_report_action)

        self.triggered.connect(self.on_action_triggered)

    @pyqtSlot(QAction)
    def on_action_triggered(self, action: QAction):
        self.itemSelected.emit(action.data())
        self.close()
