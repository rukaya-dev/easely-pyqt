from PyQt6.QtCore import Qt, pyqtSlot, QSize
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QWidget, QMessageBox, QSpacerItem, QSizePolicy
from qasync import asyncSlot

from loggers.logger_configs import set_up_logger
from services.supabase.controllers.settings.role_controller import RoleController
from signals import SignalRepositorySingleton
from views.componenets.customsComponents.buttons.button_with_loader import ButtonWithLoader
from views.componenets.customsComponents.table.save_and_cancel_buttons import SaveAndCancelButtonsWithLoader
from views.settings.roles.role_form import RoleForm

logger = set_up_logger('main.views.settings.roles_management.role_dialog')


class RoleDialog(QDialog):

    def __init__(self, action_type, parent=None):
        super().__init__(parent)

        self.action_type = action_type
        self.error_message = "An unexpected error occurred"

        self.setStyleSheet("background-color:#f3f4f6;")

        self.parent = parent
        self.is_data_widget = None

        self.role_controller = RoleController()

        # Signals
        self.signals = SignalRepositorySingleton.instance()

        central_widget = QWidget(self)
        central_widget.setObjectName("central_widget")

        # # Vertical Layout for the Role data components
        main_data_vertical_layout = QVBoxLayout()
        main_data_vertical_layout.setContentsMargins(20, 20, 20, 20)

        # # Role's Data Component
        self.form_widget = RoleForm()

        # # Controls Buttons for Adding Role
        self.save_and_cancel_btns = SaveAndCancelButtonsWithLoader(text="Save")
        self.save_and_cancel_btns.save_btn.clicked.connect(self.add_new_role)
        self.save_and_cancel_btns.cancel_btn.clicked.connect(self.close)

        self.update_btn = ButtonWithLoader("Update", size=QSize(95, 34))
        self.update_btn.setObjectName("update_save_btn")
        self.update_btn.clicked.connect(self.update_role)

        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)
        controls_layout.setContentsMargins(20, 50, 20, 20)
        controls_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        controls_layout.addWidget(self.save_and_cancel_btns)
        controls_layout.addWidget(self.update_btn)

        # # Adding the components to the main_data_vertical_layout
        main_data_vertical_layout.addWidget(self.form_widget)

        spacer = QSpacerItem(10, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        main_vertical_layout = QHBoxLayout()
        main_vertical_layout.setContentsMargins(0, 0, 0, 0)

        main_vertical_layout.addLayout(main_data_vertical_layout)
        main_vertical_layout.addSpacerItem(spacer)

        central_widget.setLayout(main_vertical_layout)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.addWidget(central_widget)
        self.layout.addLayout(controls_layout)
        self.setLayout(self.layout)

        self.setModal(True)

    def validate_data(self):
        role_name = self.form_widget.role_name_input.text()
        role_permissions = self.form_widget.permissions_data
        if not role_name:
            QMessageBox.warning(self, "Warning", "Please enter role Name")
            return False
        elif role_name == " ":
            QMessageBox.warning(self, "Warning", "Please enter a valid role Name")
            return False

        one_permission_granted = any(permission["granted"] for permission in role_permissions)

        if not one_permission_granted:
            QMessageBox.warning(self, "Warning", "Role must have at least 1 permission.")
            return False
        return True

    @pyqtSlot()
    @asyncSlot()
    async def add_new_role(self):
        global role_data
        if self.validate_data():
            role_insert_data = {
                'role_name': self.form_widget.role_name_input.text(),
                'description': self.form_widget.desc_input.text(),
            }
            self.save_and_cancel_btns.save_btn.start()

            is_exist = await self.role_controller.check_if_role_exist(role_insert_data["role_name"])
            if is_exist:
                QMessageBox.warning(None, "Warning",
                                    f"""Role with name {role_insert_data["role_name"]} already exist.""")
                self.save_and_cancel_btns.save_btn.stop()
            else:
                role_data = await self.role_controller.create_role(role_insert_data)
                if not role_data:
                    self.signals.globalCreateMessageNotificationSignal.emit({
                        "message_type": "error",
                        "message": self.error_message,
                        "duration": 2000,
                    })
                    self.save_and_cancel_btns.save_btn.stop()
                else:
                    for pdata in self.form_widget.permissions_data:
                        if pdata["granted"]:
                            permission_insert_data = {
                                "role_id": role_data[0]["role_id"],
                                "permission_id": pdata["permission_id"]
                            }
                            res = await self.role_controller.create_role_permissions(permission_insert_data)
                            if not res:
                                self.signals.globalCreateMessageNotificationSignal.emit({
                                    "message_type": "error",
                                    "message": self.error_message,
                                    "duration": 5000,
                                })
                                self.save_and_cancel_btns.save_btn.stop()
                                break

                    self.parent.refresh_table()
                    self.save_and_cancel_btns.save_btn.stop()
                    self.close()
                    self.signals.globalCreateMessageNotificationSignal.emit({
                        "message_type": "success",
                        "message": "Role Successfully Added",
                        "duration": 2000,
                    })

    @pyqtSlot()
    @asyncSlot()
    async def update_role(self):
        if self.validate_data():
            role_update_data = {
                'role_name': self.form_widget.role_name_input.text(),
                'description': self.form_widget.desc_input.text(),

            }
            self.update_btn.start()
            role = self.role_controller.store.get_role()
            is_exist = await self.role_controller.check_if_updated_role_exist(role["role_id"],
                                                                              role_update_data["role_name"])
            if is_exist:
                QMessageBox.warning(None, "Warning",
                                    f"""Role with name {role_update_data["role_name"]} already exist.""")
                self.update_btn.stop()
            else:
                res = await self.role_controller.update_role(role["role_id"], role_update_data)
                if not res:
                    self.signals.globalCreateMessageNotificationSignal.emit({
                        "message_type": "error",
                        "message": self.error_message,
                        "duration": 2000,
                    })
                    self.update_btn.stop()
                else:
                    res = await self.role_controller.delete_role_permissions(role["role_id"])
                    if not res:
                        self.signals.globalCreateMessageNotificationSignal.emit({
                            "message_type": "error",
                            "message": self.error_message,
                            "duration": 5000,
                        })
                        self.update_btn.stop()
                    else:
                        for pdata in self.form_widget.permissions_data:
                            if pdata["granted"]:
                                permission_insert_data = {
                                    "role_id": role["role_id"],
                                    "permission_id": pdata["permission_id"]
                                }
                                res = await self.role_controller.create_role_permissions(permission_insert_data)
                        if not res:
                            self.signals.globalCreateMessageNotificationSignal.emit({
                                "message_type": "error",
                                "message": self.error_message,
                                "duration": 5000,
                            })
                            self.update_btn.stop()
                        else:
                            self.parent.refresh_table()
                            self.update_btn.stop()
                            self.close()
                            self.signals.globalCreateMessageNotificationSignal.emit({
                                "message_type": "success",
                                "message": "Role Successfully Updated",
                                "duration": 2000,
                            })

    def get_data(self):
        return {
            "role_name": self.form_widget.role_name_input.text(),
            "description": self.form_widget.desc_input.text()
        }
