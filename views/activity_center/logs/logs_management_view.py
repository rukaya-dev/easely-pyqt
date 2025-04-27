import asyncio
import json

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget
from qasync import asyncSlot

from loggers.logger_configs import set_up_logger
from services.supabase.controllers.settings.log_controller import LogController
from signals import SignalRepositorySingleton
from utils.utlis import convert_to_html_text
from views.activity_center.logs.logs_dialog import LogDialog
from views.activity_center.logs.table.logs_table_layout import LogsTableLayout
from views.componenets.customsComponents.dates_and_times.change_date_filter_componenet import ChangeDateFilterComponent
from views.componenets.table.mangement.table_header_filtration_component import TableHeaderFiltration

logger = set_up_logger('main.views.logs.logs_management_view')


class LogsManagementView(QWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("background-color:white;")
        self.tab_buttons = None

        self.is_search_enabled = False
        self.is_filter_enabled = False

        self.central_widget = None
        self.table_view = None
        self.table_header_filtration = None
        self.add_history_dialog_view = None
        self.view_history_dialog_view = None
        self.filter_widget = None
        self.data = []

        self.stacked_content_widget = QStackedWidget()

        # Signals
        self.signals = SignalRepositorySingleton.instance()

        # API model
        self.log_controller = LogController()

        # Loading animation layout
        self.main_h_layout = QHBoxLayout()
        self.main_h_layout.setContentsMargins(0, 0, 0, 0)
        self.main_h_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.main_h_layout.addWidget(self.stacked_content_widget)

        # Set Layouts
        self.setLayout(self.main_h_layout)

        asyncio.create_task(self.get_initial_data())

    async def get_initial_data(self):
        self.signals.globalCreateLoadingNotificationSignal.emit("GET_LOGS_LIST")
        self.data = await self.log_controller.get_items(1, 10)
        self.setup_table_ui()
        self.signals.globalLoadingNotificationControllerSignal.emit("GET_LOGS_LIST")

    def setup_table_ui(self):
        self.table_view = LogsTableLayout(self.log_controller,
                                          data_columns=[
                                              "log_id",
                                              "action_type",
                                              "model_name",
                                              "changed_by",
                                              "change_date",
                                              "data",
                                              "status",
                                          ], column_display_names=
                                          {
                                              "log_id": "ID",
                                              "action_type": "Action type",
                                              "model_name": "Model name",
                                              "changed_by": "Changed by",
                                              "change_date": "Change date",
                                              "data": "Data",
                                              "status": "Status",
                                          },
                                          is_pagination=True, parent=self)

        self.table_view.update_table_view()

        self.filter_widget = ChangeDateFilterComponent(menu_pos="right", parent=self)
        self.filter_widget.save_and_cancel_buttons_widget.save_btn.clicked.connect(self.apply_filter)
        self.filter_widget.clear_button.button.clicked.connect(self.clear_filter)

        self.table_header_filtration = TableHeaderFiltration(add_btn_name="",
                                                             controller=self.log_controller,
                                                             apply_filter=True, page_filter_widget=self.filter_widget,
                                                             apply_search=True, search_place_holder="search by action type and model name",
                                                             parent=self)
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

        self.table_view.viewSignal.connect(self.view_history)
        self.set_main_content(self.central_widget)

    def set_main_content(self, content_widget):
        self.stacked_content_widget.addWidget(content_widget)
        self.stacked_content_widget.setCurrentWidget(content_widget)

    def fetch_and_update_table_view(self):
        self.table_view.update_table_view()

    @pyqtSlot()
    @asyncSlot()
    async def refresh_table(self):
        self.data = await self.log_controller.get_items(self.data["current_page"], 10)
        self.fetch_and_update_table_view()

    @pyqtSlot()
    @asyncSlot()
    async def view_history(self):
        if self.table_view.get_current_id():
            self.signals.globalCreateLoadingNotificationSignal.emit("VIEW_HISTORY")

            data = await self.log_controller.get_log_by_id(self.table_view.get_current_id())
            if not data:
                self.signals.globalLoadingNotificationControllerSignal.emit("VIEW_HISTORY")
                self.signals.globalCreateMessageNotificationSignal.emit({
                    "message_type": "error",
                    "message": "Error while getting log data.",
                    "duration": 2000,
                })
                await self.refresh_table()
            else:
                self.view_history_dialog_view = LogDialog("view", parent=self)

                self.view_history_dialog_view.form_widget.action_type_input.setText(data["action_type"])
                self.view_history_dialog_view.form_widget.model_name_input.setText(str(data["model_name"]))
                self.view_history_dialog_view.form_widget.changed_by_input.setText(data["changed_by"])
                self.view_history_dialog_view.form_widget.change_date_input.setText(data["change_date"])

                data_as_html = convert_to_html_text(json.loads(data["data"]))
                self.view_history_dialog_view.form_widget.data_input.insertHtml(data_as_html)
                self.view_history_dialog_view.form_widget.status_input.setText(data["status"])

                self.view_history_dialog_view.form_widget.action_type_input.setReadOnly(True)
                self.view_history_dialog_view.form_widget.model_name_input.setReadOnly(True)
                self.view_history_dialog_view.form_widget.changed_by_input.setReadOnly(True)
                self.view_history_dialog_view.form_widget.change_date_input.setReadOnly(True)
                self.view_history_dialog_view.form_widget.data_input.setReadOnly(True)
                self.view_history_dialog_view.form_widget.status_input.setReadOnly(True)

                self.view_history_dialog_view.save_and_cancel_btns.save_btn.hide()

                self.signals.globalLoadingNotificationControllerSignal.emit("VIEW_HISTORY")
                self.view_history_dialog_view.show()

    @pyqtSlot()
    @asyncSlot()
    async def clear_filter(self):
        self.signals.globalCreateLoadingNotificationSignal.emit("CLEAR_FILTER")
        self.filter_widget.change_date_filter_selection.check_box.setChecked(False)
        self.log_controller.store.set_filter_preferences({})

        await self.refresh_table()
        self.filter_widget.custom_drop_down_menu.menu.close()
        self.signals.globalLoadingNotificationControllerSignal.emit("CLEAR_FILTER")
        self.close_menu()

    @pyqtSlot()
    @asyncSlot()
    async def apply_filter(self):
        self.filter_widget.save_and_cancel_buttons_widget.save_btn.start()
        change_date = self.filter_widget.change_date_filter_selection.custom_date_range_selection_widget.selection_widget.custom_date_calendar.selectedDate().toString()

        preferences = {
            "change_date": {
                "enabled": False,
                "filteration_type": "",
                "preset_filter_id": "",
                "custom_date_value": "",
            },
        }

        if self.filter_widget.change_date_filter_selection.check_box.isChecked():
            preferences["change_date"]["enabled"] = True
            present_filter_checked_action = self.filter_widget.change_date_filter_selection.preset_date_filter_selection_widget.menu.actions_group.checkedAction()
            if present_filter_checked_action:
                preferences["change_date"]["filteration_type"] = "preset_filter"
                preset_filter_data = present_filter_checked_action.data()
                preferences["change_date"]["preset_filter_id"] = preset_filter_data["id"]
            else:
                preferences["change_date"]["filteration_type"] = "custom_filter"
                preferences["change_date"]["custom_date_value"] = change_date

        self.log_controller.store.set_filter_preferences(preferences)
        await self.refresh_table()

        self.filter_widget.save_and_cancel_buttons_widget.save_btn.stop()
        self.close_menu()

    def close_menu(self):
        self.filter_widget.custom_drop_down_menu.menu.close()
