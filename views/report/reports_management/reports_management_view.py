import asyncio
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget, QMessageBox
from qasync import asyncSlot

from loggers.logger_configs import set_up_logger
from services.supabase.controllers.settings.log_controller import LogController
from services.supabase.controllers.report_workshop.option_controller import OptionController
from services.supabase.controllers.report_workshop.report_layout_controller import ReportLayoutController

from services.supabase.controllers.settings.user_auth_controller import UserAuthController
from signals import SignalRepositorySingleton
from utils.editor import zoom
from views.report.reports_management.report_view_dialog import ViewReportDialog
from views.report.reports_management.table.table_header_filteration import TableHeaderFiltration
from views.report.reports_management.table.table_layout import TableLayout
from views.report.reports_management.update_report_content import UpdateReportContentDialog
from views.report.reports_management.update_report_status_dialog import UpdateReportStatusDialog

logger = set_up_logger('main.views.report.reports_management_view')


class ReportManagementView(QWidget):

    def __init__(self, data, report_controller, parent=None):
        super().__init__(parent)

        self.report_data = None
        self.parent = parent

        # Table Data types
        self.data = data

        self.edit_report_content_view = None
        self.edit_report_status_dialog_view = None
        self.report_information_widget = None
        self.setStyleSheet("background-color:white;")
        self.tab_buttons = None

        self.central_widget = None
        self.table_view = None
        self.table_header_filtration = None
        self.report_view_dialog = None
        self.filter_widget = None

        self.stacked_content_widget = QStackedWidget()

        # Signals
        self.signals = SignalRepositorySingleton.instance()
        self.signals.globalRecentReportCardClickedSignal.connect(self.set_current_report_id)
        self.signals.refreshReportsAllTabSignal.connect(self.refresh_first_tab)

        # API model
        self.report_controller = report_controller
        self.report_layouts_controller = ReportLayoutController()
        self.option_controller = OptionController()

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

        asyncio.create_task(self.setup_table_ui())

    async def setup_table_ui(self):
        self.table_view = TableLayout(data_controller=self.report_controller,
                                      data_columns=[
                                          "report_id",
                                          "report_title",
                                          "patient_name",
                                          "appointment_date",
                                          "status",
                                          "created_at",
                                          "updated_at",
                                      ], column_display_names=
                                      {
                                          "report_id": "ID",
                                          "report_title": "Report",
                                          "patient_name": "Patient",
                                          "appointment_date": "Appt. Date",
                                          "status": "Status",
                                          "created_at": "Created At",
                                          "updated_at": "Updated At",
                                      },
                                      parent=self)

        self.table_header_filtration = TableHeaderFiltration(reports_controller=self.report_controller,
                                                             parent=self)

        self.table_view.update_table_view()

        self.central_widget = QWidget()

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

        self.table_view.viewSignal.connect(self.view_report)
        self.table_view.editStatusSignal.connect(self.edit_report_status)
        self.table_view.editReportContentSignal.connect(self.edit_report_content)
        self.table_view.printReportSignal.connect(self.print_report)
        self.table_view.deleteReportSignal.connect(self.delete_report)
        self.signals.globalRefreshReportTableSignal.connect(self.refresh_table)

        self.set_main_content(self.central_widget)

    def set_main_content(self, content_widget):
        self.stacked_content_widget.addWidget(content_widget)
        self.stacked_content_widget.setCurrentWidget(content_widget)

    @pyqtSlot()
    @asyncSlot()
    async def refresh_table(self):
        await self.report_controller.get_items()
        self.signals.globalReportUpdateTableViewSignal.emit()

    @pyqtSlot()
    @asyncSlot()
    async def refresh_first_tab(self):
        await self.report_controller.get_items_by_tabs("all")
        self.signals.globalReportUpdateTableViewSignal.emit()

    @pyqtSlot()
    @asyncSlot()
    async def view_report(self):
        await self.fetch_report_data()
        if self.report_data:
            self.report_view_dialog = ViewReportDialog(parent=self)

            self.report_view_dialog.text_edit.insertHtml(self.report_data["report_content"])
            self.report_view_dialog.show()

    @pyqtSlot()
    @asyncSlot()
    async def print_report(self):
        await self.fetch_report_data()
        if self.report_data:
            self.report_view_dialog = ViewReportDialog(parent=self)

            # zoomed_in_html = zoom(self.report_data["report_content"], "zoom_in")
            self.report_view_dialog.text_edit.insertHtml(self.report_data["report_content"])
            self.report_view_dialog.print()

    async def fetch_report_data(self):
        self.signals.globalCreateLoadingNotificationSignal.emit("GET_REPORT_DATA")
        try:
            self.report_data = await self.report_controller.get_report_by_id(self.table_view.get_current_id())

        except Exception as e:
            self.signals.globalCreateMessageNotificationSignal.emit({
                "message_type": "error",
                "message": "An unexpected error occurred",
                "duration": 2000,
            })
            logger.error(e, exc_info=True)
            self.signals.globalLoadingNotificationControllerSignal.emit("GET_REPORT_DATA")
        finally:
            self.signals.globalLoadingNotificationControllerSignal.emit("GET_REPORT_DATA")

    @pyqtSlot()
    @asyncSlot()
    async def edit_report_status(self):
        await self.fetch_report_data()
        if self.report_data:
            self.edit_report_status_dialog_view = UpdateReportStatusDialog(
                controller=self.report_controller, report_id=self.table_view.get_current_id(), parent=self)

            await self.edit_report_status_dialog_view.populate_statuses()
            self.edit_report_status_dialog_view.report_status_combo.setCurrentText(self.report_data["status"])

            self.signals.globalLoadingNotificationControllerSignal.emit("VIEW_REPORT_STATUS")
            self.edit_report_status_dialog_view.show()

    @pyqtSlot()
    @asyncSlot()
    async def edit_report_content(self):
        await self.fetch_report_data()
        if self.report_data:

            self.edit_report_content_view = UpdateReportContentDialog(report_controller=self.report_controller,
                                                                      parent=self)

            self.edit_report_content_view.editor_view.zeus_editor_text_box.setHtml(self.report_data["report_content"])

            if self.report_data.get("category"):
                options_list_data = await self.get_all_category_options(self.report_data["category"])
                if options_list_data:
                    await self.edit_report_content_view.render_existing_options_widgets(
                        options_list_data=options_list_data)
                    self.edit_report_content_view.editor_view.zeus_editor_text_box.update_options_list([])

            self.edit_report_content_view.showMaximized()

    @pyqtSlot()
    @asyncSlot()
    async def delete_report(self):
        msg = QMessageBox()
        msg.setText('Are you sure you want to delete?')
        msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        reply = msg.exec()

        if reply == QMessageBox.StandardButton.Ok:
            self.signals.globalCreateLoadingNotificationSignal.emit("DELETE_REPORT")
            res = await self.report_controller.delete_report(self.table_view.get_current_id())
            if not res:
                self.signals.globalCreateMessageNotificationSignal.emit({
                    "message_type": "error",
                    "message": "Error while deleting patient.",
                    "duration": 5000,
                })
                self.signals.globalLoadingNotificationControllerSignal.emit("DELETE_REPORT")
                return
            else:
                self.signals.globalReportUpdateTableViewSignal.emit()
                self.signals.updateReportsTrashTableSignal.emit()

            self.signals.globalLoadingNotificationControllerSignal.emit("DELETE_REPORT")

    @asyncSlot()
    async def get_all_category_options(self, category_id):
        category_options = await self.option_controller.get_options_by_category(category_id)
        if category_options:
            return category_options

    @pyqtSlot(int)
    def set_current_report_id(self, report_id):
        self.table_view.set_current_id(report_id)
        self.view_report()
