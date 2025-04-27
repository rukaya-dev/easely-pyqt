from PyQt6.QtCore import Qt, QSize, pyqtSlot, QTimer
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton
from qasync import asyncSlot

from signals import SignalRepositorySingleton
from views.componenets.customsComponents.buttons.clear_button import CleatButton
from views.componenets.customsComponents.custom_checkbox import CustomCheckBox
from views.componenets.customsComponents.menus.date_filter_widget_with_checkbox import DateFilterWidgetWithCheckBox
from views.componenets.customsComponents.menus.drop_down_menu_component import CustomDropDownMenuComponent
from views.componenets.customsComponents.table.form_componenets.custom_input import CustomLineEdit
from views.componenets.customsComponents.table.save_and_cancel_buttons import SaveAndCancelButtonsWithLoader


class FilterWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.parent = parent
        # Signals
        self.signals = SignalRepositorySingleton.instance()

        # API model
        self.trash_controller = self.parent.trash_controller

        self.filter_drop_down_widget = QWidget()
        self.filter_drop_down_widget.setFixedWidth(450)
        self.filter_drop_down_widget.setStyleSheet("background-color:#f3f4f6;")

        self.filter_drop_down_vertical_layout = QVBoxLayout()
        self.filter_drop_down_widget.setContentsMargins(20, 20, 20, 0)
        self.filter_drop_down_vertical_layout.setSpacing(30)

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

        self.deleted_at_filter_selection = DateFilterWidgetWithCheckBox("Deleted at")

        dates_layout = QVBoxLayout()
        dates_layout.setContentsMargins(0, 0, 0, 0)

        dates_layout.addWidget(self.deleted_at_filter_selection)

        self.save_and_cancel_buttons_widget = SaveAndCancelButtonsWithLoader(text="Apply")
        self.save_and_cancel_buttons_widget.save_btn.clicked.connect(self.apply_filter)

        self.save_and_cancel_buttons_widget.setFixedSize(QSize(200, 60))

        self.clear_button = CleatButton()
        self.clear_button.button.clicked.connect(self.clear_filter)

        controls_layout = QHBoxLayout()
        controls_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.addWidget(self.clear_button, 0, Qt.AlignmentFlag.AlignLeft)
        controls_layout.addWidget(self.save_and_cancel_buttons_widget, 1, Qt.AlignmentFlag.AlignRight)

        self.filter_drop_down_vertical_layout.addLayout(patient_national_id_number_layout)
        self.filter_drop_down_vertical_layout.addLayout(patient_layout)
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

    @pyqtSlot(int)
    def handle_patient_national_id_number_checkbox_state_changed(self, state):
        if state == 2:
            self.patient_national_id_number_input.setDisabled(False)
        else:
            self.patient_national_id_number_input.setDisabled(True)

    @pyqtSlot(int)
    def handle_patient_checkbox_state_changed(self, state):
        if state == 2:
            self.patient_firstname_input.setDisabled(False)
            self.patient_lastname_input.setDisabled(False)
        else:
            self.patient_firstname_input.setDisabled(True)
            self.patient_lastname_input.setDisabled(True)

    @pyqtSlot()
    @asyncSlot()
    async def clear_filter(self):
        self.signals.globalCreateLoadingNotificationSignal.emit("CLEAR_PATIENT_TRASH_FILTER")

        self.deleted_at_filter_selection.check_box.setChecked(False)

        self.patient_national_id_number_checkbox.setChecked(False)
        self.patient_national_id_number_input.clear()
        self.handle_patient_national_id_number_checkbox_state_changed(0)

        self.patient_checkbox.setChecked(False)
        self.patient_firstname_input.clear()
        self.patient_lastname_input.clear()
        self.handle_patient_checkbox_state_changed(0)
        self.trash_controller.store.set_filter_preferences({})

        await self.parent.refresh_table()

        self.signals.globalLoadingNotificationControllerSignal.emit("CLEAR_PATIENT_TRASH_FILTER")
        self.custom_drop_down_menu.menu.close()

    @pyqtSlot()
    @asyncSlot()
    async def apply_filter(self):
        self.signals.globalCreateLoadingNotificationSignal.emit("APPLY_PATIENT_TRASH_FILTER")

        deleted_at = self.deleted_at_filter_selection.custom_date_range_selection_widget.selection_widget.custom_date_calendar.selectedDate().toString()
        national_id_number = self.patient_national_id_number_input.text()
        patient_firstname = self.patient_firstname_input.text()
        patient_lastname = self.patient_lastname_input.text()

        preferences = {
            "national_id_number": {
                "enabled": False,
                "national_id_number_value": "",
            },
            "patient": {
                "enabled": False,
                "firstname": "",
                "lastname": "",
            },
            "deleted_at": {
                "enabled": False,
                "filteration_type": "",
                "preset_filter_id": "",
                "custom_date_value": "",
            },
        }

        if self.patient_national_id_number_checkbox.isChecked():
            preferences["national_id_number"]["enabled"] = True
            if national_id_number:
                preferences["national_id_number"]["national_id_number_value"] = national_id_number
        if self.patient_checkbox.isChecked():
            preferences["patient"]["enabled"] = True
            if patient_firstname or patient_lastname:
                preferences["patient"]["firstname"] = patient_firstname
                preferences["patient"]["lastname"] = patient_lastname

        if self.deleted_at_filter_selection.check_box.isChecked():
            preferences["deleted_at"]["enabled"] = True
            present_filter_checked_action = self.deleted_at_filter_selection.preset_date_filter_selection_widget.menu.actions_group.checkedAction()
            if present_filter_checked_action:
                preferences["deleted_at"]["filteration_type"] = "preset_filter"
                preset_filter_data = present_filter_checked_action.data()
                preferences["deleted_at"]["preset_filter_id"] = preset_filter_data["id"]
            else:
                preferences["deleted_at"]["filteration_type"] = "custom_filter"
                preferences["deleted_at"]["custom_date_value"] = deleted_at

        self.trash_controller.store.set_filter_preferences(preferences)
        await self.parent.refresh_table()

        self.signals.globalLoadingNotificationControllerSignal.emit("APPLY_PATIENT_TRASH_FILTER")
        self.custom_drop_down_menu.menu.close()
