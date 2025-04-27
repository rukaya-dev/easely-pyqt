from PyQt6.QtCore import Qt, pyqtSlot, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QButtonGroup, QPushButton, \
    QAbstractButton, QLabel, QSizePolicy
from qasync import asyncSlot

from loggers.logger_configs import set_up_logger
from signals import SignalRepositorySingleton
from views.appointement.filter.appointment_filter_widget import FilterWidget
from views.componenets.customsComponents.custom_searchbar import CustomSearchBar

logger = set_up_logger('main.views.appointment.table.table_header_filtration_component')


class TableHeaderFiltration(QWidget):
    updateTableContextMenu = pyqtSignal()

    def __init__(self, appointments_controller, appointment_statuses_controller, service_controller, parent=None):
        super().__init__(parent)

        self.parent = parent

        self.appointments_controller = appointments_controller
        self.appointment_statuses_controller = appointment_statuses_controller
        self.service_controller = service_controller

        self.signals = SignalRepositorySingleton.instance()
        self.signals.globalAppointmentStateManagementTabSignal.connect(self.show_tabs_widget_based_on_state)
        self.active_tab = None

        buttons_data = [
            {
                "name": "All",
                "id": "all"
            },
            {
                "name": "Scheduled",
                "id": "scheduled"
            },
            {
                "name": "Upcoming",
                "id": "upcoming"
            },
            {
                "name": "Expired",
                "id": "expired"
            },
            {
                "name": "Canceled",
                "id": "canceled"
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
            self.signals.globalAppointmentUpdateTableViewSignal.emit()
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
            self.appointments_controller.store.set_active_appointment_tab("search_filter")
        else:
            self.appointments_controller.store.set_active_appointment_tab(
                self.appointments_controller.store.get_fallback_active_appointment_tab())

    @pyqtSlot(QAbstractButton)
    @asyncSlot()
    async def apply_preset_filter(self, button: QPushButton):
        filter_id = button.property("id")

        if self.active_tab == filter_id:
            return

        self.appointments_controller.store.set_active_appointment_tab(button.property("id"))

        self.signals.globalCreateLoadingNotificationSignal.emit("APPLY_PRESET_FILTER")

        if filter_id == "all":
            data = await self.appointments_controller.get_items_by_tabs(filter_id=filter_id, item_per_page=15,
                                                                        page_number=1)
            self.appointments_controller.store.set_all_tab_data(data)

        if filter_id == "scheduled":
            data = await self.appointments_controller.get_items_by_tabs(filter_id=filter_id, item_per_page=15,
                                                                        page_number=1)
            self.appointments_controller.store.set_scheduled_data(data)

        elif filter_id == "upcoming":
            data = await self.appointments_controller.get_items_by_tabs(filter_id=filter_id, item_per_page=15,
                                                                        page_number=1)
            self.appointments_controller.store.set_upcoming_tab_data(data)

        elif filter_id == "canceled":
            data = await self.appointments_controller.get_items_by_tabs(filter_id=filter_id, item_per_page=15,
                                                                        page_number=1)
            self.appointments_controller.store.set_canceled_tab_data(data)

        elif filter_id == "expired":
            data = await self.appointments_controller.get_items_by_tabs(filter_id=filter_id, item_per_page=15,
                                                                        page_number=1)
            self.appointments_controller.store.set_expired_tab_data(data)

        self.signals.globalAppointmentUpdateTableViewSignal.emit()
        self.active_tab = filter_id

        self.signals.globalLoadingNotificationControllerSignal.emit("APPLY_PRESET_FILTER")

    class FilterButton(QPushButton):
        def __init__(self, data, parent=None):
            super().__init__(parent)

            self.parent = parent
            self.setFont(self.parent.dis_active_font)

            self.setText(f'{data["name"]}')
            self.setProperty("id", data["id"])
            self.setObjectName(data["name"])
            self.setStyleSheet(self.parent.dis_active_button_stylesheet)
            self.setFixedHeight(30)
            self.setMinimumWidth(95)

    class SearchAndFilterPlaceHolderWidget(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)

            label = QLabel("Search & Filter")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            font = label.font()
            font.setPointSize(12)
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
            label.setFixedSize(140, 34)
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

            self.appointment_controller = self.parent.appointments_controller
            self.appointment_statuses_controller = self.parent.appointment_statuses_controller
            self.service_controller = self.parent.service_controller

            self.search_bar = CustomSearchBar()
            self.search_bar.search_bar.setPlaceholderText("search patient national id, first name, last name")
            self.search_bar.setToolTip("search patient national id, first name, last name")
            self.search_bar.search_bar.textChanged.connect(self.on_search_text_change)

            self.filter_widget = FilterWidget(appointment_controller=self.appointment_controller,
                                              appointment_statuses_controller=self.appointment_statuses_controller,
                                              service_controller=self.service_controller,
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

        @pyqtSlot(str)
        def on_search_text_change(self, text):
            QTimer.singleShot(200, lambda: (self.update_search_filter(text)))

        @asyncSlot(str)
        async def update_search_filter(self, text):
            self.parent.check_search_and_filter()
            if len(text) >= 1:
                self.appointment_controller.store.set_search_text(text)
                await self.appointment_controller.search_appointments()
                self.parent.signals.globalAppointmentUpdateTableViewSignal.emit()
            else:
                self.appointment_controller.store.set_search_text("")
                self.parent.signals.globalAppointmentUpdateTableViewSignal.emit()

