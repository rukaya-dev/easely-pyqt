from PyQt6 import QtCore
from PyQt6.QtCore import Qt, QSize, pyqtSlot
from PyQt6.QtGui import QIcon, QPixmap, QStandardItemModel, QStandardItem, QDoubleValidator
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QSizePolicy
from qasync import asyncSlot

from configs.app_config import locale
from utils.validator import national_id_number_validator
from views.componenets.customsComponents.custom_checkbox import CustomCheckBox
from views.componenets.customsComponents.custom_combobox import CustomComboBox
from views.componenets.customsComponents.custom_scroll_area import CustomScrollArea
from views.componenets.customsComponents.dates_and_times.custom_time_picker import CustomTimePicker

from loggers.logger_configs import set_up_logger
from signals import SignalRepositorySingleton
from views.componenets.customsComponents.buttons.clear_button import CleatButton
from views.componenets.customsComponents.menus.date_filter_widget_with_checkbox import DateFilterWidgetWithCheckBox
from views.componenets.customsComponents.menus.drop_down_menu_component import CustomDropDownMenuComponent
from views.componenets.customsComponents.table.form_componenets.custom_input import CustomLineEdit
from views.componenets.customsComponents.table.save_and_cancel_buttons import SaveAndCancelButtonsWithLoader

logger = set_up_logger('main.views.appointment.appointment_filter_widget')


class FilterWidget(QWidget):
    def __init__(self, billing_controller, service_controller, parent=None):
        super().__init__(parent)

        self.service_id = None
        self.parent = parent
        self.filter_activated = False

        # Signals
        self.signals = SignalRepositorySingleton.instance()

        # API model
        self.billing_controller = billing_controller
        self.service_controller = service_controller

        double_validator = QDoubleValidator()
        double_validator.setLocale(locale)
        double_validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        double_validator.setBottom(0)

        self.filter_drop_down_widget = QWidget()

        self.filter_drop_down_vertical_layout = QVBoxLayout()
        self.filter_drop_down_vertical_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.filter_drop_down_widget.setContentsMargins(0, 0, 20, 0)
        self.filter_drop_down_vertical_layout.setSpacing(20)

        self.scroll_area = CustomScrollArea(self)
        self.scroll_area.setMinimumSize(500, 500)
        self.scroll_area.setContentsMargins(0, 0, 0, 0)
        self.scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setWidget(self.filter_drop_down_widget)

        central_widget = QWidget()
        central_widget.setStyleSheet("background-color:#f3f4f6;")

        central_layout = QVBoxLayout(central_widget)
        central_layout.setContentsMargins(30, 20, 2, 30)
        central_layout.addWidget(self.scroll_area)

        self.service_name_checkbox = CustomCheckBox("Service Name")
        self.service_name_checkbox.stateChanged.connect(self.handle_service_name_checkbox_state_changed)

        self.service_name_model = QStandardItemModel()

        self.service_name_selection_widget = CustomComboBox()
        self.service_name_selection_widget.setModel(self.service_name_model)
        self.service_name_selection_widget.currentIndexChanged.connect(self.on_service_name_index_changed)

        self.populate_services()
        self.handle_service_name_checkbox_state_changed(0)

        service_name_layout = QVBoxLayout()
        service_name_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        service_name_layout.setContentsMargins(0, 0, 0, 0)
        service_name_layout.setSpacing(20)

        service_name_layout.addWidget(self.service_name_checkbox)
        service_name_layout.addWidget(self.service_name_selection_widget)
        # ------------------------------------------------------------------------

        self.appointment_date = DateFilterWidgetWithCheckBox("Appointment Date")
        self.appointment_date.check_box.setChecked(False)

        # Start Time Slot
        self.appointment_time_checkbox = CustomCheckBox(name="Appointment Time", parent=self)
        self.appointment_time_checkbox.stateChanged.connect(self.handle_appointment_time_checkbox_state_changed)

        self.appointment_time_slot_widget = CustomTimePicker()
        self.handle_appointment_time_checkbox_state_changed(0)

        appointment_time_slot_layout = QVBoxLayout()
        appointment_time_slot_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        appointment_time_slot_layout.setContentsMargins(0, 0, 0, 0)
        appointment_time_slot_layout.setSpacing(20)

        appointment_time_slot_layout.addWidget(self.appointment_time_checkbox)
        appointment_time_slot_layout.addWidget(self.appointment_time_slot_widget)

        appointment_date_and_time_layout = QHBoxLayout()
        appointment_date_and_time_layout.setContentsMargins(0, 0, 0, 0)
        appointment_date_and_time_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        appointment_date_and_time_layout.addWidget(self.appointment_date)
        appointment_date_and_time_layout.addLayout(appointment_time_slot_layout)
        # ------------------------------------------------------------------------

        self.patient_national_id_number_checkbox = CustomCheckBox(name="Patient National ID Number", parent=self)

        self.patient_national_id_number_input = CustomLineEdit(placeholder_text="", parent=self)
        self.patient_national_id_number_input.setValidator(national_id_number_validator)
        self.patient_national_id_number_checkbox.stateChanged.connect(
            self.handle_patient_national_id_number_checkbox_state_changed)
        self.handle_patient_national_id_number_checkbox_state_changed(0)

        patient_national_id_number_layout = QVBoxLayout()
        patient_national_id_number_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        patient_national_id_number_layout.setContentsMargins(0, 0, 0, 0)
        patient_national_id_number_layout.setSpacing(20)

        patient_national_id_number_layout.addWidget(self.patient_national_id_number_checkbox)
        patient_national_id_number_layout.addWidget(self.patient_national_id_number_input)
        # ------------------------------------------------------------------------

        self.patient_checkbox = CustomCheckBox(name="Patient Name", parent=self)

        self.patient_firstname_input = CustomLineEdit(placeholder_text="first name", parent=self)

        self.patient_lastname_input = CustomLineEdit(placeholder_text="last name", parent=self)
        self.patient_checkbox.stateChanged.connect(self.handle_patient_checkbox_state_changed)
        self.handle_patient_checkbox_state_changed(0)

        patient_first_last_names_layout = QHBoxLayout()
        patient_first_last_names_layout.setSpacing(10)
        patient_first_last_names_layout.setContentsMargins(0, 0, 0, 0)
        patient_first_last_names_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        patient_first_last_names_layout.addWidget(self.patient_firstname_input)
        patient_first_last_names_layout.addWidget(self.patient_lastname_input)

        patient_layout = QVBoxLayout()
        patient_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        patient_layout.setContentsMargins(0, 0, 0, 0)
        patient_layout.setSpacing(20)

        patient_layout.addWidget(self.patient_checkbox)
        patient_layout.addLayout(patient_first_last_names_layout)
        # ------------------------------------------------------------------------

        self.total_amount_checkbox = CustomCheckBox(name="Total Amount", parent=self)

        self.total_amount_input = CustomLineEdit(placeholder_text="", parent=self)
        self.total_amount_input.setValidator(double_validator)
        self.total_amount_checkbox.stateChanged.connect(self.handle_total_amount_checkbox_state_changed)
        self.handle_total_amount_checkbox_state_changed(0)

        total_amount_layout = QVBoxLayout()
        total_amount_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        total_amount_layout.setContentsMargins(0, 0, 0, 0)
        total_amount_layout.setSpacing(20)

        total_amount_layout.addWidget(self.total_amount_checkbox)
        total_amount_layout.addWidget(self.total_amount_input)
        # ------------------------------------------------------------------------

        self.discount_checkbox = CustomCheckBox(name="Discount", parent=self)

        self.discount_input = CustomLineEdit(placeholder_text="", parent=self)
        self.discount_input.setValidator(double_validator)
        self.discount_checkbox.stateChanged.connect(self.handle_discount_checkbox_state_changed)
        self.handle_discount_checkbox_state_changed(0)

        discount_layout = QVBoxLayout()
        discount_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        discount_layout.setContentsMargins(0, 0, 0, 0)
        discount_layout.setSpacing(20)

        discount_layout.addWidget(self.discount_checkbox)
        discount_layout.addWidget(self.discount_input)
        # ------------------------------------------------------------------------

        self.net_amount_checkbox = CustomCheckBox(name="Net Amount", parent=self)

        self.net_amount_input = CustomLineEdit(placeholder_text="", parent=self)
        self.net_amount_input.setValidator(double_validator)
        self.net_amount_checkbox.stateChanged.connect(self.handle_net_amount_checkbox_state_changed)
        self.handle_net_amount_checkbox_state_changed(0)

        net_amount_layout = QVBoxLayout()
        net_amount_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        net_amount_layout.setContentsMargins(0, 0, 0, 0)
        net_amount_layout.setSpacing(20)

        net_amount_layout.addWidget(self.net_amount_checkbox)
        net_amount_layout.addWidget(self.net_amount_input)

        pricing = QHBoxLayout()
        pricing.setSpacing(10)
        pricing.setContentsMargins(0, 0, 0, 0)
        pricing.setAlignment(Qt.AlignmentFlag.AlignTop)

        pricing.addLayout(total_amount_layout)
        pricing.addLayout(discount_layout)
        pricing.addLayout(net_amount_layout)
        # ------------------------------------------------------------------------

        self.billing_date_date_filter_selection = DateFilterWidgetWithCheckBox("Billing Date")

        dates_layout = QVBoxLayout()
        dates_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        dates_layout.setContentsMargins(0, 0, 0, 0)
        dates_layout.addWidget(self.billing_date_date_filter_selection)

        self.save_and_cancel_buttons_widget = SaveAndCancelButtonsWithLoader(text="Save")
        self.save_and_cancel_buttons_widget.cancel_btn.clicked.connect(self.close_menu)

        self.save_and_cancel_buttons_widget.setFixedSize(QSize(200, 60))
        self.save_and_cancel_buttons_widget.save_btn.clicked.connect(self.apply_filter)

        self.clear_button = CleatButton()
        self.clear_button.button.clicked.connect(self.clear_filter)

        controls_layout = QHBoxLayout()
        controls_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.addWidget(self.clear_button, 0, Qt.AlignmentFlag.AlignLeft)
        controls_layout.addWidget(self.save_and_cancel_buttons_widget, 1, Qt.AlignmentFlag.AlignRight)

        self.filter_drop_down_vertical_layout.addLayout(patient_national_id_number_layout)
        self.filter_drop_down_vertical_layout.addLayout(patient_layout)
        self.filter_drop_down_vertical_layout.addLayout(service_name_layout)
        self.filter_drop_down_vertical_layout.addLayout(pricing)
        self.filter_drop_down_vertical_layout.addLayout(appointment_date_and_time_layout)
        self.filter_drop_down_vertical_layout.addLayout(dates_layout)
        self.filter_drop_down_vertical_layout.addLayout(controls_layout)

        self.filter_drop_down_widget.setLayout(self.filter_drop_down_vertical_layout)

        self.filter_toggle_menu_button = QPushButton()

        self.filter_toggle_menu_button.setStyleSheet("""
        QPushButton {
            border:0;
            background-color:transparent;
        }
        """)

        icon_pixmap = QPixmap(":resources/icons/filter.svg")
        icon = QIcon(icon_pixmap)

        self.filter_toggle_menu_button.setIcon(icon)
        self.filter_toggle_menu_button.setIconSize(QSize(20, 20))
        self.filter_toggle_menu_button.setFixedSize(QSize(50, 38))

        self.custom_drop_down_menu = CustomDropDownMenuComponent(menu_button=self.filter_toggle_menu_button,
                                                                 menu_pos="right",
                                                                 menu_widget=central_widget)

        filter_btn_layout = QHBoxLayout(self)
        filter_btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        filter_btn_layout.setContentsMargins(0, 0, 0, 0)
        filter_btn_layout.setSpacing(0)
        filter_btn_layout.addWidget(self.custom_drop_down_menu)

        self.setLayout(filter_btn_layout)

    def close_menu(self):
        self.custom_drop_down_menu.menu.close()

    def set_service_id(self, service_id):
        self.service_id = service_id

    @pyqtSlot(int)
    def on_service_name_index_changed(self, index):
        item = self.service_name_model.item(index)
        if item:
            service_id = item.data(QtCore.Qt.ItemDataRole.UserRole)
            self.set_service_id(service_id)

    @pyqtSlot(int)
    def handle_patient_national_id_number_checkbox_state_changed(self, state):
        if state == 2:
            self.patient_national_id_number_input.setDisabled(False)
        else:
            self.patient_national_id_number_input.setDisabled(True)

    @pyqtSlot(int)
    def handle_appointment_date_state_changed(self, state):
        if state == 2:
            self.appointment_date.setDisabled(False)
        else:
            self.appointment_date.setDisabled(True)

    @pyqtSlot(int)
    def handle_appointment_time_checkbox_state_changed(self, state):
        if state == 2:
            self.appointment_time_slot_widget.setDisabled(False)
        else:
            self.appointment_time_slot_widget.setDisabled(True)

    @pyqtSlot(int)
    def handle_patient_checkbox_state_changed(self, state):
        if state == 2:
            self.patient_firstname_input.setDisabled(False)
            self.patient_lastname_input.setDisabled(False)
        else:
            self.patient_firstname_input.setDisabled(True)
            self.patient_lastname_input.setDisabled(True)

    @pyqtSlot(int)
    def handle_total_amount_checkbox_state_changed(self, state):
        if state == 2:
            self.total_amount_input.setDisabled(False)
        else:
            self.total_amount_input.setDisabled(True)

    @pyqtSlot(int)
    def handle_discount_checkbox_state_changed(self, state):
        if state == 2:
            self.discount_input.setDisabled(False)
        else:
            self.discount_input.setDisabled(True)

    def populate_services(self):
        services = self.service_controller.store.get_data()
        if services or len(services) == 0:
            for item in services:
                standard_item = QStandardItem()
                standard_item.setData(item["name"], Qt.ItemDataRole.DisplayRole)
                standard_item.setData(item["service_id"], Qt.ItemDataRole.UserRole)
                self.service_name_model.appendRow(standard_item)

    @pyqtSlot(int)
    def handle_service_name_checkbox_state_changed(self, state):
        if state == 2:
            self.service_name_selection_widget.setEnabled(True)
        else:
            self.service_name_selection_widget.setEnabled(False)

    @pyqtSlot(int)
    def handle_net_amount_checkbox_state_changed(self, state):
        if state == 2:
            self.net_amount_input.setEnabled(True)
        else:
            self.net_amount_input.setEnabled(False)

    @pyqtSlot()
    @asyncSlot()
    async def clear_filter(self):
        self.signals.globalCreateLoadingNotificationSignal.emit("GET_BILLINGS_INITIAL_DATA")
        self.service_name_checkbox.setChecked(False)
        self.handle_service_name_checkbox_state_changed(0)

        self.patient_national_id_number_checkbox.setChecked(False)
        self.patient_national_id_number_input.clear()
        self.handle_patient_national_id_number_checkbox_state_changed(0)

        self.net_amount_checkbox.setChecked(False)
        self.net_amount_input.clear()
        self.handle_net_amount_checkbox_state_changed(0)

        self.appointment_date.check_box.setChecked(False)

        self.appointment_time_checkbox.setChecked(False)
        self.handle_appointment_time_checkbox_state_changed(0)

        self.patient_checkbox.setChecked(False)
        self.patient_firstname_input.clear()
        self.patient_lastname_input.clear()
        self.handle_patient_checkbox_state_changed(0)

        self.total_amount_checkbox.setChecked(False)
        self.total_amount_input.clear()
        self.handle_total_amount_checkbox_state_changed(0)

        self.discount_checkbox.setChecked(False)
        self.discount_input.clear()
        self.handle_discount_checkbox_state_changed(0)

        self.billing_date_date_filter_selection.check_box.setChecked(False)
        self.billing_controller.store.set_filter_preferences({})
        await self.parent.refresh_table()
        self.signals.globalLoadingNotificationControllerSignal.emit("GET_BILLINGS_INITIAL_DATA")
        self.close_menu()

    @pyqtSlot()
    @asyncSlot()
    async def apply_filter(self):
        self.save_and_cancel_buttons_widget.save_btn.start()

        national_id_number = self.patient_national_id_number_input.text()
        service_name = self.service_name_selection_widget.currentText()
        appointment_date = self.appointment_date.custom_date_range_selection_widget.selection_widget.custom_date_calendar.selectedDate().toString()
        appointment_time_slot = self.appointment_time_slot_widget.time().toString("HH:mm")
        patient_firstname = self.patient_firstname_input.text()
        patient_lastname = self.patient_lastname_input.text()
        total_amount = self.total_amount_input.text()
        discount = self.discount_input.text()
        net_amount = self.net_amount_input.text()
        billing_date = self.billing_date_date_filter_selection.custom_date_range_selection_widget.selection_widget.custom_date_calendar.selectedDate().toString()

        preferences = {
            "service_name": {
                "enabled": False,
                "service_name_value": "",
            },
            "national_id_number": {
                "enabled": False,
                "national_id_number_value": "",
            },
            "appointment_date": {
                "enabled": False,
                "filteration_type": "",
                "preset_filter_id": "",
                "custom_date_value": "",
            },
            "appointment_time": {
                "enabled": False,
                "time_slot_value": "",
            },
            "patient": {
                "enabled": False,
                "firstname": "",
                "lastname": "",
            },
            "total_amount": {
                "enabled": False,
                "amount": "",
            },
            "discount": {
                "enabled": False,
                "amount": "",
            },
            "net_amount": {
                "enabled": False,
                "amount": "",
            },
            "billing_date": {
                "enabled": False,
                "filteration_type": "",
                "preset_filter_id": "",
                "custom_date_value": "",
            },
            "updated_at": {
                "enabled": False,
                "filteration_type": "",
                "preset_filter_id": "",
                "custom_date_value": "",
            },
        }

        if self.patient_national_id_number_checkbox.isChecked():
            preferences["national_id_number"]["enabled"] = True
            if service_name:
                preferences["national_id_number"]["national_id_number_value"] = national_id_number

        if self.service_name_checkbox.isChecked():
            preferences["service_name"]["enabled"] = True
            if service_name:
                preferences["service_name"]["service_name_value"] = service_name

        if self.appointment_date.check_box.isChecked():
            preferences["appointment_date"]["enabled"] = True
            present_filter_checked_action = self.appointment_date.preset_date_filter_selection_widget.menu.actions_group.checkedAction()
            if present_filter_checked_action:
                preferences["appointment_date"]["filteration_type"] = "preset_filter"
                preset_filter_data = present_filter_checked_action.data()
                preferences["appointment_date"]["preset_filter_id"] = preset_filter_data["id"]
            else:
                preferences["appointment_date"]["filteration_type"] = "custom_filter"
                preferences["appointment_date"]["custom_date_value"] = appointment_date

        if self.appointment_time_checkbox.isChecked():
            preferences["appointment_time"]["enabled"] = True
            if appointment_time_slot:
                preferences["appointment_time"]["time_slot_value"] = appointment_time_slot

        if self.patient_checkbox.isChecked():
            preferences["patient"]["enabled"] = True
            if patient_firstname or patient_lastname:
                preferences["patient"]["firstname"] = patient_firstname
                preferences["patient"]["lastname"] = patient_lastname

        if self.total_amount_checkbox.isChecked():
            preferences["total_amount"]["enabled"] = True
            if total_amount:
                preferences["total_amount"]["amount"] = total_amount

        if self.discount_checkbox.isChecked():
            preferences["discount"]["enabled"] = True
            if discount:
                preferences["discount"]["amount"] = discount

        if self.net_amount_checkbox.isChecked():
            preferences["net_amount"]["enabled"] = True
            if net_amount:
                preferences["net_amount"]["amount"] = net_amount

        if self.billing_date_date_filter_selection.check_box.isChecked():
            preferences["billing_date"]["enabled"] = True
            present_filter_checked_action = self.billing_date_date_filter_selection.preset_date_filter_selection_widget.menu.actions_group.checkedAction()
            if present_filter_checked_action:
                preferences["billing_date"]["filteration_type"] = "preset_filter"
                preset_filter_data = present_filter_checked_action.data()
                preferences["billing_date"]["preset_filter_id"] = preset_filter_data["id"]
            else:
                preferences["billing_date"]["filteration_type"] = "custom_filter"
                preferences["billing_date"]["custom_date_value"] = billing_date

        self.billing_controller.store.set_filter_preferences(preferences)
        
        await self.parent.refresh_table()
        self.save_and_cancel_buttons_widget.save_btn.stop()
        self.close_menu()
