from PyQt6 import QtCore
from PyQt6.QtCore import Qt, QSize, pyqtSlot
from PyQt6.QtGui import QIcon, QPixmap, QStandardItemModel, QStandardItem, QDoubleValidator
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QSizePolicy
from qasync import asyncSlot

from configs.app_config import locale
from utils.validator import normal_input_validator
from views.componenets.customsComponents.custom_checkbox import CustomCheckBox
from views.componenets.customsComponents.custom_combobox import CustomComboBox
from views.componenets.customsComponents.custom_scroll_area import CustomScrollArea

from loggers.logger_configs import set_up_logger
from signals import SignalRepositorySingleton
from views.componenets.customsComponents.buttons.clear_button import CleatButton
from views.componenets.customsComponents.menus.date_filter_widget_with_checkbox import DateFilterWidgetWithCheckBox
from views.componenets.customsComponents.menus.drop_down_menu_component import CustomDropDownMenuComponent
from views.componenets.customsComponents.table.form_componenets.custom_input import CustomLineEdit
from views.componenets.customsComponents.table.save_and_cancel_buttons import SaveAndCancelButtonsWithLoader

logger = set_up_logger('main.views.appointment.appointment_filter_widget')


class FilterWidget(QWidget):
    def __init__(self, categories_controller, option_controller, parent=None):
        super().__init__(parent)

        self.service_id = None
        self.parent = parent

        # Signals
        self.signals = SignalRepositorySingleton.instance()

        # API model
        self.categories_controller = categories_controller
        self.option_controller = option_controller

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

        self.category_checkbox = CustomCheckBox("Category")
        self.category_checkbox.stateChanged.connect(self.handle_category_checkbox_state_changed)

        self.category_model = QStandardItemModel()

        self.category_selection_widget = CustomComboBox()
        self.category_selection_widget.setModel(self.category_model)
        self.category_selection_widget.currentIndexChanged.connect(self.on_category_index_changed)

        self.populate_categories()
        self.handle_category_checkbox_state_changed(0)

        category_layout = QVBoxLayout()
        category_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        category_layout.setContentsMargins(0, 0, 0, 0)
        category_layout.setSpacing(20)

        category_layout.addWidget(self.category_checkbox)
        category_layout.addWidget(self.category_selection_widget)
        # ------------------------------------------------------------------------
        self.option_name_checkbox = CustomCheckBox(name="Option Name", parent=self)

        self.option_name_input = CustomLineEdit(placeholder_text="", parent=self)
        self.option_name_input.setValidator(normal_input_validator)
        self.option_name_checkbox.stateChanged.connect(
            self.handle_option_name_checkbox_state_changed)
        self.handle_option_name_checkbox_state_changed(0)

        option_name_layout = QVBoxLayout()
        option_name_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        option_name_layout.setContentsMargins(0, 0, 0, 0)
        option_name_layout.setSpacing(20)

        option_name_layout.addWidget(self.option_name_checkbox)
        option_name_layout.addWidget(self.option_name_input)
        # ------------------------------------------------------------------------

        self.created_at_date_filter_selection = DateFilterWidgetWithCheckBox("Created At")
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

        self.filter_drop_down_vertical_layout.addLayout(option_name_layout)
        self.filter_drop_down_vertical_layout.addLayout(category_layout)
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
    def on_category_index_changed(self, index):
        item = self.category_model.item(index)
        if item:
            service_id = item.data(QtCore.Qt.ItemDataRole.UserRole)
            self.set_service_id(service_id)

    @pyqtSlot(int)
    def handle_option_name_checkbox_state_changed(self, state):
        if state == 2:
            self.option_name_input.setDisabled(False)
        else:
            self.option_name_input.setDisabled(True)

    def populate_categories(self):
        categories = self.categories_controller.store.get_data()
        if categories:
            for item in categories:
                standard_item = QStandardItem()
                standard_item.setData(item["name"], Qt.ItemDataRole.DisplayRole)
                standard_item.setData(item["category_id"], Qt.ItemDataRole.UserRole)
                self.category_model.appendRow(standard_item)

    @pyqtSlot(int)
    def handle_category_checkbox_state_changed(self, state):
        if state == 2:
            self.category_selection_widget.setEnabled(True)
        else:
            self.category_selection_widget.setEnabled(False)

    @pyqtSlot()
    @asyncSlot()
    async def clear_filter(self):
        self.signals.globalCreateLoadingNotificationSignal.emit("GET_BILLINGS_INITIAL_DATA")
        
        self.category_checkbox.setChecked(False)
        self.handle_category_checkbox_state_changed(0)

        self.option_name_checkbox.setChecked(False)
        self.option_name_input.clear()
        self.handle_option_name_checkbox_state_changed(0)

        self.created_at_date_filter_selection.check_box.setChecked(False)
        self.updated_at_date_filter_selection.check_box.setChecked(False)
        self.option_controller.store.set_filter_preferences({})
        
        await self.parent.refresh_table()
        self.signals.globalLoadingNotificationControllerSignal.emit("GET_BILLINGS_INITIAL_DATA")
        self.close_menu()

    @pyqtSlot()
    @asyncSlot()
    async def apply_filter(self):
        self.save_and_cancel_buttons_widget.save_btn.start()

        option_name = self.option_name_input.text()
        category = self.category_selection_widget.currentText()
        created_at = self.created_at_date_filter_selection.custom_date_range_selection_widget.selection_widget.custom_date_calendar.selectedDate().toString()
        updated_at = self.updated_at_date_filter_selection.custom_date_range_selection_widget.selection_widget.custom_date_calendar.selectedDate().toString()

        preferences = {
            "category": {
                "enabled": False,
                "category_value": "",
            },
            "option_name": {
                "enabled": False,
                "option_name_value": "",
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

        if self.option_name_checkbox.isChecked():
            preferences["option_name"]["enabled"] = True
            if option_name:
                preferences["option_name"]["option_name_value"] = option_name

        if self.category_checkbox.isChecked():
            preferences["category"]["enabled"] = True
            if category:
                preferences["category"]["category_value"] = category

        if self.created_at_date_filter_selection.check_box.isChecked():
            preferences["created_at"]["enabled"] = True
            present_filter_checked_action = self.created_at_date_filter_selection.preset_date_filter_selection_widget.menu.actions_group.checkedAction()
            if present_filter_checked_action:
                preferences["created_at"]["filteration_type"] = "preset_filter"
                preset_filter_data = present_filter_checked_action.data()
                preferences["created_at"]["preset_filter_id"] = preset_filter_data["id"]
            else:
                preferences["created_at"]["filteration_type"] = "custom_filter"
                preferences["created_at"]["custom_date_value"] = created_at
                
        if self.updated_at_date_filter_selection.check_box.isChecked():
            preferences["updated_at"]["enabled"] = True
            present_filter_checked_action = self.updated_at_date_filter_selection.preset_date_filter_selection_widget.menu.actions_group.checkedAction()
            if present_filter_checked_action:
                preferences["updated_at"]["filteration_type"] = "preset_filter"
                preset_filter_data = present_filter_checked_action.data()
                preferences["updated_at"]["preset_filter_id"] = preset_filter_data["id"]
            else:
                preferences["updated_at"]["filteration_type"] = "custom_filter"
                preferences["updated_at"]["custom_date_value"] = updated_at

        self.option_controller.store.set_filter_preferences(preferences)

        await self.parent.refresh_table()
        self.save_and_cancel_buttons_widget.save_btn.stop()
        self.close_menu()
