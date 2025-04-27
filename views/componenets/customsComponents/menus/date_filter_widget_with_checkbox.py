from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout

from views.componenets.customsComponents.custom_checkbox import CustomCheckBox
from views.componenets.customsComponents.menus.custom_date_range_selection_widget import CustomDateFilterSelectionWidget
from views.componenets.customsComponents.menus.date_filter_menu_button import PresetDateFilterSelectionWidget


class DateFilterWidgetWithCheckBox(QWidget):
    def __init__(self, name, parent=None):
        super().__init__(parent)

        self.filter_data = None

        central_widget = QWidget()
        central_widget.setFixedWidth(250)

        self.check_box = CustomCheckBox(name)
        self.check_box.stateChanged.connect(self.handle_checkbox_state_changed)

        self.preset_date_filter_selection_widget = PresetDateFilterSelectionWidget(self)

        self.preset_date_filter_selection_widget.menu.presetFilterActionTriggered.connect(
            self.handle_preset_filter_style)

        self.custom_date_range_selection_widget = CustomDateFilterSelectionWidget(self)
        self.custom_date_range_selection_widget.selection_widget.apply_btn.clicked.connect(
            self.handle_custom_filter_style)

        self.preset_date_filter_selection_widget.setDisabled(True)
        self.custom_date_range_selection_widget.setDisabled(True)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        main_layout.addWidget(self.preset_date_filter_selection_widget)
        main_layout.addWidget(self.custom_date_range_selection_widget)

        central_widget.setLayout(main_layout)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        layout.addWidget(self.check_box)
        layout.addWidget(central_widget)

        self.setLayout(layout)

        self.setFixedWidth(300)

    @pyqtSlot(int)
    def handle_checkbox_state_changed(self, state):
        if state == 2:
            self.preset_date_filter_selection_widget.setDisabled(False)
            self.custom_date_range_selection_widget.setDisabled(False)
        else:
            self.preset_date_filter_selection_widget.setDisabled(True)
            self.custom_date_range_selection_widget.setDisabled(True)

    @pyqtSlot()
    def handle_preset_filter_style(self):

        self.preset_date_filter_selection_widget.preset_date_menu_button.set_active_widget_style()

        self.custom_date_range_selection_widget.custom_date_menu_button.set_de_active_widget_style()

    def handle_custom_filter_style(self):
        self.preset_date_filter_selection_widget.preset_date_menu_button.set_de_active_widget_style()
        if self.preset_date_filter_selection_widget.menu.actions_group.checkedAction():
            self.preset_date_filter_selection_widget.menu.actions_group.checkedAction().setChecked(False)

        self.custom_date_range_selection_widget.custom_date_menu_button.set_active_widget_style()
