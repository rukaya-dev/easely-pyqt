import asyncio
import json

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget
from qasync import asyncSlot

from loggers.logger_configs import set_up_logger
from signals import SignalRepositorySingleton
from services.supabase.controllers.patient.patient_trash_controller import PatientTrashController
from utils.utlis import convert_to_html_text
from views.componenets.trash.table_layout import TableLayout
from views.componenets.trash.view_trash_dialog import TrashDialog
from views.patient.trash_management_view.filter_widget import FilterWidget
from views.componenets.table.mangement.table_header_filtration_component import TableHeaderFiltration

logger = set_up_logger('main.views.trash.trash_management_view')


class TrashManagementView(QWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("background-color:white;")
        self.tab_buttons = None

        self.is_search_enabled = False
        self.is_filter_enabled = False

        self.central_widget = None
        self.table_view = None
        self.table_header_filtration = None
        self.view_trash_dialog = None
        self.filter_widget = None
        self.data = []

        self.stacked_content_widget = QStackedWidget()

        # Signals
        self.signals = SignalRepositorySingleton.instance()
        self.signals.updatePatientsTrashTableSignal.connect(self.refresh_table)

        # API model
        self.trash_controller = PatientTrashController()

        # Loading animation layout
        self.main_h_layout = QHBoxLayout()
        self.main_h_layout.setContentsMargins(0, 0, 0, 0)
        self.main_h_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.main_h_layout.addWidget(self.stacked_content_widget)

        # Set Layouts
        self.setLayout(self.main_h_layout)

        asyncio.create_task(self.get_initial_data())

    async def get_initial_data(self):
        self.data = await self.trash_controller.get_items(1, 10)
        self.setup_table_ui()

    def setup_table_ui(self):
        self.table_view = TableLayout(self.trash_controller,
                                      data_columns=[
                                          "trash_id",
                                          "name",
                                          "age",
                                          "gender",
                                          "phone_number",
                                          "deleted_by",
                                          "deleted_at",
                                      ], column_display_names={
                                          "trash_id": "ID",
                                          "patient": "Name",
                                          "age": "Age",
                                          "gender": "Gender",
                                          "phone_number": "Phone number",
                                          "deleted_by": "Deleted by",
                                          "deleted_at": "Deleted at",
                                      },
                                      is_pagination=True, parent=self)

        self.table_view.update_table_view()

        self.filter_widget = FilterWidget(parent=self)

        self.table_header_filtration = TableHeaderFiltration(add_btn_name="",
                                                             controller=self.trash_controller,
                                                             apply_filter=True, page_filter_widget=self.filter_widget,
                                                             apply_search=True, search_place_holder="search deleted by",
                                                             parent=self

                                                             )
        self.table_header_filtration.add_btn.hide()
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

        self.table_view.viewSignal.connect(self.view_trash)
        self.table_view.revertSignal.connect(self.put_back)
        self.set_main_content(self.central_widget)

    def set_main_content(self, content_widget):
        self.stacked_content_widget.addWidget(content_widget)
        self.stacked_content_widget.setCurrentWidget(content_widget)

    def fetch_and_update_table_view(self):
        self.table_view.update_table_view()

    @pyqtSlot()
    @asyncSlot()
    async def view_trash(self):
        if self.table_view.get_current_id():
            self.signals.globalCreateLoadingNotificationSignal.emit("VIEW_TRASH")

            data = await self.trash_controller.get_trash_by_id(self.table_view.get_current_id())
            if not data:
                self.signals.globalLoadingNotificationControllerSignal.emit("VIEW_TRASH")
                self.signals.globalCreateMessageNotificationSignal.emit({
                    "message_type": "error",
                    "message": "Error while getting trash data.",
                    "duration": 2000,
                })
                await self.refresh_table()
            else:
                self.view_trash_dialog = TrashDialog("view", parent=self)

                self.view_trash_dialog.form_widget.deleted_by_input.setText(data["deleted_by"])
                self.view_trash_dialog.form_widget.deleted_at_input.setText(data["deleted_at"])

                data_as_html = convert_to_html_text(json.loads(data["patient_info"]))
                self.view_trash_dialog.form_widget.patient_info_input.insertHtml(data_as_html)

                self.view_trash_dialog.form_widget.deleted_by_input.setReadOnly(True)
                self.view_trash_dialog.form_widget.deleted_at_input.setReadOnly(True)
                self.view_trash_dialog.form_widget.patient_info_input.setReadOnly(True)

                self.view_trash_dialog.save_and_cancel_btns.save_btn.hide()

                self.signals.globalLoadingNotificationControllerSignal.emit("VIEW_TRASH")
                self.view_trash_dialog.show()

    @pyqtSlot()
    @asyncSlot()
    async def refresh_table(self):
        self.data = await self.trash_controller.get_items(self.data["current_page"], 10)
        self.fetch_and_update_table_view()

    @pyqtSlot()
    @asyncSlot()
    async def put_back(self):
        if self.table_view.get_current_id():
            self.signals.globalCreateLoadingNotificationSignal.emit("PUT_BACK")
            data = await self.trash_controller.get_trash_by_id(self.table_view.get_current_id())
            if not data:
                self.signals.globalCreateMessageNotificationSignal.emit({
                    "message_type": "error",
                    "message": "An unexpected error occurred",
                    "duration": 2000,
                })
                self.signals.globalCreateLoadingNotificationSignal.emit("PUT_BACK")
            else:
                res = await self.trash_controller.put_back(data)
                if not res:
                    self.signals.globalCreateMessageNotificationSignal.emit({
                        "message_type": "error",
                        "message": "An unexpected error occurred",
                        "duration": 2000,
                    })
                    self.signals.globalLoadingNotificationControllerSignal.emit("PUT_BACK")
                else:
                    self.signals.updatePatientsTableSignal.emit()
                    await self.refresh_table()
                self.signals.globalLoadingNotificationControllerSignal.emit("PUT_BACK")
