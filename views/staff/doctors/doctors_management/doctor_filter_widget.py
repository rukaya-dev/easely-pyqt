from PyQt6 import QtCore
from PyQt6.QtCore import Qt, QSize, pyqtSlot
from PyQt6.QtGui import QIcon, QPixmap, QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton
from qasync import asyncSlot

from services.supabase.controllers.settings.service_controller import ServiceController
from services.supabase.controllers.staff.doctor.doctor_service_relation_controller import \
    DoctorServiceRelationController
from views.componenets.customsComponents.custom_checkbox import CustomCheckBox
from views.componenets.customsComponents.custom_combobox import CustomComboBox
from views.componenets.customsComponents.dates_and_times.custom_time_picker import CustomTimePicker
from views.componenets.customsComponents.menus.date_filter_widget_with_checkbox import \
    DateFilterWidgetWithCheckBox
from loggers.logger_configs import set_up_logger
from services.supabase.controllers.staff.doctor.doctor_controller import DoctorController
from signals import SignalRepositorySingleton
from views.componenets.customsComponents.buttons.clear_button import CleatButton
from views.componenets.customsComponents.menus.drop_down_menu_component import CustomDropDownMenuComponent
from views.componenets.customsComponents.table.save_and_cancel_buttons import SaveAndCancelButtonsWithLoader
from views.settings.services.available_days_widget import AvailableDaysWidget

logger = set_up_logger('main.views.staff.doctors.doctors_management.doctor_filter_widget')


class FilterWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.service_id = None
        self.parent = parent

        # Signals
        self.signals = SignalRepositorySingleton.instance()

        # API model
        self.doctor_controller = DoctorController()
        self.service_controller = ServiceController()
        self.doctor_service_controller = DoctorServiceRelationController()

        self.filter_drop_down_widget = QWidget()
        self.filter_drop_down_widget.setStyleSheet("background-color:#f3f4f6;")

        self.filter_drop_down_vertical_layout = QVBoxLayout()
        self.filter_drop_down_widget.setContentsMargins(20, 20, 20, 0)
        self.filter_drop_down_vertical_layout.setSpacing(30)

        self.service_name_checkbox = CustomCheckBox("Service Name")
        self.service_name_checkbox.stateChanged.connect(self.handle_service_name_checkbox_state_changed)

        self.service_name_model = QStandardItemModel()

        self.service_name_selection_widget = CustomComboBox()
        self.service_name_selection_widget.setModel(self.service_name_model)
        self.service_name_selection_widget.currentIndexChanged.connect(self.on_service_name_index_changed)

        self.populate_services()
        self.handle_service_name_checkbox_state_changed(0)

        service_name_layout = QVBoxLayout()
        service_name_layout.setContentsMargins(0, 0, 0, 0)
        service_name_layout.setSpacing(20)

        service_name_layout.addWidget(self.service_name_checkbox)
        service_name_layout.addWidget(self.service_name_selection_widget)

        self.available_days_check_box = CustomCheckBox(name="Available Days", parent=self)
        self.available_days_check_box.stateChanged.connect(self.handle_available_days_state_changed)

        self.days_widget = AvailableDaysWidget()
        self.handle_available_days_state_changed(0)

        available_days_layout = QVBoxLayout()
        available_days_layout.setContentsMargins(0, 0, 0, 0)
        available_days_layout.setSpacing(20)

        available_days_layout.addWidget(self.available_days_check_box)
        available_days_layout.addWidget(self.days_widget)

        # Start Time Slot
        self.start_time_check_box = CustomCheckBox(name="Start Time Slot", parent=self)
        self.start_time_check_box.stateChanged.connect(self.handle_start_time_checkbox_state_changed)

        self.start_time_slot_widget = CustomTimePicker()
        self.handle_start_time_checkbox_state_changed(0)

        start_time_slot_layout = QVBoxLayout()
        start_time_slot_layout.setContentsMargins(0, 0, 0, 0)
        start_time_slot_layout.setSpacing(20)

        start_time_slot_layout.addWidget(self.start_time_check_box)
        start_time_slot_layout.addWidget(self.start_time_slot_widget)

        # End Time Slot
        self.end_time_check_box = CustomCheckBox(name="End Time Slot", parent=self)
        self.end_time_check_box.stateChanged.connect(self.handle_end_time_checkbox_state_changed)

        self.end_time_slot_widget = CustomTimePicker()
        self.handle_end_time_checkbox_state_changed(0)

        end_time_slot_layout = QVBoxLayout()
        end_time_slot_layout.setContentsMargins(0, 0, 0, 0)
        end_time_slot_layout.setSpacing(20)

        end_time_slot_layout.addWidget(self.end_time_check_box)
        end_time_slot_layout.addWidget(self.end_time_slot_widget)

        self.time_slot_check_box = CustomCheckBox(name="Time Slot", parent=self)
        self.time_slot_check_box.stateChanged.connect(self.handle_time_checkbox_state_changed)

        self.time_slot_widget = CustomTimePicker()
        self.handle_time_checkbox_state_changed(0)

        time_slot_layout = QVBoxLayout()
        time_slot_layout.setContentsMargins(0, 0, 0, 0)
        time_slot_layout.setSpacing(20)

        time_slot_layout.addWidget(self.time_slot_check_box)
        time_slot_layout.addWidget(self.time_slot_widget)

        # Start & End Time Slots Layout
        start_and_end_time_slot_layout = QHBoxLayout()
        start_and_end_time_slot_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        start_and_end_time_slot_layout.setContentsMargins(0, 0, 0, 0)
        start_and_end_time_slot_layout.setSpacing(20)

        start_and_end_time_slot_layout.addLayout(start_time_slot_layout)
        start_and_end_time_slot_layout.addLayout(end_time_slot_layout)
        start_and_end_time_slot_layout.addLayout(time_slot_layout)

        self.created_at_date_filter_selection = DateFilterWidgetWithCheckBox("Created at")
        self.updated_at_date_filter_selection = DateFilterWidgetWithCheckBox("Updated at")

        dates_layout = QVBoxLayout()
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

        self.filter_drop_down_vertical_layout.addLayout(service_name_layout)
        self.filter_drop_down_vertical_layout.addLayout(available_days_layout)
        self.filter_drop_down_vertical_layout.addLayout(start_and_end_time_slot_layout)
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
                                                                 menu_widget=self.filter_drop_down_widget)

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
    def handle_available_days_state_changed(self, state):
        if state == 2:
            for btn in self.days_widget.available_days_buttons:
                btn.setEnabled(True)
        else:
            for btn in self.days_widget.available_days_buttons:
                self.days_widget.change_day_button_style(state, btn)
                btn.setEnabled(False)

    @pyqtSlot(int)
    def handle_start_time_checkbox_state_changed(self, state):
        if state == 2:
            self.start_time_slot_widget.setDisabled(False)
        else:
            self.start_time_slot_widget.setDisabled(True)

    @pyqtSlot(int)
    def handle_end_time_checkbox_state_changed(self, state):
        if state == 2:
            self.end_time_slot_widget.setDisabled(False)
        else:
            self.end_time_slot_widget.setDisabled(True)

    @pyqtSlot(int)
    def handle_time_checkbox_state_changed(self, state):
        if state == 2:
            self.time_slot_widget.setDisabled(False)
        else:
            self.time_slot_widget.setDisabled(True)

    @asyncSlot()
    async def populate_services(self):
        services = await self.service_controller.get_all_services()
        if services:
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

    @pyqtSlot()
    @asyncSlot()
    async def clear_filter(self):
        self.service_name_checkbox.setChecked(False)
        self.handle_service_name_checkbox_state_changed(0)

        self.available_days_check_box.setChecked(False)
        self.handle_available_days_state_changed(0)

        self.start_time_check_box.setChecked(False)
        self.handle_start_time_checkbox_state_changed(0)

        self.end_time_check_box.setChecked(False)
        self.handle_end_time_checkbox_state_changed(0)

        self.time_slot_check_box.setChecked(False)
        self.handle_time_checkbox_state_changed(0)

        self.created_at_date_filter_selection.check_box.setChecked(False)
        self.updated_at_date_filter_selection.check_box.setChecked(False)
        self.doctor_controller.store.set_filter_preferences({})
        self.parent.refresh_table()
        self.close_menu()

    @pyqtSlot()
    @asyncSlot()
    async def apply_filter(self):
        self.save_and_cancel_buttons_widget.save_btn.start()

        service_name = self.service_name_selection_widget.currentText()
        available_days = self.days_widget.available_days_data
        start_time_slot = self.start_time_slot_widget.time().toString("HH:mm")
        end_time_slot = self.end_time_slot_widget.time().toString("HH:mm")
        time_slot = self.time_slot_widget.time().toString("HH:mm")
        created_at_date = self.created_at_date_filter_selection.custom_date_range_selection_widget.selection_widget.custom_date_calendar.selectedDate().toString()
        updated_at_date = self.updated_at_date_filter_selection.custom_date_range_selection_widget.selection_widget.custom_date_calendar.selectedDate().toString()

        preferences = {
            "service_name": {
                "enabled": False,
                "service_name_value": "",
            },
            "available_days": {
                "enabled": False,
                "available_days_set": "",
            },
            "start_time_slot": {
                "enabled": False,
                "time_slot_value": "",
            },
            "end_time_slot": {
                "enabled": False,
                "time_slot_value": "",
            },
            "time_slot": {
                "enabled": False,
                "time_slot_value": "",
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

        if self.service_name_checkbox.isChecked():
            preferences["service_name"]["enabled"] = True
            if service_name:
                preferences["service_name"]["service_name_value"] = service_name

        if self.available_days_check_box.isChecked():
            preferences["available_days"]["enabled"] = True
            if available_days:
                preferences["available_days"]["available_days_set"] = available_days

        if self.start_time_check_box.isChecked():
            preferences["start_time_slot"]["enabled"] = True
            if start_time_slot:
                preferences["start_time_slot"]["time_slot_value"] = start_time_slot

        if self.end_time_check_box.isChecked():
            preferences["end_time_slot"]["enabled"] = True
            if end_time_slot:
                preferences["end_time_slot"]["time_slot_value"] = end_time_slot

        if self.time_slot_check_box.isChecked():
            preferences["time_slot"]["enabled"] = True
            if time_slot:
                preferences["time_slot"]["time_slot_value"] = time_slot

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

        self.doctor_controller.store.set_filter_preferences(preferences)
        self.parent.refresh_table()
        self.save_and_cancel_buttons_widget.save_btn.stop()
        self.close_menu()
