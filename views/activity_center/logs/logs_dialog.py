from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QWidget, QSpacerItem, QSizePolicy

from loggers.logger_configs import set_up_logger
from services.supabase.controllers.settings.log_controller import LogController
from signals import SignalRepositorySingleton
from views.componenets.customsComponents.custom_scroll_area import CustomScrollArea
from views.componenets.customsComponents.table.save_and_cancel_buttons import SaveAndCancelButtonsWithLoader
from views.activity_center.logs.logs_form import LogForm

logger = set_up_logger('main.views.logs.logs_dialog')


class LogDialog(QDialog):
    def __init__(self, action_type, parent=None):
        super().__init__(parent)

        self.action_type = action_type
        self.setStyleSheet("background-color:#f3f4f6;")

        self.parent = parent
        self.is_history_data_widget = None

        self.log_controller = LogController()

        # Signals
        self.signals = SignalRepositorySingleton.instance()

        central_widget = QWidget(self)
        central_widget.setObjectName("central_widget")

        main_vertical_layout = QVBoxLayout()
        main_vertical_layout.setContentsMargins(0, 0, 0, 0)

        main_history_data_vertical_layout = QHBoxLayout()
        main_history_data_vertical_layout.setContentsMargins(20, 20, 20, 20)

        self.form_widget = LogForm(parent=self)

        self.save_and_cancel_btns = SaveAndCancelButtonsWithLoader(text="Save")
        self.save_and_cancel_btns.cancel_btn.clicked.connect(self.close)

        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)
        controls_layout.setContentsMargins(20, 20, 20, 20)
        controls_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        controls_layout.addWidget(self.save_and_cancel_btns)

        spacer = QSpacerItem(10, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        main_history_data_vertical_layout.addWidget(self.form_widget)
        main_history_data_vertical_layout.addSpacerItem(spacer)

        main_vertical_layout.addLayout(main_history_data_vertical_layout)
        main_vertical_layout.addLayout(controls_layout)

        central_widget.setLayout(main_vertical_layout)

        scroll_area = CustomScrollArea(self)
        scroll_area.setWidget(central_widget)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 5, 20)
        self.layout.addWidget(scroll_area)
        self.setLayout(self.layout)

        self.setMinimumHeight(700)
