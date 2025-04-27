from qasync import asyncSlot
from loggers.logger_configs import set_up_logger
from signals import SignalRepositorySingleton
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QSizePolicy

from views.appointement.table.context_menu import ContextMenu
from views.componenets.customsComponents.messages.no_data_widget import NoDataWidget
from views.componenets.customsComponents.table.form_componenets.next_pagination__button import NextPaginationButton
from views.componenets.customsComponents.table.form_componenets.previous_paginiation_button import \
    PreviousPaginationButton
from views.componenets.customsComponents.messages.not_found_search import NotFoundSearchMessageWidget
from views.componenets.table.mangement.table_model import TableModel
from views.componenets.table.mangement.table_view import TableView

logger = set_up_logger('views.appointment.table.table_layout')


class TableLayout(QWidget):
    viewSignal = pyqtSignal()
    editStatusSignal = pyqtSignal()
    editAdditionalDataSignal = pyqtSignal()
    addAppointmentSignal = pyqtSignal()
    re_scheduleAppointmentSignal = pyqtSignal()
    cancelAppointmentSignal = pyqtSignal()
    makeReportSignal = pyqtSignal()

    def __init__(self, data_controller, data_columns=None, column_display_names=None, parent=None):
        super().__init__(parent)

        self.active_tab = None
        if data_columns is None:
            data_columns = ["id", "created_at"]

        self.parent = parent

        self.controller = data_controller

        self.context_menu = None
        self.current_id = None

        # Signals
        self.signals = SignalRepositorySingleton.instance()
        self.signals.globalAppointmentUpdateTableViewSignal.connect(self.update_table_view)

        self.table_model = TableModel(table_name="appointments", data_columns=data_columns,
                                      column_display_names=column_display_names)

        central_widget = QWidget()

        self.table_view = TableView()
        self.table_view.setModel(self.table_model)

        self.table_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_view.customContextMenuRequested.connect(self.show_context_menu)

        # Pagination controls
        self.pagination_widget = QWidget()
        self.pagination_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self.prevButton = PreviousPaginationButton()
        self.prevButton.clicked.connect(self.prevPage)

        self.nextButton = NextPaginationButton()
        self.nextButton.clicked.connect(self.nextPage)

        # Label text count
        self.total_items = QLabel()
        self.total_items.setStyleSheet("font-size:14px;color:black;font-weight:300px;")
        self.total_items.setAlignment(Qt.AlignmentFlag.AlignCenter)

        pagination_layout = QHBoxLayout()
        pagination_layout.setContentsMargins(20, 20, 20, 20)
        pagination_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        pagination_layout.addWidget(self.prevButton)
        pagination_layout.addWidget(self.total_items)
        pagination_layout.addWidget(self.nextButton)
        self.pagination_widget.setLayout(pagination_layout)

        # Not found widget
        self.no_data_widget = NoDataWidget()
        self.no_data_widget.hide()

        # Search isn't found
        self.search_no_data_widget = NotFoundSearchMessageWidget()
        self.search_no_data_widget.hide()

        table_content_v_layout = QVBoxLayout()
        table_content_v_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        table_content_v_layout.setContentsMargins(0, 0, 0, 0)
        table_content_v_layout.setSpacing(0)

        table_content_v_layout.addWidget(self.table_view)
        table_content_v_layout.addWidget(self.no_data_widget, Qt.AlignmentFlag.AlignCenter)
        table_content_v_layout.addWidget(self.search_no_data_widget, Qt.AlignmentFlag.AlignCenter)

        table_content_v_layout.addWidget(self.pagination_widget)
        table_content_v_layout.setAlignment(self.pagination_widget, Qt.AlignmentFlag.AlignRight)
        central_widget.setLayout(table_content_v_layout)

        main_h_layout = QHBoxLayout()
        main_h_layout.setContentsMargins(20, 0, 20, 20)
        main_h_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_h_layout.addWidget(central_widget)

        self.setLayout(main_h_layout)
        self.table_model.dataChanged.connect(self.table_view.update)

    def update_table_view(self):
        self.active_tab = self.controller.store.get_active_appointment_tab()
        tab_data_map = {
            "all": self.controller.store.get_all_tab_data(),
            "scheduled": self.controller.store.get_scheduled_data(),
            "upcoming": self.controller.store.get_upcoming_tab_data(),
            "expired": self.controller.store.get_expired_tab_data(),
            "canceled": self.controller.store.get_canceled_tab_data(),
            "search_filter": self.controller.store.get_search_filter_tab_data(),
        }

        data = tab_data_map.get(self.active_tab, tab_data_map[self.active_tab])
        if isinstance(data, dict):
            if len(data.get("data", [])) > 0:
                self.search_no_data_widget.hide()
                self.no_data_widget.hide()
                self.table_view.show()
                self.table_model.updateData(data["data"])
                self.table_view.reset()
                self.pagination_widget.show()
                self.update_pagination_text()
            else:
                self.table_view.hide()
                self.pagination_widget.hide()
                self.no_data_widget.show()
        else:
            self.table_view.hide()
            self.pagination_widget.hide()
            self.no_data_widget.show()

    @asyncSlot()
    async def nextPage(self):
        tab_data_map = {
            "all": self.controller.store.get_all_tab_data(),
            "scheduled": self.controller.store.get_scheduled_data(),
            "upcoming": self.controller.store.get_upcoming_tab_data(),
            "expired": self.controller.store.get_expired_tab_data(),
            "canceled": self.controller.store.get_canceled_tab_data(),
            "search_filter": self.controller.store.get_search_filter_tab_data(),
        }

        # Check if next_page is None for the active tab
        active_tab_data = tab_data_map.get(self.active_tab)
        if active_tab_data and active_tab_data.get("next_page") is None:
            return

        self.nextButton.start()
        self.active_tab = self.controller.store.get_active_appointment_tab()

        try:
            next_page = tab_data_map[self.active_tab]["next_page"]

            if self.active_tab == "search_filter":
                await self.controller.get_items(item_per_page=15, page_number=next_page)
            else:
                await self.controller.get_items_by_tabs(self.active_tab, item_per_page=15, page_number=next_page)

        except Exception as e:
            logger.error(e, exc_info=True)
            self.signals.globalLoadingNotificationControllerSignal.emit("GET_LIST")

        finally:
            tab_data_update_method = f"get_{self.active_tab}_tab_data"

            setattr(self.controller.store, f"{self.active_tab}_data_tab",
                    getattr(self.controller.store, tab_data_update_method)())

            self.update_table_view()
            self.update_pagination_text()
            self.nextButton.stop()

    @asyncSlot()
    async def prevPage(self):
        tab_data_map = {
            "all": self.controller.store.get_all_tab_data(),
            "scheduled": self.controller.store.get_scheduled_data(),
            "upcoming": self.controller.store.get_upcoming_tab_data(),
            "expired": self.controller.store.get_expired_tab_data(),
            "canceled": self.controller.store.get_canceled_tab_data(),
            "search_filter": self.controller.store.get_search_filter_tab_data(),
        }

        active_tab_data = tab_data_map.get(self.active_tab)
        if active_tab_data and active_tab_data.get("prev_page") is None:
            return

        self.prevButton.start()
        self.active_tab = self.controller.store.get_active_appointment_tab()

        try:
            prev_page = tab_data_map[self.active_tab]["prev_page"]
            if self.active_tab == "search_filter":
                await self.controller.get_items(item_per_page=15, page_number=prev_page)
            else:
                await self.controller.get_items_by_tabs(self.active_tab, item_per_page=15, page_number=prev_page)

        except Exception as e:
            logger.error(e, exc_info=True)
            self.signals.globalLoadingNotificationControllerSignal.emit("GET_LIST")

        finally:
            tab_data_update_method = f"get_{self.active_tab}_tab_data"

            setattr(self.controller.store, f"{self.active_tab}_data_tab",
                    getattr(self.controller.store, tab_data_update_method)())

            self.update_table_view()
            self.update_pagination_text()
            self.prevButton.stop()

    def update_pagination_text(self):
        tab_data_map = {
            "all": self.controller.store.get_all_tab_data(),
            "scheduled": self.controller.store.get_scheduled_data(),
            "upcoming": self.controller.store.get_upcoming_tab_data(),
            "expired": self.controller.store.get_expired_tab_data(),
            "canceled": self.controller.store.get_canceled_tab_data(),
            "search_filter": self.controller.store.get_search_filter_tab_data(),
        }

        active_tab_data = tab_data_map.get(self.active_tab)

        self.total_items.setText(f"{active_tab_data['current_page']} / {active_tab_data['total_pages']} ")

    def get_current_id(self):
        return self.current_id

    def set_current_id(self, cid):
        self.current_id = cid

    def show_context_menu(self, position):
        if position is not None:
            index = self.table_view.indexAt(position)
            current_row = index.row()

            self.context_menu = ContextMenu(self.controller, parent=self)

            self.context_menu.itemSelected.connect(
                lambda item_id, row=current_row: self.menu_item_triggered(item_id, row))

            self.context_menu.move(self.table_view.mapToGlobal(position))
            self.context_menu.show()

    def menu_item_triggered(self, item_id, current_row_index):
        c_id = self.get_current_id_from_table_model(row_index=current_row_index)
        self.set_current_id(c_id)

        if item_id == "view":
            self.viewSignal.emit()

        elif item_id == "edit_status":
            self.editStatusSignal.emit()

        elif item_id == "edit_additional_data":
            self.editAdditionalDataSignal.emit()

        elif item_id == "re_schedule":
            self.re_scheduleAppointmentSignal.emit()

        elif item_id == "cancel_appointment":
            self.cancelAppointmentSignal.emit()

        elif item_id == "make_report":
            self.makeReportSignal.emit()

    def get_current_id_from_table_model(self, row_index):
        if 0 <= row_index < self.table_model.rowCount():
            index = self.table_model.index(row_index, 0)
            current_id = self.table_model.data(index)
            if current_id:
                return current_id
        return None
