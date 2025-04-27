import asyncio
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QMessageBox, QStackedWidget
from qasync import asyncSlot

from loggers.logger_configs import set_up_logger
from services.supabase.controllers.settings.service_controller import ServiceController
from services.supabase.controllers.settings.log_controller import LogController
from services.supabase.controllers.settings.user_auth_controller import UserAuthController
from signals import SignalRepositorySingleton
from views.componenets.table.mangement.table_header_filtration_component import TableHeaderFiltration
from views.componenets.table.mangement.table_layout import TableLayout
from views.settings.services.service_dialog import ServiceDialog
from views.settings.services.service_filter_widget import FilterWidget

logger = set_up_logger('main.views.settings.services.services_management_view')


class ServicesManagementView(QWidget):

    def __init__(self):
        super().__init__()

        self.setStyleSheet("background-color:white;")
        self.tab_buttons = None

        self.is_search_enabled = False
        self.is_filter_enabled = False

        self.central_widget = None
        self.table_view = None
        self.table_header_filtration = None
        self.add_service_dialog_view = None
        self.service_view_dialog = None
        self.edit_service_dialog_view = None
        self.filter_widget = None
        self.data = []

        self.stacked_content_widget = QStackedWidget()

        # Signals
        self.signals = SignalRepositorySingleton.instance()

        # API model
        self.service_controller = ServiceController()
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
        # self.signals.globalCreateLoadingNotificationSignal.emit("GET_SERVICES_INITIAL_LIST")
        self.data = await self.service_controller.get_items(1, 20)
        self.setup_table_ui()
        # self.signals.globalLoadingNotificationControllerSignal.emit("GET_SERVICES_INITIAL_LIST")

    def setup_table_ui(self):
        self.table_view = TableLayout(table_name="services  ", data_controller=self.service_controller,
                                      data_columns=[
                                          "service_id",
                                          "name",
                                          "description",
                                          "created_at",
                                          "updated_at",

                                      ], column_display_names=
                                      {
                                          "service_id": "ID",
                                          "name": "Name",
                                          "description": "Description",
                                          "created_at": "Created at",
                                          "updated_at": "Updated at",

                                      },
                                      is_pagination=True, parent=self)

        self.table_view.update_table_view()

        self.filter_widget = FilterWidget(parent=self)

        self.table_header_filtration = TableHeaderFiltration(add_btn_name="Service",
                                                             controller=self.service_controller,
                                                             apply_filter=True, page_filter_widget=self.filter_widget,
                                                             apply_search=True, search_place_holder="search by name and description",
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

        self.table_header_filtration.add_btn.clicked.connect(self.show_add_service_dialog)

        self.table_view.viewSignal.connect(self.view_service)
        self.table_view.editSignal.connect(self.edit_service)
        self.table_view.deleteSignal.connect(self.delete_service)

        self.set_main_content(self.central_widget)

    def set_main_content(self, content_widget):
        self.stacked_content_widget.addWidget(content_widget)
        self.stacked_content_widget.setCurrentWidget(content_widget)

    def fetch_and_update_table_view(self):
        self.table_view.update_table_view()

    @pyqtSlot()
    @asyncSlot()
    async def refresh_table(self):
        self.data = await self.service_controller.get_items(self.data["current_page"], 10)
        self.fetch_and_update_table_view()

    @pyqtSlot()
    @asyncSlot()
    async def view_service(self):
        if self.table_view.get_current_id():
            self.signals.globalCreateLoadingNotificationSignal.emit("VIEW_SERVICE")
            data = await self.service_controller.get_service_by_id(self.table_view.get_current_id())
            if not data:
                self.signals.globalLoadingNotificationControllerSignal.emit("VIEW_SERVICE")
                self.signals.globalCreateMessageNotificationSignal.emit({
                    "message_type": "error",
                    "message": "Error while getting service data.",
                    "duration": 2000,
                })
            else:
                self.service_view_dialog = ServiceDialog("view", parent=self)

                # setting service data
                self.service_view_dialog.form_widget.name_input.setText(data["name"])
                self.service_view_dialog.form_widget.description_input.setText(data["description"])

                self.service_view_dialog.form_widget.name_input.setReadOnly(True)
                self.service_view_dialog.form_widget.description_input.setReadOnly(True)

                self.service_view_dialog.update_btn.hide()
                self.service_view_dialog.save_and_cancel_btns.save_btn.hide()

                self.signals.globalLoadingNotificationControllerSignal.emit("VIEW_SERVICE")
                self.service_view_dialog.show()

    @pyqtSlot()
    def show_add_service_dialog(self):
        add_service_dialog_view = ServiceDialog("add", parent=self)
        add_service_dialog_view.update_btn.hide()
        add_service_dialog_view.show()

    @pyqtSlot()
    @asyncSlot()
    async def edit_service(self):
        if self.table_view.get_current_id():
            self.signals.globalCreateLoadingNotificationSignal.emit("EDIT_SERVICE")
            data = await self.service_controller.get_service_by_id(self.table_view.get_current_id())
            if not data:
                self.signals.globalLoadingNotificationControllerSignal.emit("EDIT_SERVICE")
                self.signals.globalCreateMessageNotificationSignal.emit({
                    "message_type": "error",
                    "message": "Error while getting service data.",
                    "duration": 2000,
                })
            else:
                self.edit_service_dialog_view = ServiceDialog("view", parent=self)

                # setting service data
                self.edit_service_dialog_view.form_widget.name_input.setText(data["name"])
                self.edit_service_dialog_view.form_widget.description_input.setText(data["description"])

                self.edit_service_dialog_view.save_and_cancel_btns.save_btn.hide()

                self.signals.globalLoadingNotificationControllerSignal.emit("EDIT_SERVICE")
                self.edit_service_dialog_view.show()

    @pyqtSlot()
    @asyncSlot()
    async def delete_service(self):
        if self.table_view.get_current_id():
            msg = QMessageBox()
            msg.setText('Are you sure you want to delete?')
            msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            reply = msg.exec()

            if reply == QMessageBox.StandardButton.Ok:
                self.signals.globalCreateLoadingNotificationSignal.emit("DELETE_SERVICE")
                data = await self.service_controller.delete_service(self.table_view.get_current_id())
                if not data:
                    self.signals.globalCreateMessageNotificationSignal.emit({
                        "message_type": "error",
                        "message": "Could not delete service.",
                        "duration": 3000,
                    })
                    self.signals.globalLoadingNotificationControllerSignal.emit("DELETE_SERVICE")
                else:
                    await self.refresh_table()
                    self.signals.globalCreateMessageNotificationSignal.emit({
                        "message_type": "success",
                        "message": "service successfully deleted",
                        "duration": 2000,
                    })
                self.signals.globalLoadingNotificationControllerSignal.emit("DELETE_SERVICE")
