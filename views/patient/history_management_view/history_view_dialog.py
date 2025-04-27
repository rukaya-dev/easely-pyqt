from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QWidget

from loggers.logger_configs import set_up_logger
from signals import SignalRepositorySingleton
from views.componenets.customsComponents.buttons.button_with_loader import ButtonWithLoader
from views.componenets.customsComponents.table.save_and_cancel_buttons import SaveAndCancelButtonsWithLoader
from views.patient.history_management_view.log_form import LogForm

logger = set_up_logger('main.views.logs.logs_dialog')


class HistoryViewDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setStyleSheet("background-color:#f3f4f6;")

        self.parent = parent

        # Signals
        self.signals = SignalRepositorySingleton.instance()

        central_widget = QWidget(self)

        main_vertical_layout = QVBoxLayout()
        main_vertical_layout.setContentsMargins(0, 0, 0, 0)

        main_history_data_vertical_layout = QVBoxLayout()
        main_history_data_vertical_layout.setContentsMargins(20, 20, 3, 20)

        self.form_widget = LogForm(parent=self)

        self.save_and_cancel_btns = SaveAndCancelButtonsWithLoader(text="Save")
        self.save_and_cancel_btns.cancel_btn.clicked.connect(self.close)

        self.update_btn = ButtonWithLoader("Update", size=QSize(95, 34))

        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)
        controls_layout.setContentsMargins(20, 20, 20, 20)
        controls_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        controls_layout.addWidget(self.save_and_cancel_btns)
        controls_layout.addWidget(self.update_btn)

        main_history_data_vertical_layout.addWidget(self.form_widget)

        main_vertical_layout.addLayout(main_history_data_vertical_layout)
        main_vertical_layout.addLayout(controls_layout)

        central_widget.setLayout(main_vertical_layout)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.addWidget(central_widget)
        self.setLayout(self.layout)

        self.setMinimumWidth(600)
        self.setMinimumHeight(700)

        self.setModal(True)


