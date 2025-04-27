import asyncio

from PyQt6.QtCore import Qt, pyqtSlot, QSortFilterProxyModel
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QMessageBox, QStackedWidget, QCheckBox
from qasync import asyncSlot

from loggers.logger_configs import set_up_logger
from signals import SignalRepositorySingleton
from services.supabase.controllers.settings.role_controller import RoleController
from views.settings.roles.role_dialog import RoleDialog
from views.componenets.table.mangement.table_header_filtration_component import TableHeaderFiltration
from views.componenets.table.mangement.table_layout import TableLayout

logger = set_up_logger('main.views.settings.roles_management_view')


class RolesManagementView(QWidget):
    def __init__(self):
        super().__init__()

        self.stacked_content_widget = QStackedWidget()
        self.data = []
        self.is_search_enabled = False
        self.proxy_model = None
        self.central_widget = None
        self.table_view = None
        self.table_header_filtration = None
        self.add_role_dialog = None
        self.view_role_dialog = None
        self.edit_role_dialog = None
        self.permissions = None

        # Signals
        self.signals = SignalRepositorySingleton.instance()

        # API model
        self.role_controller = RoleController()

        self.error_message = "Unexpected error occurred"

        # Loading animation layout
        self.main_h_layout = QHBoxLayout()
        self.main_h_layout.setContentsMargins(0, 0, 0, 0)
        self.main_h_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.main_h_layout.addWidget(self.stacked_content_widget)

        # Set Layouts
        self.setLayout(self.main_h_layout)

        asyncio.create_task(self.get_initial_data())

    async def get_initial_data(self):
        self.data = await self.role_controller.get_items(1, 20)
        self.setup_table_ui()

    def setup_table_ui(self):
        self.proxy_model = QSortFilterProxyModel()

        self.table_view = TableLayout(table_name="roles", data_controller=self.role_controller,
                                      data_columns=["role_id", "role_name", "permissions"],
                                      column_display_names={
                                          "role_id": "ID",
                                          "role_name": "Name",
                                          "permissions": "Permissions"
                                      },
                                      parent=self)
        self.table_view.update_table_view()
        self.table_header_filtration = TableHeaderFiltration(add_btn_name="Role",
                                                             controller=self.role_controller,
                                                             parent=self)
        self.central_widget = QWidget()
        self.central_widget.setObjectName("roles_management_table_widget")

        table_content_v_layout = QVBoxLayout()
        self.central_widget.setLayout(table_content_v_layout)
        table_content_v_layout.setContentsMargins(0, 0, 0, 0)
        table_content_v_layout.setSpacing(0)

        table_header_with_table_layout = QVBoxLayout()
        table_header_with_table_layout.setContentsMargins(0, 10, 0, 0)
        table_header_with_table_layout.setSpacing(0)
        table_header_with_table_layout.addWidget(self.table_header_filtration)
        table_header_with_table_layout.addWidget(self.table_view)

        table_content_v_layout.addLayout(table_header_with_table_layout)

        self.table_header_filtration.add_btn.clicked.connect(self.show_add_role_dialog)
        self.table_view.viewSignal.connect(self.view_role)
        self.table_view.editSignal.connect(self.edit_role)
        self.table_view.deleteSignal.connect(self.delete_role)
        self.set_main_content(self.central_widget)

    def set_main_content(self, content_widget):
        self.stacked_content_widget.addWidget(content_widget)
        self.stacked_content_widget.setCurrentWidget(content_widget)

    def fetch_and_update_table_view(self):
        self.table_view.update_table_view()

    @pyqtSlot()
    @asyncSlot()
    async def refresh_table(self):
        self.data = await self.role_controller.get_items(self.data["current_page"], 10)
        self.fetch_and_update_table_view()

    @pyqtSlot()
    @asyncSlot()
    async def view_role(self):
        if self.table_view.get_current_id():
            self.signals.globalCreateLoadingNotificationSignal.emit("VIEW_ROLE")
            data = await self.role_controller.get_role_by_id(self.table_view.current_id)
            if not data:
                self.signals.globalLoadingNotificationControllerSignal.emit("VIEW_ROLE")
                self.signals.globalCreateMessageNotificationSignal.emit({
                    "message_type": "error",
                    "message": self.error_message,
                    "duration": 2000,
                })
            else:
                self.view_role_dialog = RoleDialog("view", parent=self)
                # Extract only permission_name and permission_id to a new list of dicts
                permissions = [{"permission_id": item["permissions"]["permission_id"],
                                "permission_name": item["permissions"]["permission_name"]} for item in
                               data["roles_permissions"]]

                self.view_role_dialog.form_widget.render_permissions(permissions)
                permissions_checkboxes = self.view_role_dialog.form_widget.findChildren(QCheckBox)
                for checkbox in permissions_checkboxes:
                    checkbox.setChecked(True)
                    checkbox.setDisabled(True)

                self.view_role_dialog.form_widget.role_name_input.setText(data['role_name'])
                self.view_role_dialog.form_widget.desc_input.setText(data["description"])
                self.view_role_dialog.form_widget.role_name_input.setReadOnly(True)
                self.view_role_dialog.form_widget.desc_input.setReadOnly(True)
                self.view_role_dialog.update_btn.hide()
                self.view_role_dialog.save_and_cancel_btns.save_btn.hide()

                self.signals.globalLoadingNotificationControllerSignal.emit("VIEW_ROLE")

                self.view_role_dialog.show()

    @pyqtSlot()
    @asyncSlot()
    async def edit_role(self):
        if self.table_view.get_current_id():
            self.signals.globalCreateLoadingNotificationSignal.emit("VIEW_ROLE")
            data = await self.role_controller.get_role_by_id(self.table_view.current_id)
            if not data:
                self.signals.globalLoadingNotificationControllerSignal.emit("VIEW_ROLE")
                self.signals.globalCreateMessageNotificationSignal.emit({
                    "message_type": "error",
                    "message": self.error_message,
                    "duration": 2000,
                })
            else:

                self.permissions = await self.role_controller.get_all_permissions()
                if not self.permissions:
                    self.signals.globalLoadingNotificationControllerSignal.emit("VIEW_ROLE")
                    self.signals.globalCreateMessageNotificationSignal.emit({
                        "message_type": "error",
                        "message": self.error_message,
                        "duration": 2000,
                    })
                else:
                    self.edit_role_dialog = RoleDialog("Edit Role", parent=self)
                    self.edit_role_dialog.form_widget.render_permissions(self.permissions)
                    # Extract only permission_name and permission_id to a new list of dicts
                    current_role_permissions = [{"permission_id": item["permissions"]["permission_id"],
                                                 "permission_name": item["permissions"]["permission_name"]} for item in
                                                data["roles_permissions"]]

                    current_role_permissions_ids = {permission["permission_id"] for permission in current_role_permissions}

                    permissions_checkboxes = self.edit_role_dialog.form_widget.findChildren(QCheckBox)

                    seen_permissions = set()

                    for current_permission_id in current_role_permissions_ids:
                        if current_permission_id not in seen_permissions:
                            seen_permissions.add(current_permission_id)
                            for checkbox in permissions_checkboxes:
                                if checkbox.permissionId == current_permission_id:
                                    self.edit_role_dialog.form_widget.permissions_data.append(
                                        {"permission_id": current_permission_id, "granted": True}
                                    )
                                    checkbox.setChecked(True)
                                    break

                    # set data to role pop up view
                    self.edit_role_dialog.form_widget.role_name_input.setText(data["role_name"])
                    self.edit_role_dialog.form_widget.desc_input.setText(data["description"])
                    self.edit_role_dialog.save_and_cancel_btns.save_btn.hide()

                    self.signals.globalLoadingNotificationControllerSignal.emit("VIEW_ROLE")

                    self.edit_role_dialog.show()

    @pyqtSlot()
    @asyncSlot()
    async def show_add_role_dialog(self):
        self.signals.globalCreateLoadingNotificationSignal.emit("CREATE_ROLE")
        try:
            self.permissions = await self.role_controller.get_all_permissions()
            if not self.permissions:
                logger.error()

        except Exception as e:
            self.signals.globalCreateMessageNotificationSignal.emit({
                "message_type": "error",
                "message": f"An unexpected error occurred: {e}",
                "duration": 2000,
            })
            logger.error(e, exc_info=True)
        finally:
            self.add_role_dialog = RoleDialog("Add Role", parent=self)
            self.add_role_dialog.form_widget.render_permissions(self.permissions)
            self.add_role_dialog.update_btn.hide()
            self.signals.globalLoadingNotificationControllerSignal.emit("CREATE_ROLE")
            self.signals.globalCreateMessageNotificationSignal.emit({
                "message_type": "success",
                "message": "Successful get all permissions.",
                "duration": 1000,
            })

            self.add_role_dialog.show()

    @pyqtSlot()
    @asyncSlot()
    async def delete_role(self):
        if self.table_view.get_current_id():
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText('Are you sure you want to delete?')
            msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            reply = msg.exec()

            if reply == QMessageBox.StandardButton.Ok:
                if self.table_view.current_id == 15:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Icon.Warning)
                    msg.setText("Admin Role cannot be deleted.")
                    msg.setDetailedText("admin role is a default role and should not be deleted.")
                    msg.exec()
                self.signals.globalCreateLoadingNotificationSignal.emit("DELETE_ROLE")
                res = await self.role_controller.delete_role(self.table_view.current_id)
                if not res:
                    self.signals.globalCreateMessageNotificationSignal.emit({
                        "message_type": "error",
                        "message": self.error_message,
                        "duration": 5000,
                    })
                else:
                    await self.refresh_table()
                    self.signals.globalCreateMessageNotificationSignal.emit({
                        "message_type": "success",
                        "message": "Role deleted Successfully.",
                        "duration": 5000,
                    })
                self.signals.globalLoadingNotificationControllerSignal.emit("DELETE_ROLE")
