from PyQt6 import QtCore
from PyQt6.QtCore import Qt, QSize, pyqtSlot
from PyQt6.QtGui import QIcon, QPixmap, QStandardItem
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton
from qasync import asyncSlot

from services.supabase.controllers.staff.assistant.assistant_controller import AssistantController
from views.componenets.customsComponents.menus.date_filter_widget_with_checkbox import \
    DateFilterWidgetWithCheckBox
from loggers.logger_configs import set_up_logger
from signals import SignalRepositorySingleton
from views.componenets.customsComponents.buttons.clear_button import CleatButton
from views.componenets.customsComponents.menus.drop_down_menu_component import CustomDropDownMenuComponent
from views.componenets.customsComponents.table.save_and_cancel_buttons import SaveAndCancelButtonsWithLoader

logger = set_up_logger('main.views.staff.assistants.assistant_filter_widget')


class FilterWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.service_id = None
        self.parent = parent

        # Signals
        self.signals = SignalRepositorySingleton.instance()

        # API model
        self.assistant_controller = AssistantController()

        self.filter_drop_down_widget = QWidget()
        self.filter_drop_down_widget.setStyleSheet("background-color:#f3f4f6;")

        self.filter_drop_down_vertical_layout = QVBoxLayout()
        self.filter_drop_down_widget.setContentsMargins(20, 20, 20, 0)
        self.filter_drop_down_vertical_layout.setSpacing(30)

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

    @pyqtSlot()
    @asyncSlot()
    async def clear_filter(self):

        self.created_at_date_filter_selection.check_box.setChecked(False)
        self.updated_at_date_filter_selection.check_box.setChecked(False)

        self.assistant_controller.store.set_filter_preferences({})

        self.parent.refresh_table()
        self.close_menu()

    @pyqtSlot()
    @asyncSlot()
    async def apply_filter(self):
        self.save_and_cancel_buttons_widget.save_btn.start()

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

        self.assistant_controller.store.set_filter_preferences(preferences)
        self.parent.refresh_table()
        self.save_and_cancel_buttons_widget.save_btn.stop()
        self.close_menu()
