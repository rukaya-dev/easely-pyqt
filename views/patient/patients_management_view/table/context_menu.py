import json

from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWidgets import QMenu

from services.supabase.controllers.settings.user_auth_controller import UserAuthController
from stylesheets.common_stylesheet import menu_stylesheet


class ContextMenu(QMenu):
    itemSelected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.user_auth_controller = UserAuthController()
        user = self.user_auth_controller.user_auth_store.get_user()
        role_json_data = json.loads(user["role"])
        self.user_roles = role_json_data

        permissions = [permission.get("permissions", {}).get("permission_slug", "") for permission in
                       self.user_roles.get("roles_permissions", [])]


        self.setContentsMargins(0, 4, 0, 4)

        font = self.font()
        font.setPointSize(11)
        font.setWeight(font.Weight.Normal)
        self.setFont(font)

        self.setStyleSheet(menu_stylesheet)
        self.setFixedWidth(200)

        view_action = QAction(QIcon(':/resources/icons/eye.svg'), "View", self)
        view_action.setData("view")

        edit_action = QAction(QIcon(':/resources/icons/edit.svg'), "Edit", self)
        edit_action.setData("edit")

        delete_action = QAction(QIcon(':/resources/icons/delete.svg'), "Delete", self)
        delete_action.setData("delete")

        create_appointment_action = QAction(QIcon(':/resources/icons/active_add.svg'), "Appointment", self)
        create_appointment_action.setData("create_appointment")

        self.addAction(view_action)
        self.addAction(edit_action)
        self.addAction(delete_action)

        if "appointments_access" in permissions:
            self.addSeparator()
            self.addAction(create_appointment_action)

        self.triggered.connect(self.on_action_triggered)

    @pyqtSlot(QAction)
    def on_action_triggered(self, action: QAction):
        self.itemSelected.emit(action.data())
        self.close()
