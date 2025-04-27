from PyQt6.QtCore import Qt, pyqtSlot, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QButtonGroup, QPushButton, \
    QAbstractButton, QLabel, QSizePolicy
from qasync import asyncSlot

from loggers.logger_configs import set_up_logger
from signals import SignalRepositorySingleton
from views.componenets.customsComponents.custom_searchbar import CustomSearchBar
from views.report.reports_management.report_filter_widget import FilterWidget

logger = set_up_logger('main.views.reports.table.table_header_filtration_component')


class TableHeaderFiltration(QWidget):
    updateTableContextMenu = pyqtSignal()

    def __init__(self, reports_controller, parent=None):
        super().__init__(parent)

        self.parent = parent

        self.reports_controller = reports_controller

        self.signals = SignalRepositorySingleton.instance()
        self.signals.globalReportStateManagementTabSignal.connect(self.show_tabs_widget_based_on_state)
        self.active_tab = None

        buttons_data = [
            {
                "name": "All",
                "id": "all"
            },
            {
                "name": "Recent",
                "id": "recent"
            },
            {
                "name": "Drafted",
                "id": "drafted"
            },
            {
                "name": "Finalized",
                "id": "finalized"
            },
            {
                "name": "Archived",
                "id": "archived"
            },

        ]

        self.dis_active_button_stylesheet = """
        QPushButton {
                border:0;
                border-radius:5px;
                color:#3F93D3;
                background-color:#E6F3FC;
            }
        """
        self.active_button_stylesheet = """
        QPushButton {
                border:0;
                border-radius:5px;
                color:white;
                background-color:#0C80E3;
            }
        """

        self.active_font = QFont()
        self.active_font.setPointSize(12)
        self.active_font.setWeight(self.active_font.Weight.DemiBold)

        self.dis_active_font = QFont()
        self.dis_active_font.setPointSize(12)
        self.dis_active_font.setWeight(self.dis_active_font.Weight.Normal)

        self.filter_buttons_group = QButtonGroup()
        self.search_filter_widget_placeholder = self.SearchAndFilterPlaceHolderWidget()
        self.search_filter_widget_placeholder.hide()

        self.main_h_filter_buttons_widget = QWidget()
        main_h_filter_buttons_layout = QHBoxLayout(self.main_h_filter_buttons_widget)
        main_h_filter_buttons_layout.setSpacing(10)
        main_h_filter_buttons_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        for i, item in enumerate(buttons_data):
            button = self.FilterButton(item, parent=self)
            self.filter_buttons_group.addButton(button)
            main_h_filter_buttons_layout.addWidget(button)
            if i == 0:
                self.change_filter_btn_style(button)
                self.current_active_filter_button = button

        self.filter_buttons_group.buttonClicked.connect(self.change_filter_btn_style)
        self.filter_buttons_group.buttonClicked.connect(self.apply_preset_filter)

        self.search_filter_widget = self.SearchAndFiltrationWidget(parent=self)

        self.main_h_layout = QHBoxLayout()
        self.main_h_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.main_h_layout.setContentsMargins(30, 0, 30, 10)

        self.main_h_layout.addWidget(self.main_h_filter_buttons_widget)
        self.main_h_layout.addWidget(self.search_filter_widget_placeholder)
        self.main_h_layout.addWidget(self.search_filter_widget)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(self.main_h_layout)

        self.setLayout(layout)

    @pyqtSlot(str)
    def show_tabs_widget_based_on_state(self, tab):
        if tab == 'search_filter':
            self.main_h_filter_buttons_widget.hide()
            self.search_filter_widget_placeholder.show()
            self.signals.globalReportUpdateTableViewSignal.emit()
        else:
            self.main_h_filter_buttons_widget.show()
            self.search_filter_widget_placeholder.hide()

    def change_filter_btn_style(self, button: QPushButton):
        button.setStyleSheet(self.active_button_stylesheet)
        button.setFont(self.active_font)
        for btn in self.filter_buttons_group.buttons():
            if btn != button:
                btn.setStyleSheet(self.dis_active_button_stylesheet)
                btn.setFont(self.dis_active_font)

    def check_search_and_filter(self):
        if len(self.search_filter_widget.search_bar.search_bar.text()) > 0 or self.search_filter_widget.filter_widget.filter_activated:
            self.reports_controller.store.set_active_report_tab("search_filter")
        else:
            self.reports_controller.store.set_active_report_tab(
                self.reports_controller.store.get_fallback_active_report_tab())

    @pyqtSlot(QAbstractButton)
    @asyncSlot()
    async def apply_preset_filter(self, button: QPushButton):
        filter_id = button.property("id")

        if self.active_tab == filter_id:
            return

        self.reports_controller.store.set_active_report_tab(button.property("id"))

        self.signals.globalCreateLoadingNotificationSignal.emit("APPLY_PRESET_FILTER")

        if filter_id == "all":
            data = await self.reports_controller.get_items_by_tabs(filter_id=filter_id, item_per_page=15,
                                                                   page_number=1)
            self.reports_controller.store.set_all_tab_data(data)

        if filter_id == "recent":
            data = await self.reports_controller.get_items_by_tabs(filter_id=filter_id, item_per_page=15,
                                                                   page_number=1)
            self.reports_controller.store.set_recent_tab_reports(data)

        elif filter_id == "drafted":
            data = await self.reports_controller.get_items_by_tabs(filter_id=filter_id, item_per_page=15,
                                                                   page_number=1)
            self.reports_controller.store.set_drafted_tab_reports(data)

        elif filter_id == "finalized":
            data = await self.reports_controller.get_items_by_tabs(filter_id=filter_id, item_per_page=15,
                                                                   page_number=1)
            self.reports_controller.store.set_finalized_tab_reports(data)

        elif filter_id == "archived":
            data = await self.reports_controller.get_items_by_tabs(filter_id=filter_id, item_per_page=15,
                                                                   page_number=1)
            self.reports_controller.store.set_archived_tab_reports(data)

        self.signals.globalReportUpdateTableViewSignal.emit()

        self.active_tab = filter_id

        self.signals.globalLoadingNotificationControllerSignal.emit("APPLY_PRESET_FILTER")

    class FilterButton(QPushButton):
        def __init__(self, data, parent=None):
            super().__init__(parent)

            self.parent = parent
            self.setFont(self.parent.dis_active_font)

            self.setText(data["name"])
            self.setProperty("id", data["id"])
            self.setStyleSheet(self.parent.dis_active_button_stylesheet)
            self.setFixedHeight(30)
            self.setMinimumWidth(80)

    class SearchAndFilterPlaceHolderWidget(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)

            label = QLabel("Search & Filter")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            font = label.font()
            font.setWeight(font.Weight.Bold)
            label.setFont(font)

            label.setStyleSheet("""
            QLabel {
                    border:0;
                    border-radius:5px;
                    color:white;
                    background-color:#0C80E3;
                    letter-spacing:0.5px;
                }
        """)
            label.setFixedSize(120, 38)
            label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

            self.setFixedHeight(48)

            layout = QVBoxLayout()
            layout.setAlignment(Qt.AlignmentFlag.AlignBottom)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(label, 0)
            self.setLayout(layout)

    class SearchAndFiltrationWidget(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)

            self.parent = parent

            self.add_btn = None
            self.left_layout = None
            self.search_bar = None
            self.right_layout = None

            self.reports_controller = self.parent.reports_controller

            self.search_bar = CustomSearchBar()
            self.search_bar.setToolTip(
                "Search patient national id, name, report title, category, doctor and referring doctor")
            self.search_bar.search_bar.setPlaceholderText("search patient, report title, category")
            self.search_bar.search_bar.textChanged.connect(self.on_search_text_change)

            self.filter_widget = FilterWidget(model_name="reports", controller=self.reports_controller, menu_pos="left",
                                              parent=self)

            main_h_layout = QHBoxLayout()
            main_h_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

            main_h_layout.setSpacing(0)
            main_h_layout.setContentsMargins(0, 0, 0, 0)

            main_h_layout.addWidget(self.filter_widget, 0, Qt.AlignmentFlag.AlignRight)
            main_h_layout.addWidget(self.search_bar, 0, Qt.AlignmentFlag.AlignRight)

            layout = QVBoxLayout()
            layout.setAlignment(Qt.AlignmentFlag.AlignRight)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addLayout(main_h_layout)

            self.setLayout(layout)

            self.setStyleSheet("background-color:white;")


        @pyqtSlot(str)
        def on_search_text_change(self, text):
            QTimer.singleShot(200, lambda: (self.update_search_filter(text)))

        @asyncSlot(str)
        async def update_search_filter(self, text):
            self.parent.check_search_and_filter()
            if len(text) >= 1:
                self.reports_controller.store.set_search_text(text)
                await self.reports_controller.search_reports()
                self.parent.signals.globalReportUpdateTableViewSignal.emit()
            else:
                self.reports_controller.store.set_search_text("")
                self.parent.signals.globalReportUpdateTableViewSignal.emit()
