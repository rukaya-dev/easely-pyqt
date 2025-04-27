import datetime

from PyQt6.QtCore import Qt, pyqtSlot, QSize
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QWidget, QMessageBox
from qasync import asyncSlot

from loggers.logger_configs import set_up_logger
from services.supabase.controllers.settings.service_controller import ServiceController
from services.supabase.controllers.settings.log_controller import LogController
from services.supabase.controllers.settings.user_auth_controller import UserAuthController
from signals import SignalRepositorySingleton
from views.componenets.customsComponents.buttons.button_with_loader import ButtonWithLoader
from views.componenets.customsComponents.custom_scroll_area import CustomScrollArea
from views.componenets.customsComponents.table.save_and_cancel_buttons import SaveAndCancelButtonsWithLoader
from views.settings.services.service_form import ServiceForm

logger = set_up_logger('main.views.settings.services.service_dialog')


class ServiceDialog(QDialog):
    def __init__(self, action_type, parent=None):
        super().__init__(parent)

        self.action_type = action_type
        self.setStyleSheet("background-color:#f3f4f6;")

        self.parent = parent
        self.generated_time_slots = None

        self.service_controller = ServiceController()

        self.log_controller = LogController()
        self.user_auth_controller = UserAuthController()
        self.auth_user = self.user_auth_controller.user_auth_store.get_user()

        # Signals
        self.signals = SignalRepositorySingleton.instance()

        central_widget = QWidget(self)
        central_widget.setObjectName("central_widget")

        main_service_data_vertical_layout = QVBoxLayout()
        main_service_data_vertical_layout.setContentsMargins(0, 0, 0, 0)

        self.form_widget = ServiceForm(parent=self)

        self.save_and_cancel_btns = SaveAndCancelButtonsWithLoader(text="Save")
        self.save_and_cancel_btns.save_btn.clicked.connect(self.add_new_service)
        self.save_and_cancel_btns.cancel_btn.clicked.connect(self.close)

        self.update_btn = ButtonWithLoader("Update", size=QSize(95, 34))
        self.update_btn.clicked.connect(self.update_service)

        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)
        controls_layout.setContentsMargins(20, 20, 20, 20)
        controls_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        controls_layout.addWidget(self.save_and_cancel_btns)
        controls_layout.addWidget(self.update_btn)

        main_service_data_vertical_layout.addWidget(self.form_widget)

        main_vertical_layout = QHBoxLayout()
        main_vertical_layout.setContentsMargins(0, 0, 0, 0)

        main_vertical_layout.addLayout(main_service_data_vertical_layout)

        central_widget.setLayout(main_vertical_layout)

        scroll_area = CustomScrollArea(self)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setWidget(central_widget)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 5, 0)
        layout.addWidget(scroll_area)
        layout.addLayout(controls_layout)

        self.setLayout(layout)

        self.setFixedWidth(500)
        self.setFixedHeight(400)

    def validate_data(self):

        name = self.form_widget.name_input.text()

        if not name or name == " ":
            QMessageBox.warning(self, "Warning", "service name is required.")
            return False

        return True

    @pyqtSlot()
    @asyncSlot()
    async def add_new_service(self):
        if self.validate_data():
            self.save_and_cancel_btns.save_btn.start()
            data = self.get_data()
            is_exist = await self.service_controller.check_if_service_exist(data["name"])
            if is_exist:
                QMessageBox.warning(None, "Warning", f"""Service with name {data["name"]} already exist.""")
                self.save_and_cancel_btns.save_btn.stop()
            else:
                res = await self.service_controller.create_service(data)
                if not res:
                    self.save_and_cancel_btns.save_btn.stop()
                    self.signals.globalCreateMessageNotificationSignal.emit({
                        "message_type": "error",
                        "message": "Unexpected Error occurred",
                        "duration": 2000,
                    })
                else:
                    self.parent.refresh_table()
                    self.save_and_cancel_btns.save_btn.stop()
                    self.close()
                    self.signals.globalCreateMessageNotificationSignal.emit({
                        "message_type": "success",
                        "message": "Service Successfully Added",
                        "duration": 2000,
                    })

    @pyqtSlot()
    @asyncSlot()
    async def update_service(self):
        if self.validate_data():
            data = self.get_data()
            modified_data = {"updated_at": datetime.datetime.now().isoformat()}
            modified_data.update(data)

            self.update_btn.start()
            is_exist = await self.service_controller.check_if_updated_service_exist(self.parent.table_view.get_current_id(),
                                                                                    modified_data["name"])
            if is_exist:
                QMessageBox.warning(None, "Warning", f"""Service with name {modified_data["name"]} already exist.""")
                self.update_btn.stop()
            else:
                data = await self.service_controller.update_service(self.parent.table_view.get_current_id(), modified_data)
                if not data:
                    self.signals.globalCreateMessageNotificationSignal.emit({
                        "message_type": "error",
                        "message": "Unexpected Error occurred",
                        "duration": 2000,
                    })
                    self.update_btn.stop()
                else:
                    self.parent.refresh_table()
                    self.update_btn.stop()
                    self.close()
                    self.signals.globalCreateMessageNotificationSignal.emit({
                        "message_type": "success",
                        "message": "Service Successfully Updated",
                        "duration": 2000,
                    })

    def get_data(self):
        return {
            "name": self.form_widget.name_input.text(),
            "description": self.form_widget.description_input.toPlainText(),
        }
