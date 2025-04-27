import asyncio

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QMessageBox, QStackedWidget
from qasync import asyncSlot

from loggers.logger_configs import set_up_logger
from services.supabase.controllers.settings.log_controller import LogController
from services.supabase.controllers.staff.assistant.assistant_controller import AssistantController
from services.supabase.controllers.settings.user_auth_controller import UserAuthController
from signals import SignalRepositorySingleton
from views.componenets.table.mangement.table_header_filtration_component import TableHeaderFiltration
from views.componenets.table.mangement.table_layout import TableLayout
from views.staff.assistants.assistant_dialog import AssistantDialog
from views.staff.assistants.assistant_filter_widget import FilterWidget

logger = set_up_logger('main.views.staff.assistants.assistants_management.assistants_management_view')


class AssistantsManagementView(QWidget):

    def __init__(self):
        super().__init__()

        self.setStyleSheet("background-color:white;")
        self.tab_buttons = None

        self.is_search_enabled = False
        self.is_filter_enabled = False

        self.central_widget = None
        self.table_view = None
        self.table_header_filtration = None
        self.add_assistant_dialog_view = None
        self.assistant_view_dialog = None
        self.view_assistant_information_widget = None
        self.edit_assistant_information_widget = None
        self.edit_assistant_dialog_view = None
        self.filter_widget = None
        self.data = []

        self.stacked_content_widget = QStackedWidget()

        # Signals
        self.signals = SignalRepositorySingleton.instance()
        # self.signals.updateassistantsTableSignal.connect(self.refresh_table)

        # API model
        self.assistant_controller = AssistantController()
        self.log_controller = LogController()
        self.user_auth_controller = UserAuthController()
        self.auth_user = self.user_auth_controller.user_auth_store.get_user()

        # Loading animation layout
        self.main_h_layout = QHBoxLayout()
        self.main_h_layout.setContentsMargins(0, 0, 0, 0)
        self.main_h_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.main_h_layout.addWidget(self.stacked_content_widget)

        # Set Layouts
        self.setLayout(self.main_h_layout)

        asyncio.create_task(self.get_initial_data())

    async def get_initial_data(self):
        # self.signals.globalCreateLoadingNotificationSignal.emit("GET_assistantS_LIST")
        self.data = await self.assistant_controller.get_items(1, 20)
        self.setup_table_ui()

    #         self.signals.globalLoadingNotificationControllerSignal.emit("GET_assistantS_LIST")

    def setup_table_ui(self):
        self.table_view = TableLayout(table_name="assistants", data_controller=self.assistant_controller,
                                      data_columns=[
                                          "assistant_id",
                                          "first_name",
                                          "last_name",
                                          "phone_number",
                                          "created_at",
                                          "updated_at"

                                      ], column_display_names=
                                      {
                                          "assistant_id": "ID",
                                          "first_name": "First name",
                                          "last_name": "Last name",
                                          "phone_number": "Phone number",
                                          "created_at": "Created at",
                                          "updated_at": "Updated at",

                                      },
                                      is_pagination=True, parent=self)

        self.table_view.update_table_view()

        self.filter_widget = FilterWidget(parent=self)

        self.table_header_filtration = TableHeaderFiltration(add_btn_name="assistant",
                                                             controller=self.assistant_controller,
                                                             apply_filter=True, page_filter_widget=self.filter_widget,
                                                             apply_search=True,
                                                             search_place_holder="search by name,speciality and phone number",
                                                             parent=self)
        self.central_widget = QWidget()

        table_content_v_layout = QVBoxLayout()
        self.central_widget.setLayout(table_content_v_layout)
        table_content_v_layout.setContentsMargins(0, 0, 0, 0)
        table_content_v_layout.setSpacing(0)

        table_header_with_table_layout = QVBoxLayout()
        table_header_with_table_layout.setContentsMargins(0, 20, 0, 0)
        table_header_with_table_layout.setSpacing(0)

        table_header_with_table_layout.addWidget(self.table_header_filtration)
        table_header_with_table_layout.addWidget(self.table_view)

        table_content_v_layout.addLayout(table_header_with_table_layout)

        self.table_header_filtration.add_btn.clicked.connect(self.show_add_assistant_dialog)

        self.table_view.viewSignal.connect(self.view_assistant)
        self.table_view.editSignal.connect(self.edit_assistant)
        self.table_view.deleteSignal.connect(self.delete_assistant)
        # self.table_view.serviceManagementSignal.connect(self.view_service_management)

        self.set_main_content(self.central_widget)

    def set_main_content(self, content_widget):
        self.stacked_content_widget.addWidget(content_widget)
        self.stacked_content_widget.setCurrentWidget(content_widget)

    def fetch_and_update_table_view(self):
        self.table_view.update_table_view()

    @pyqtSlot()
    @asyncSlot()
    async def refresh_table(self):
        self.data = await self.assistant_controller.get_items(page_number=self.data["current_page"], item_per_page=10)
        self.fetch_and_update_table_view()

    @pyqtSlot()
    @asyncSlot()
    async def view_assistant(self):
        if self.table_view.get_current_id():
            self.signals.globalCreateLoadingNotificationSignal.emit("VIEW_assistant")
            data = await self.assistant_controller.get_assistant_by_id(self.table_view.get_current_id())
            if not data:
                self.signals.globalLoadingNotificationControllerSignal.emit("VIEW_assistant")
                self.signals.globalCreateMessageNotificationSignal.emit({
                    "message_type": "error",
                    "message": "Error while getting assistant data.",
                    "duration": 2000,
                })
            else:
                self.assistant_view_dialog = AssistantDialog("view", parent=self)
                self.view_assistant_information_widget = self.assistant_view_dialog.form_widget

                # setting assistant data
                self.view_assistant_information_widget.first_name_input.setText(data["first_name"])
                self.view_assistant_information_widget.last_name_input.setText(data["last_name"])
                self.view_assistant_information_widget.qualifications_input.setText(data["qualifications"])
                self.view_assistant_information_widget.email_input.setText(data["email"])
                self.view_assistant_information_widget.phone_number_input.setText(data["phone_number"])
                self.view_assistant_information_widget.address_input.setText(data["address"])
                self.view_assistant_information_widget.role_input.setText(data["role"])

                self.view_assistant_information_widget.first_name_input.setReadOnly(True)
                self.view_assistant_information_widget.last_name_input.setReadOnly(True)
                self.view_assistant_information_widget.qualifications_input.setDisabled(True)
                self.view_assistant_information_widget.email_input.setReadOnly(True)
                self.view_assistant_information_widget.phone_number_input.setReadOnly(True)
                self.view_assistant_information_widget.address_input.setDisabled(True)

                self.assistant_view_dialog.update_btn.hide()
                self.assistant_view_dialog.save_and_cancel_btns.save_btn.hide()

                self.signals.globalLoadingNotificationControllerSignal.emit("VIEW_assistant")
                self.assistant_view_dialog.show()

    @pyqtSlot()
    def show_add_assistant_dialog(self):
        add_assistant_dialog_view = AssistantDialog("add", parent=self)
        add_assistant_dialog_view.update_btn.hide()
        add_assistant_dialog_view.show()

    @pyqtSlot()
    @asyncSlot()
    async def edit_assistant(self):
        if self.table_view.get_current_id():
            self.signals.globalCreateLoadingNotificationSignal.emit("UPDATE_assistant")

            data = await self.assistant_controller.get_assistant_by_id(self.table_view.get_current_id())
            if not data:
                self.signals.globalLoadingNotificationControllerSignal.emit("UPDATE_assistant")
                self.signals.globalCreateMessageNotificationSignal.emit({
                    "message_type": "error",
                    "message": "Error while getting assistant data.",
                    "duration": 2000,
                })
            else:
                self.edit_assistant_dialog_view = AssistantDialog("edit", parent=self)
                self.edit_assistant_information_widget = self.edit_assistant_dialog_view.form_widget

                # assistant Info.
                self.edit_assistant_information_widget.first_name_input.setText(data["first_name"])
                self.edit_assistant_information_widget.last_name_input.setText(data["last_name"])
                self.edit_assistant_information_widget.qualifications_input.setText(data["qualifications"])
                self.edit_assistant_information_widget.email_input.setText(data["email"])
                self.edit_assistant_information_widget.phone_number_input.setText(data["phone_number"])
                self.edit_assistant_information_widget.address_input.setText(data["address"])
                self.edit_assistant_information_widget.role_input.setText(data["role"])

                self.edit_assistant_dialog_view.save_and_cancel_btns.save_btn.hide()

                self.signals.globalLoadingNotificationControllerSignal.emit("UPDATE_assistant")
                self.edit_assistant_dialog_view.show()

    @pyqtSlot()
    @asyncSlot()
    async def delete_assistant(self):
        if self.table_view.get_current_id():
            msg = QMessageBox()
            msg.setText('Are you sure you want to delete?')
            msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            reply = msg.exec()

            if reply == QMessageBox.StandardButton.Ok:
                self.signals.globalCreateLoadingNotificationSignal.emit("DELETE_ASSISTANT")
                data = await self.assistant_controller.delete_assistant(self.table_view.get_current_id())
                if not data:
                    self.signals.globalCreateMessageNotificationSignal.emit({
                        "message_type": "error",
                        "message": "Could not delete assistant.",
                        "duration": 3000,
                    })
                    self.signals.globalLoadingNotificationControllerSignal.emit("DELETE_ASSISTANT")
                else:
                    await self.refresh_table()
                    self.signals.globalCreateMessageNotificationSignal.emit({
                        "message_type": "success",
                        "message": "assistant successfully deleted",
                        "duration": 2000,
                    })
                self.signals.globalLoadingNotificationControllerSignal.emit("DELETE_ASSISTANT")
