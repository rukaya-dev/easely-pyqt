from qasync import asyncSlot
from loggers.logger_configs import set_up_logger
from signals import SignalRepositorySingleton
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPalette
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QApplication, QLabel, QSizePolicy

from views.componenets.customsComponents.messages.no_data_widget import NoDataWidget
from views.componenets.customsComponents.table.form_componenets.next_pagination__button import NextPaginationButton
from views.componenets.customsComponents.table.form_componenets.previous_paginiation_button import \
    PreviousPaginationButton
from views.componenets.customsComponents.messages.not_found_search import NotFoundSearchMessageWidget
from views.componenets.table.mangement.table_model import TableModel
from views.componenets.table.mangement.table_view import TableView
from views.patient.patients_management_view.table.context_menu import ContextMenu

logger = set_up_logger('views.patient.patient_management_view.table.table_layout')


class TableLayout(QWidget):
    viewSignal = pyqtSignal()
    editSignal = pyqtSignal()
    deleteSignal = pyqtSignal()
    addAppointmentSignal = pyqtSignal()

    def __init__(self, table_name, data_controller, data_columns=None, column_display_names=None, is_pagination=True,
                 parent=None):
        super().__init__(parent)

        if data_columns is None:
            data_columns = ["id", "created_at"]

        self.parent = parent
        self.table_name = table_name
        self.is_pagination = is_pagination
        self.contextMenu = None
        self.add_btn = None
        self.table_view = None
        self.table_model = None
        self.current_cursor = None
        self.next_page_id = None
        self.current_id = None
        self.delete_action = None
        self.edit_action = None
        self.view_action = None
        self.export_action = None

        self.controller = data_controller

        # Signals
        self.signals = SignalRepositorySingleton.instance()

        self.table_model = TableModel(table_name=self.table_name, data_columns=data_columns, column_display_names=column_display_names)

        central_widget = QWidget()

        # Set up the QTableView
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

        if is_pagination:
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
        if self.parent.data:
            if len(self.parent.data["data"]) > 0:
                self.no_data_widget.hide()
                self.table_view.show()
                self.table_model.updateData(self.parent.data["data"])
                self.table_view.reset()
                if self.is_pagination:
                    self.pagination_widget.show()
                    self.update_pagination_text()
            else:
                self.table_view.hide()
                self.pagination_widget.hide()
                if not self.parent.data:
                    self.search_no_data_widget.show()
                else:
                    self.no_data_widget.show()
        else:
            self.no_data_widget.show()

    @asyncSlot()
    async def nextPage(self):
        if self.parent.data["next_page"] is None:
            return
        self.nextButton.start()
        try:

            await self.controller.get_items(page_number=self.parent.data["next_page"], item_per_page=20)
        except Exception as e:
            # Handle any other exception
            logger.error(e, exc_info=True)
            self.signals.globalLoadingNotificationControllerSignal.emit("GET_LIST")
        finally:

            data = self.controller.store.get_data()
            self.parent.data = data
            self.update_table_view()
            self.update_pagination_text()
            self.nextButton.stop()

    @asyncSlot()
    async def prevPage(self):
        if self.parent.data["prev_page"] is None:
            return
        self.prevButton.start()
        try:
            await self.controller.get_items(page_number=self.parent.data["prev_page"], item_per_page=20)

        except Exception as e:
            logger.error(e, exc_info=True)
            self.signals.globalLoadingNotificationControllerSignal.emit("GET_LIST")
        finally:
            data = self.controller.store.get_data()
            self.parent.data = data
            self.update_table_view()
            self.update_pagination_text()
            self.prevButton.stop()

    def update_pagination_text(self):
        self.total_items.setText(f"{self.parent.data['current_page']} / {self.parent.data['total_pages']} ")

    def get_current_id(self):
        return self.current_id

    def set_current_id(self, cid):
        self.current_id = cid

    def show_context_menu(self, position):
        if position is not None:
            index = self.table_view.indexAt(position)
            current_row = index.row()

            self.contextMenu = ContextMenu()

            self.contextMenu.itemSelected.connect(
                lambda item_id, row=current_row: self.menu_item_triggered(item_id, row))

            self.contextMenu.move(self.table_view.mapToGlobal(position))
            self.contextMenu.show()

    def menu_item_triggered(self, item_id, current_row_index):
        c_id = self.get_current_id_from_table_model(row_index=current_row_index)
        self.set_current_id(c_id)

        if item_id == "view":
            self.viewSignal.emit()

        elif item_id == "edit":
            self.editSignal.emit()

        elif item_id == "delete":
            self.deleteSignal.emit()

        elif item_id == "create_appointment":
            self.addAppointmentSignal.emit()

    def get_current_id_from_table_model(self, row_index):
        # Ensure the rowIndex is within the valid range
        if 0 <= row_index < self.table_model.rowCount():
            index = self.table_model.index(row_index, 0)
            current_id = self.table_model.data(index)
            if current_id:
                return current_id
        return None
