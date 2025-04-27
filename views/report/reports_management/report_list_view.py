import asyncio
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget

from services.supabase.controllers.report.report_controller import ReportController
from signals import SignalRepositorySingleton
from views.report.reports_management.recent_reports import RecentReports
from views.report.reports_management.reports_management_view import ReportManagementView


class ReportListView(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # Signals
        self.recent_report_list = None
        self.central_widget = None
        self.report_table_management_view = None
        self.recent_reports = None
        self.data = None
        self.signals = SignalRepositorySingleton.instance()

        self.report_controller = ReportController()

        self.stacked_content_widget = QStackedWidget()

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stacked_content_widget)

        self.setLayout(layout)
        asyncio.create_task(self.get_initial_data())

    async def get_initial_data(self):
        self.signals.globalCreateLoadingNotificationSignal.emit("GET_REPORTS_LIST")

        self.data = await self.report_controller.get_items_by_tabs("all", page_number=1, item_per_page=20)

        self.recent_report_list = await self.report_controller.get_items_by_tabs("recent", 4, 1)

        await self.setup_table_ui()

        self.signals.globalLoadingNotificationControllerSignal.emit("GET_REPORTS_LIST")

    async def setup_table_ui(self):
        self.recent_reports = RecentReports(self.recent_report_list, controller=self.report_controller)
        self.report_table_management_view = ReportManagementView(self.data,
                                                                 report_controller=self.report_controller,
                                                                 parent=self)

        self.central_widget = QWidget()

        main_h_layout = QHBoxLayout(self.central_widget)
        main_h_layout.setSpacing(30)
        main_h_layout.setContentsMargins(0, 0, 0, 0)
        main_h_layout.addWidget(self.recent_reports)
        main_h_layout.addWidget(self.report_table_management_view, 1)

        self.set_main_content(self.central_widget)

    def set_main_content(self, content_widget):
        self.stacked_content_widget.addWidget(content_widget)
        self.stacked_content_widget.setCurrentWidget(content_widget)

