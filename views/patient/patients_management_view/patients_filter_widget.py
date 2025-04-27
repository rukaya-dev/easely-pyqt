from PyQt6.QtCore import Qt, QSize, pyqtSlot
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QButtonGroup, QPushButton
from qasync import asyncSlot

from loggers.logger_configs import set_up_logger
from services.supabase.controllers.patient.patient_controller import PatientController
from signals import SignalRepositorySingleton
from utils.validator import AgeIntValidator
from views.componenets.customsComponents.buttons.clear_button import CleatButton
from views.componenets.customsComponents.custom_checkbox import CustomCheckBox
from views.componenets.customsComponents.menus.drop_down_menu_component import CustomDropDownMenuComponent
from views.componenets.customsComponents.table.form_componenets.custom_input import CustomLineEdit
from views.componenets.customsComponents.table.save_and_cancel_buttons import SaveAndCancelButtonsWithLoader
from views.componenets.customsComponents.menus.date_filter_widget_with_checkbox import \
    DateFilterWidgetWithCheckBox

logger = set_up_logger('main.views.patient.patients_management_view.patient_filter_widget')


class FilterWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.parent = parent
        self.currently_selected_gender = "Male"

        # Signals
        self.signals = SignalRepositorySingleton.instance()

        # API model
        self.patient_controller = PatientController()

        self.gender_buttons = []

        self.filter_drop_down_widget = QWidget()
        self.filter_drop_down_widget.setFixedWidth(450)
        self.filter_drop_down_widget.setStyleSheet("background-color:#f3f4f6;")

        self.filter_drop_down_vertical_layout = QVBoxLayout()
        self.filter_drop_down_widget.setContentsMargins(20, 20, 20, 0)
        self.filter_drop_down_vertical_layout.setSpacing(30)

        self.gender_checkbox = CustomCheckBox(name="Gender", parent=self)

        self.gender_checkbox.stateChanged.connect(self.handle_gender_checkbox_state_changed)

        self.normal_gender_style = "border: 1px solid #DDDDDD;font-size:14px;border-radius:3px;color:#2C2D33;background-color:white;"

        self.male_btn = QPushButton()
        self.male_btn.setText("Male")
        self.male_btn.setObjectName("Male")
        self.male_btn.setFixedSize(QSize(70, 30))
        self.male_btn.setStyleSheet(self.normal_gender_style)

        self.female_btn = QPushButton()
        self.female_btn.setText("Female")
        self.female_btn.setObjectName("Female")
        self.female_btn.setFixedSize(QSize(70, 30))
        self.female_btn.setStyleSheet(self.normal_gender_style)

        self.male_btn.setCheckable(True)
        self.female_btn.setCheckable(True)

        self.gender_buttons.append(self.male_btn)
        self.gender_buttons.append(self.female_btn)

        self.gender_group = QButtonGroup()
        self.gender_group.addButton(self.male_btn)
        self.gender_group.addButton(self.female_btn)

        self.gender_group.buttonToggled.connect(self.change_gender_btns_style)

        gender_buttons_horizontal_layout = QHBoxLayout()
        gender_buttons_horizontal_layout.setContentsMargins(27, 0, 10, 10)
        gender_buttons_horizontal_layout.setSpacing(10)
        gender_buttons_horizontal_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        gender_buttons_horizontal_layout.addWidget(self.male_btn)
        gender_buttons_horizontal_layout.addWidget(self.female_btn)

        gender_selection_layout = QVBoxLayout()
        gender_selection_layout.setContentsMargins(0, 0, 0, 0)
        gender_selection_layout.setSpacing(10)
        gender_selection_layout.addWidget(self.gender_checkbox)
        gender_selection_layout.addLayout(gender_buttons_horizontal_layout)

        self.age_checkbox = CustomCheckBox(name="Age", parent=self)
        self.age_checkbox.stateChanged.connect(self.handle_age_checkbox_state_changed)

        self.age_input = CustomLineEdit(placeholder_text="23 Yrs", parent=self)
        self.age_input.setFixedHeight(30)
        self.age_input.setDisabled(True)

        self.int_validator = AgeIntValidator()
        self.age_input.setValidator(self.int_validator)

        age_vertical_layout = QVBoxLayout()
        age_vertical_layout.setContentsMargins(27, 0, 10, 10)
        age_vertical_layout.setSpacing(20)

        age_vertical_layout.addWidget(self.age_checkbox)
        age_vertical_layout.addWidget(self.age_input, Qt.AlignmentFlag.AlignRight)

        gender_age_layout = QHBoxLayout()
        gender_age_layout.setContentsMargins(0, 0, 0, 0)
        gender_selection_layout.setSpacing(20)
        gender_age_layout.addLayout(gender_selection_layout)
        gender_age_layout.addLayout(age_vertical_layout)

        self.created_at_date_filter_selection = DateFilterWidgetWithCheckBox("Created at")
        self.updated_at_date_filter_selection = DateFilterWidgetWithCheckBox("Updated at")

        dates_layout = QVBoxLayout()
        dates_layout.setContentsMargins(0, 0, 0, 0)
        dates_layout.addWidget(self.created_at_date_filter_selection)
        dates_layout.addWidget(self.updated_at_date_filter_selection)

        self.save_and_cancel_buttons_widget = SaveAndCancelButtonsWithLoader(text="Save")

        self.save_and_cancel_buttons_widget.setFixedSize(QSize(200, 60))
        self.save_and_cancel_buttons_widget.save_btn.clicked.connect(self.apply_filter)

        self.clear_button = CleatButton()
        self.clear_button.button.clicked.connect(self.clear_filter)

        controls_layout = QHBoxLayout()
        controls_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.addWidget(self.clear_button, 0, Qt.AlignmentFlag.AlignLeft)
        controls_layout.addWidget(self.save_and_cancel_buttons_widget, 1, Qt.AlignmentFlag.AlignRight)

        self.filter_drop_down_vertical_layout.addLayout(gender_age_layout)
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

    def set_currently_selected_gender(self, gender):
        self.currently_selected_gender = gender

    def change_gender_btns_style(self, button):
        if self.gender_checkbox.isChecked():
            button.setStyleSheet(
                "font-size:14px;border-radius:3px;border:1px solid #0DBAB5;color:white;background-color:#2563EB;")

            self.currently_selected_gender = button.objectName()

            for btn in self.gender_group.buttons():
                if btn != button:
                    btn.setStyleSheet(
                        "border:1px solid #DDDDDD;font-size:14px;border-radius:3px;color:#2C2D33;background-color:white;")

    @pyqtSlot(int)
    def handle_gender_checkbox_state_changed(self, state):
        if state == 2:
            self.male_btn.setCheckable(True)
            self.female_btn.setCheckable(True)
            for btn in self.gender_group.buttons():
                btn.setStyleSheet(
                    "border: 1px solid #8D8D8D;font-size:14px;border-radius:3px;color:#2C2D33;background-color:white;")
            self.change_gender_btns_style(self.male_btn)
        else:
            self.male_btn.setCheckable(False)
            self.female_btn.setCheckable(False)
            for btn in self.gender_group.buttons():
                btn.setStyleSheet(self.normal_gender_style)
                btn.setChecked(False)
                self.currently_selected_gender = "Male"

    @pyqtSlot(int)
    def handle_age_checkbox_state_changed(self, state):
        if state == 2:
            self.age_input.setDisabled(False)
        else:
            self.age_input.setDisabled(True)

    @pyqtSlot()
    @asyncSlot()
    async def clear_filter(self):
        self.signals.globalCreateLoadingNotificationSignal.emit("CLEAR_PATIENT_FILTER")
        self.gender_checkbox.setChecked(False)
        self.age_checkbox.setChecked(False)
        self.created_at_date_filter_selection.check_box.setChecked(False)
        self.updated_at_date_filter_selection.check_box.setChecked(False)
        self.patient_controller.store.set_filter_preferences({})
        await self.parent.refresh_table()
        self.signals.globalLoadingNotificationControllerSignal.emit("CLEAR_PATIENT_FILTER")
        self.custom_drop_down_menu.menu.close()


    @pyqtSlot()
    @asyncSlot()
    async def apply_filter(self):
        self.signals.globalCreateLoadingNotificationSignal.emit("APPLY_PATIENT_FILTER")

        created_at_date = self.created_at_date_filter_selection.custom_date_range_selection_widget.selection_widget.custom_date_calendar.selectedDate().toString()
        updated_at_date = self.updated_at_date_filter_selection.custom_date_range_selection_widget.selection_widget.custom_date_calendar.selectedDate().toString()

        preferences = {
            "gender": False,
            "age": {
                "enabled": False,
                "age_value": "",
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

        if self.gender_checkbox.isChecked():
            preferences["gender"] = self.currently_selected_gender

        if self.age_checkbox.isChecked():
            preferences["age"]["enabled"] = True
            age_value = self.age_input.text()
            if age_value:
                preferences["age"]["age_value"] = age_value

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
        #
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

        # try:
        self.patient_controller.store.set_filter_preferences(preferences)
        self.parent.data = await self.patient_controller.get_items()
        self.parent.fetch_and_update_table_view()
        self.signals.globalLoadingNotificationControllerSignal.emit("APPLY_PATIENT_FILTER")
        self.custom_drop_down_menu.menu.close()
