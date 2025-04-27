from PyQt6 import QtCore
from PyQt6.QtCore import Qt, QSize, pyqtSlot
from PyQt6.QtGui import QIcon, QPixmap, QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QSizePolicy
from qasync import asyncSlot

from views.appointement.filter.future_date_selection_filter_widget_with_check_box import \
    FutureDateFilterWidgetWithCheckBox
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
    def __init__(self, appointment_controller, appointment_statuses_controller, service_controller, parent=None):
        super().__init__(parent)

        self.service_id = None
        self.parent = parent
        self.filter_activated = False

        self.first_name_placeholder = "first name"
        self.last_name_placeholder = "last name"

        # Signals
        self.signals = SignalRepositorySingleton.instance()

        # API model
        self.appointment_controller = appointment_controller
        self.service_controller = service_controller
        self.appointment_statuses_controller = appointment_statuses_controller

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
        self.appointment_status_checkbox = CustomCheckBox("Appointment Status")
        self.appointment_status_checkbox.stateChanged.connect(self.handle_appointment_status_checkbox_state_changed)

        self.appointment_status_model = QStandardItemModel()

        self.appointment_status_selection_widget = CustomComboBox()
        self.appointment_status_selection_widget.setModel(self.appointment_status_model)
        self.appointment_status_selection_widget.currentIndexChanged.connect(self.on_service_name_index_changed)

        self.populate_appointment_statuses()
        self.handle_appointment_status_checkbox_state_changed(0)

        appointment_status_layout = QVBoxLayout()
        appointment_status_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        appointment_status_layout.setContentsMargins(0, 0, 0, 0)
        appointment_status_layout.setSpacing(20)

        appointment_status_layout.addWidget(self.appointment_status_checkbox)
        appointment_status_layout.addWidget(self.appointment_status_selection_widget)
        # ------------------------------------------------------------------------

        self.appointment_date = FutureDateFilterWidgetWithCheckBox("Appointment Date")
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

        self.patient_firstname_input = CustomLineEdit(placeholder_text=self.first_name_placeholder, parent=self)

        self.patient_lastname_input = CustomLineEdit(placeholder_text=self.last_name_placeholder, parent=self)
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

        self.doctor_checkbox = CustomCheckBox(name="Doctor", parent=self)

        self.doctor_firstname_input = CustomLineEdit(placeholder_text=self.first_name_placeholder, parent=self)
        self.doctor_lastname_input = CustomLineEdit(placeholder_text=self.last_name_placeholder, parent=self)
        self.doctor_checkbox.stateChanged.connect(self.handle_doctor_checkbox_state_changed)
        self.handle_doctor_checkbox_state_changed(0)

        doctor_first_last_names_layout = QHBoxLayout()
        doctor_first_last_names_layout.setSpacing(10)
        doctor_first_last_names_layout.setContentsMargins(0, 0, 0, 0)
        doctor_first_last_names_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        doctor_first_last_names_layout.addWidget(self.doctor_firstname_input)
        doctor_first_last_names_layout.addWidget(self.doctor_lastname_input)

        doctor_layout = QVBoxLayout()
        doctor_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        doctor_layout.setContentsMargins(0, 0, 0, 0)
        doctor_layout.setSpacing(20)

        doctor_layout.addWidget(self.doctor_checkbox)
        doctor_layout.addLayout(doctor_first_last_names_layout)
        # ------------------------------------------------------------------------

        self.assistant_checkbox = CustomCheckBox(name="Assistant", parent=self)

        self.assistant_firstname_input = CustomLineEdit(placeholder_text=self.first_name_placeholder, parent=self)
        self.assistant_lastname_input = CustomLineEdit(placeholder_text=self.last_name_placeholder, parent=self)
        self.assistant_checkbox.stateChanged.connect(self.handle_assistant_checkbox_state_changed)
        self.handle_assistant_checkbox_state_changed(0)

        assistant_first_last_names_layout = QHBoxLayout()
        assistant_first_last_names_layout.setSpacing(10)
        assistant_first_last_names_layout.setContentsMargins(0, 0, 0, 0)
        assistant_first_last_names_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        assistant_first_last_names_layout.addWidget(self.assistant_firstname_input)
        assistant_first_last_names_layout.addWidget(self.assistant_lastname_input)

        assistant_layout = QVBoxLayout()
        assistant_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        assistant_layout.setContentsMargins(0, 0, 0, 0)
        assistant_layout.setSpacing(20)

        assistant_layout.addWidget(self.assistant_checkbox)
        assistant_layout.addLayout(assistant_first_last_names_layout)
        # ------------------------------------------------------------------------

        self.created_at_date_filter_selection = DateFilterWidgetWithCheckBox("Created at")
        self.updated_at_date_filter_selection = DateFilterWidgetWithCheckBox("Updated at")

        dates_layout = QVBoxLayout()
        dates_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        dates_layout.setContentsMargins(0, 0, 0, 0)
        dates_layout.addWidget(self.created_at_date_filter_selection)
        dates_layout.addWidget(self.updated_at_date_filter_selection)

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
        self.filter_drop_down_vertical_layout.addLayout(doctor_layout)
        self.filter_drop_down_vertical_layout.addLayout(assistant_layout)
        self.filter_drop_down_vertical_layout.addLayout(appointment_status_layout)
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
                                                                 menu_pos="left",
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
    def handle_doctor_checkbox_state_changed(self, state):
        if state == 2:
            self.doctor_firstname_input.setDisabled(False)
            self.doctor_lastname_input.setDisabled(False)
        else:
            self.doctor_firstname_input.setDisabled(True)
            self.doctor_lastname_input.setDisabled(True)

    @pyqtSlot(int)
    def handle_assistant_checkbox_state_changed(self, state):
        if state == 2:
            self.assistant_firstname_input.setDisabled(False)
            self.assistant_lastname_input.setDisabled(False)
        else:
            self.assistant_firstname_input.setDisabled(True)
            self.assistant_lastname_input.setDisabled(True)

    def populate_services(self):
        services = self.service_controller.store.get_data()
        if services:
            for item in services:
                standard_item = QStandardItem()
                standard_item.setData(item["name"], Qt.ItemDataRole.DisplayRole)
                standard_item.setData(item["service_id"], Qt.ItemDataRole.UserRole)
                self.service_name_model.appendRow(standard_item)

    @asyncSlot()
    async def populate_appointment_statuses(self):
        statuses = self.appointment_statuses_controller.store.get_data()
        if statuses:
            for item in statuses:
                standard_item = QStandardItem()
                standard_item.setData(item["status_name"], Qt.ItemDataRole.DisplayRole)
                standard_item.setData(item["status_id"], Qt.ItemDataRole.UserRole)
                self.appointment_status_model.appendRow(standard_item)

    @pyqtSlot(int)
    def handle_service_name_checkbox_state_changed(self, state):
        if state == 2:
            self.service_name_selection_widget.setEnabled(True)
        else:
            self.service_name_selection_widget.setEnabled(False)

    @pyqtSlot(int)
    def handle_appointment_status_checkbox_state_changed(self, state):
        if state == 2:
            self.appointment_status_selection_widget.setEnabled(True)
        else:
            self.appointment_status_selection_widget.setEnabled(False)

    @pyqtSlot()
    @asyncSlot()
    async def clear_filter(self):

        self.appointment_controller.store.set_active_appointment_tab(
            self.appointment_controller.store.get_fallback_active_appointment_tab())
        self.signals.globalAppointmentUpdateTableViewSignal.emit()

        self.service_name_checkbox.setChecked(False)
        self.handle_service_name_checkbox_state_changed(0)

        self.patient_national_id_number_checkbox.setChecked(False)
        self.patient_national_id_number_input.clear()
        self.handle_patient_national_id_number_checkbox_state_changed(0)

        self.appointment_status_checkbox.setChecked(False)
        self.handle_appointment_status_checkbox_state_changed(0)

        self.appointment_date.check_box.setChecked(False)

        self.appointment_time_checkbox.setChecked(False)
        self.handle_appointment_time_checkbox_state_changed(0)

        self.patient_checkbox.setChecked(False)
        self.patient_firstname_input.clear()
        self.patient_lastname_input.clear()
        self.handle_patient_checkbox_state_changed(0)

        self.doctor_checkbox.setChecked(False)
        self.doctor_lastname_input.clear()
        self.doctor_lastname_input.clear()
        self.handle_doctor_checkbox_state_changed(0)

        self.assistant_checkbox.setChecked(False)
        self.assistant_firstname_input.clear()
        self.assistant_lastname_input.clear()
        self.handle_assistant_checkbox_state_changed(0)

        self.created_at_date_filter_selection.check_box.setChecked(False)
        self.updated_at_date_filter_selection.check_box.setChecked(False)
        self.appointment_controller.store.set_filter_preferences({})
        self.close_menu()

    @pyqtSlot()
    @asyncSlot()
    async def apply_filter(self):
        self.filter_activated = True
        self.parent.parent.check_search_and_filter()
        self.signals.globalCreateLoadingNotificationSignal.emit("APPLY_APPOINTMENT_FILTER")

        national_id_number = self.patient_national_id_number_input.text()
        service_name = self.service_name_selection_widget.currentText()
        appointment_status = self.appointment_status_selection_widget.currentText()
        appointment_date = self.appointment_date.custom_date_range_selection_widget.selection_widget.custom_date_calendar.selectedDate().toString()
        appointment_time_slot = self.appointment_time_slot_widget.time().toString("HH:mm")
        patient_firstname = self.patient_firstname_input.text()
        patient_lastname = self.patient_lastname_input.text()
        doctor_firstname = self.doctor_firstname_input.text()
        doctor_lastname = self.doctor_lastname_input.text()
        assistant_firstname = self.assistant_firstname_input.text()
        assistant_lastname = self.assistant_lastname_input.text()
        created_at_date = self.created_at_date_filter_selection.custom_date_range_selection_widget.selection_widget.custom_date_calendar.selectedDate().toString()
        updated_at_date = self.updated_at_date_filter_selection.custom_date_range_selection_widget.selection_widget.custom_date_calendar.selectedDate().toString()

        preferences = {
            "service_name": {
                "enabled": False,
                "service_name_value": "",
            },
            "national_id_number": {
                "enabled": False,
                "national_id_number_value": "",
            },
            "appointment_status": {
                "enabled": False,
                "appointment_status_value": "",
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
            "doctor": {
                "enabled": False,
                "firstname": "",
                "lastname": "",
            },
            "assistant": {
                "enabled": False,
                "firstname": "",
                "lastname": "",
            },
            "re_scheduled_date": {
                "enabled": False,
                "filteration_type": "",
                "preset_filter_id": "",
                "custom_date_value": "",
            },
            "created_at": {
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

        if self.appointment_status_checkbox.isChecked():
            preferences["appointment_status"]["enabled"] = True
            if appointment_status:
                preferences["appointment_status"]["appointment_status_value"] = appointment_status

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

        if self.doctor_checkbox.isChecked():
            preferences["doctor"]["enabled"] = True
            if doctor_firstname or doctor_lastname:
                preferences["doctor"]["firstname"] = doctor_firstname
                preferences["doctor"]["lastname"] = doctor_lastname

        if self.assistant_checkbox.isChecked():
            preferences["assistant"]["enabled"] = True
            if assistant_firstname or assistant_lastname:
                preferences["assistant"]["firstname"] = assistant_firstname
                preferences["assistant"]["lastname"] = assistant_lastname

        if self.created_at_date_filter_selection.check_box.isChecked():
            preferences["created_at"]["enabled"] = True
            present_filter_checked_action = self.created_at_date_filter_selection.preset_date_filter_selection_widget.menu.actions_group.checkedAction()
            if present_filter_checked_action:
                preferences["created_at"]["filteration_type"] = "preset_filter"
                preset_filter_data = present_filter_checked_action.data()
                preferences["created_at"]["preset_filter_id"] = preset_filter_data["id"]
            else:
                preferences["created_at"]["filteration_type"] = "custom_filter"
                preferences["created_at"]["custom_date_value"] = created_at_date
        if self.updated_at_date_filter_selection.check_box.isChecked():
            preferences["updated_at"]["enabled"] = True
            present_filter_checked_action = self.updated_at_date_filter_selection.preset_date_filter_selection_widget.menu.actions_group.checkedAction()
            if present_filter_checked_action:
                preferences["updated_at"]["filteration_type"] = "preset_filter"
                preset_filter_data = present_filter_checked_action.data()
                preferences["updated_at"]["preset_filter_id"] = preset_filter_data["id"]
            else:
                preferences["updated_at"]["filteration_type"] = "custom_filter"
                preferences["updated_at"]["custom_date_value"] = updated_at_date

        self.appointment_controller.store.set_filter_preferences(preferences)
        self.signals.refreshAppointmentsTableSignal.emit()
        self.signals.globalLoadingNotificationControllerSignal.emit("APPLY_APPOINTMENT_FILTER")
        self.close_menu()
