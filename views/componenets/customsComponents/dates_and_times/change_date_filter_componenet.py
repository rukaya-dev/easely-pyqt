from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton

from signals import SignalRepositorySingleton
from views.componenets.customsComponents.buttons.clear_button import CleatButton
from views.componenets.customsComponents.menus.date_filter_widget_with_checkbox import DateFilterWidgetWithCheckBox
from views.componenets.customsComponents.menus.drop_down_menu_component import CustomDropDownMenuComponent
from views.componenets.customsComponents.table.save_and_cancel_buttons import SaveAndCancelButtonsWithLoader


class ChangeDateFilterComponent(QWidget):
    def __init__(self, menu_pos="right", parent=None):
        super().__init__(parent)

        self.parent = parent
        # Signals
        self.signals = SignalRepositorySingleton.instance()

        self.filter_drop_down_widget = QWidget()
        self.filter_drop_down_widget.setFixedWidth(450)
        self.filter_drop_down_widget.setStyleSheet("background-color:#f3f4f6;")

        self.filter_drop_down_vertical_layout = QVBoxLayout()
        self.filter_drop_down_widget.setContentsMargins(20, 20, 20, 0)
        self.filter_drop_down_vertical_layout.setSpacing(30)

        self.change_date_filter_selection = DateFilterWidgetWithCheckBox("Change date")

        dates_layout = QVBoxLayout()
        dates_layout.setContentsMargins(0, 0, 0, 0)

        dates_layout.addWidget(self.change_date_filter_selection)

        self.save_and_cancel_buttons_widget = SaveAndCancelButtonsWithLoader(text="Save")

        self.save_and_cancel_buttons_widget.setFixedSize(QSize(200, 60))

        self.clear_button = CleatButton()

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
                                                                 menu_pos=menu_pos,
                                                                 menu_widget=self.filter_drop_down_widget)

        filter_btn_layout = QHBoxLayout(self)
        filter_btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        filter_btn_layout.setContentsMargins(0, 0, 0, 0)
        filter_btn_layout.setSpacing(0)
        filter_btn_layout.addWidget(self.custom_drop_down_menu)

        self.setLayout(filter_btn_layout)
