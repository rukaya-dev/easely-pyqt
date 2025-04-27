import datetime

from PyQt6.QtCore import Qt, pyqtSlot, QSize
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QWidget, QMessageBox, QSpacerItem, QSizePolicy
from qasync import asyncSlot

from loggers.logger_configs import set_up_logger
from services.supabase.controllers.settings.log_controller import LogController
from services.supabase.controllers.staff.doctor.doctor_controller import DoctorController
from services.supabase.controllers.settings.user_auth_controller import UserAuthController
from signals import SignalRepositorySingleton
from views.componenets.customsComponents.buttons.button_with_loader import ButtonWithLoader
from views.componenets.customsComponents.custom_scroll_area import CustomScrollArea
from views.componenets.customsComponents.table.save_and_cancel_buttons import SaveAndCancelButtonsWithLoader
from views.staff.doctors.doctors_management.doctor_form import DoctorForm

logger = set_up_logger('main.views.staff.doctors.doctors_management.doctor_dialog')


class DoctorDialog(QDialog):
    def __init__(self, action_type, parent=None):
        super().__init__(parent)

        self.action_type = action_type
        self.setStyleSheet("background-color:#f3f4f6;")

        self.parent = parent
        self.generated_time_slots = None

        self.doctor_controller = DoctorController()

        self.log_controller = LogController()
        self.user_auth_controller = UserAuthController()
        self.auth_user = self.user_auth_controller.user_auth_store.get_user()

        # Signals
        self.signals = SignalRepositorySingleton.instance()

        central_widget = QWidget(self)
        central_widget.setObjectName("central_widget")

        main_doctor_data_vertical_layout = QVBoxLayout()
        main_doctor_data_vertical_layout.setContentsMargins(0, 0, 0, 0)

        self.form_widget = DoctorForm(parent=self)

        self.save_and_cancel_btns = SaveAndCancelButtonsWithLoader(text="Save")
        self.save_and_cancel_btns.save_btn.clicked.connect(self.add_new_doctor)
        self.save_and_cancel_btns.cancel_btn.clicked.connect(self.close)

        self.update_btn = ButtonWithLoader("Update", QSize(82, 34))
        self.update_btn.clicked.connect(self.update_doctor)

        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)
        controls_layout.setContentsMargins(20, 20, 20, 20)
        controls_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        controls_layout.addWidget(self.save_and_cancel_btns)
        controls_layout.addWidget(self.update_btn)

        main_doctor_data_vertical_layout.addWidget(self.form_widget)

        main_vertical_layout = QHBoxLayout()
        main_vertical_layout.setContentsMargins(0, 0, 0, 0)

        spacer = QSpacerItem(10, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        main_vertical_layout.addLayout(main_doctor_data_vertical_layout)
        main_vertical_layout.addSpacerItem(spacer)

        central_widget.setLayout(main_vertical_layout)

        scroll_area = CustomScrollArea(self)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setWidget(central_widget)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 5, 20)
        layout.addWidget(scroll_area)
        layout.addLayout(controls_layout)

        self.setLayout(layout)

        self.setMinimumWidth(800)
        self.setMinimumHeight(600)

    def validate_data(self):

        first_name = self.form_widget.first_name_input.text()
        last_name = self.form_widget.last_name_input.text()

        if not first_name or first_name == " ":
            QMessageBox.warning(self, "Warning", "doctor first name is required.")
            return False

        if not last_name or last_name == " ":
            QMessageBox.warning(self, "Warning", "doctor last name is required.")
            return False

        return True

    @pyqtSlot()
    @asyncSlot()
    async def add_new_doctor(self):
        if self.validate_data():
            self.save_and_cancel_btns.save_btn.start()
            data = self.get_data()

            data = await self.doctor_controller.create_doctor(data)
            if not data:
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
                    "message": "Successfully Added New Doctor.",
                    "duration": 2000,
                })

    @pyqtSlot()
    @asyncSlot()
    async def update_doctor(self):
        if self.validate_data():
            data = self.get_data()

            self.update_btn.start()

            modified_data = {"updated_at": datetime.datetime.now().isoformat()}
            modified_data.update(data)

            data = await self.doctor_controller.update_doctor(self.parent.table_view.get_current_id(), modified_data)
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
                    "message": "Successfully Updated Doctor",
                    "duration": 2000,
                })

    def get_data(self):
        return {
            "first_name": self.form_widget.first_name_input.text(),
            "last_name": self.form_widget.last_name_input.text(),
            "specialty": self.form_widget.specialty_input.text(),
            "qualifications": self.form_widget.qualifications_input.toPlainText(),
            "email": self.form_widget.email_input.text(),
            "phone_number": self.form_widget.phone_number_input.text(),
            "address": self.form_widget.address_input.toPlainText(),
            "room_number": self.form_widget.room_number_input.text(),
        }
    #     {
    #         "first_name": "Rukaya",
    #         "last_name": "Abdul-hussien",
    #         "specialty": "Developer",
    #         "qualifications": "Nothing",
    #         "phone_number": "+000000000000",
    #         "email": "rukaya@bitbyte3.com",
    #         "room_number": "1001",
    #         "start_time": '08:00:00',
    #         "end_time": '17:00:00',
    #         "image_id": None,
    #         "available_days": json.dumps(["Monday", "Wednesday", "Friday"]),
    #         "available_time_slots": json.dumps(["09:00-11:00", "14:00-16:00"])
    #     },
