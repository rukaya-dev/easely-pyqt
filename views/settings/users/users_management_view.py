import asyncio

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QMessageBox, QStackedWidget
from qasync import asyncSlot

from loggers.logger_configs import set_up_logger
from signals import SignalRepositorySingleton
from services.supabase.controllers.settings.user_controller import UserController
from views.settings.users.edit_password_dialog import EditPasswordDialog
from views.settings.users.table.table_layout_view import TableLayout
from views.settings.users.user_dialog import UserDialog
from views.componenets.table.mangement.table_header_filtration_component import TableHeaderFiltration

logger = set_up_logger('main.view.users_management_view')


class UsersManagementView(QWidget):
    def __init__(self):
        super().__init__()

        self.data = []
        self.is_search_enabled = False
        self.central_widget = None
        self.table_view = None
        self.table_header_filtration = None
        self.add_users_dialog = None
        self.view_users_dialog = None
        self.edit_users_dialog = None

        self.stacked_content_widget = QStackedWidget()

        self.error_message = "An unexpected error occurred"

        # Signals
        self.signals = SignalRepositorySingleton.instance()

        # API model
        self.user_controller = UserController()

        # Loading animation layout
        self.main_h_layout = QHBoxLayout()
        self.main_h_layout.setContentsMargins(0, 0, 0, 0)
        self.main_h_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.main_h_layout.addWidget(self.stacked_content_widget)

        # Set Layouts
        self.setLayout(self.main_h_layout)

        asyncio.create_task(self.get_initial_data())

    async def get_initial_data(self):
        self.data = await self.user_controller.get_items()
        self.setup_table_ui()

    def setup_table_ui(self):
        self.table_view = TableLayout(table_name="users", data_controller=self.user_controller,
                                      data_columns=["id", "email", "created_at", "updated_at"],
                                      column_display_names={
                                          "id": "ID",
                                          "email": "Email",
                                          "created_at": "Created At",
                                          "updated_at": "Updated At",
                                      },
                                      is_pagination=False, parent=self)
        self.table_view.update_table_view()
        self.table_header_filtration = TableHeaderFiltration(add_btn_name="User",
                                                             controller=self.user_controller,
                                                             parent=self)
        self.central_widget = QWidget()
        self.central_widget.setObjectName("users_management_table_widget")

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

        self.table_header_filtration.add_btn.clicked.connect(self.show_add_users_dialog)
        self.table_view.viewSignal.connect(self.view_user)
        self.table_view.editPasswordSignal.connect(self.edit_password)
        self.table_view.deleteSignal.connect(self.delete_user)
        self.set_main_content(self.central_widget)

    def set_main_content(self, content_widget):
        self.stacked_content_widget.addWidget(content_widget)
        self.stacked_content_widget.setCurrentWidget(content_widget)

    def fetch_and_update_table_view(self):
        self.table_view.update_table_view()

    @pyqtSlot()
    @asyncSlot()
    async def refresh_table(self):
        self.data = await self.user_controller.get_items()
        self.fetch_and_update_table_view()

    @pyqtSlot(str)
    @asyncSlot()
    async def view_user(self, action):
        if self.table_view.get_current_id():
            self.signals.globalCreateLoadingNotificationSignal.emit("VIEW_USER")
            data = await self.user_controller.get_user_by_id(self.table_view.current_id)
            if not data:
                self.signals.globalLoadingNotificationControllerSignal.emit("VIEW_USER")
                self.signals.globalCreateMessageNotificationSignal.emit({
                    "message_type": "error",
                    "message": self.error_message,
                    "duration": 2000,
                })
            else:
                self.view_users_dialog = UserDialog("View User", parent=self)
                self.view_users_dialog.form_widget.firstname_input.setText(data["raw_user_meta_data"]["first_name"])
                self.view_users_dialog.form_widget.lastname_input.setText(data["raw_user_meta_data"]["last_name"])
                self.view_users_dialog.form_widget.email_input.setText(data["email"])
                self.view_users_dialog.form_widget.current_role = data["raw_user_meta_data"]["user_role"]

                if action == "view":
                    self.view_users_dialog.toggle_inputs_state("view")
                else:
                    self.view_users_dialog.toggle_inputs_state("edit_user_info")

                self.signals.globalLoadingNotificationControllerSignal.emit("VIEW_USER")

                self.view_users_dialog.show()

    @pyqtSlot()
    @asyncSlot()
    async def edit_password(self):
        if self.table_view.get_current_id():
            self.signals.globalCreateLoadingNotificationSignal.emit("GET_USER")
            data = await self.user_controller.get_user_by_id(self.table_view.current_id)
            if not data:
                self.signals.globalLoadingNotificationControllerSignal.emit("GET_USER")
                self.signals.globalCreateMessageNotificationSignal.emit({
                    "message_type": "error",
                    "message": self.error_message,
                    "duration": 2000,
                })
            else:
                self.signals.globalLoadingNotificationControllerSignal.emit("GET_USER")
                edit_password_dialog = EditPasswordDialog(user_id=data["id"], parent=self)
                edit_password_dialog.show()

    @pyqtSlot()
    def show_add_users_dialog(self):
        self.add_users_dialog = UserDialog("Add Role", parent=self)
        self.add_users_dialog.update_btn.hide()
        self.add_users_dialog.show()

    @pyqtSlot()
    @asyncSlot()
    async def delete_user(self):
        if self.table_view.get_current_id():
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText('Are you sure you want to delete?')
            msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            reply = msg.exec()

            if reply == QMessageBox.StandardButton.Ok:
                self.signals.globalCreateLoadingNotificationSignal.emit("DELETE_USER")
                try:
                    await self.user_controller.delete_user(self.table_view.current_id)

                except Exception as e:
                    self.signals.globalCreateMessageNotificationSignal.emit({
                        "message_type": "error",
                        "message": self.error_message,
                        "duration": 2000,
                    })

                finally:
                    await self.refresh_table()
                    self.signals.globalCreateMessageNotificationSignal.emit({
                        "message_type": "success",
                        "message": "User DeletedSuccessfully",
                        "duration": 2000,
                    })
                self.signals.globalLoadingNotificationControllerSignal.emit("DELETE_USER")
