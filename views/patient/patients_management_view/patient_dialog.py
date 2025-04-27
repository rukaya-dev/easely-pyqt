import datetime
import json

from PyQt6.QtCore import Qt, pyqtSlot, QSize
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QWidget, QMessageBox
from qasync import asyncSlot

from loggers.logger_configs import set_up_logger
from services.supabase.controllers.settings.log_controller import LogController
from services.supabase.controllers.patient.patient_controller import PatientController
from services.supabase.controllers.patient.patient_history_change_logs_controller import \
    PatientHistoryChangeLogsController
from services.supabase.controllers.settings.user_auth_controller import UserAuthController
from signals import SignalRepositorySingleton
from views.componenets.customsComponents.buttons.button_with_loader import ButtonWithLoader
from views.componenets.customsComponents.custom_scroll_area import CustomScrollArea
from views.componenets.customsComponents.table.save_and_cancel_buttons import SaveAndCancelButtonsWithLoader
from views.patient.patients_management_view.patients_form import PatientForm

logger = set_up_logger('main.views.patient.patient_dialog')


class PatientDialog(QDialog):
    def __init__(self, action_type, parent=None):
        super().__init__(parent)

        self.action_type = action_type
        self.setStyleSheet("background-color:#f3f4f6;")

        self.parent = parent
        self.is_patient_data_widget = None

        self.patient_controller = PatientController()
        self.patient_history_log_controller = PatientHistoryChangeLogsController()

        self.log_controller = LogController()
        self.user_auth_controller = UserAuthController()
        self.auth_user = self.user_auth_controller.user_auth_store.get_user()

        # Signals
        self.signals = SignalRepositorySingleton.instance()

        central_widget = QWidget(self)
        central_widget.setObjectName("central_widget")

        main_patient_data_vertical_layout = QVBoxLayout()
        main_patient_data_vertical_layout.setContentsMargins(0, 0, 0, 0)

        self.form_widget = PatientForm(parent=self)

        self.save_and_cancel_btns = SaveAndCancelButtonsWithLoader(text="Save")
        self.save_and_cancel_btns.save_btn.clicked.connect(self.add_new_patient)
        self.save_and_cancel_btns.cancel_btn.clicked.connect(self.close)

        self.update_btn = ButtonWithLoader("Update", size=QSize(95, 34))
        self.update_btn.clicked.connect(self.update_patient)

        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)
        controls_layout.setContentsMargins(20, 20, 20, 20)
        controls_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        controls_layout.addWidget(self.save_and_cancel_btns)
        controls_layout.addWidget(self.update_btn)

        main_patient_data_vertical_layout.addWidget(self.form_widget)

        main_vertical_layout = QHBoxLayout()
        main_vertical_layout.setContentsMargins(20, 20, 40, 20)

        main_vertical_layout.addLayout(main_patient_data_vertical_layout)

        central_widget.setLayout(main_vertical_layout)

        scroll_area = CustomScrollArea(self)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setWidget(central_widget)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 5, 20)
        layout.addWidget(scroll_area)
        layout.addLayout(controls_layout)

        self.setLayout(layout)
        self.setMinimumWidth(750)
        self.setMinimumHeight(600)

    def validate_data(self):
        national_id_number = self.form_widget.national_id_number_input.text()
        first_name = self.form_widget.firstname_input.text()
        last_name = self.form_widget.lastname_input.text()
        patient_age = self.form_widget.age_input.text()
        insurance_provider = self.form_widget.insurance_provider_input.text()
        insurance_policy_number = self.form_widget.insurance_policy_number_input.text()
        coverage_percentage = self.form_widget.coverage_percentage_input.text()

        if not national_id_number or national_id_number == " ":
            QMessageBox.warning(self, "Warning", "Patient National id number is required.")
            return False

        if not first_name or first_name == " ":
            QMessageBox.warning(self, "Warning", "Patient First name is required.")
            return False

        if not last_name or last_name == " ":
            QMessageBox.warning(self, "Warning", "Patient Last name is required.")
            return False

        if not patient_age or patient_age == " ":
            QMessageBox.warning(self, "Warning", "Patient Age is required.")
            return False

        if insurance_provider or insurance_policy_number or coverage_percentage:
            if not insurance_provider:
                QMessageBox.warning(self, "Warning",
                                    "Patient Insurance provider is required if any insurance information is provided.")
                return False
            if not insurance_policy_number:
                QMessageBox.warning(self, "Warning",
                                    "Patient Insurance policy number is required if any insurance information is provided.")
                return False

            if not coverage_percentage:
                QMessageBox.warning(self, "Warning",
                                    "Coverage percentage is required if any insurance information is provided.")
                return False

        return True

    @pyqtSlot()
    @asyncSlot()
    async def add_new_patient(self):
        if self.validate_data():
            data = self.get_data()
            self.save_and_cancel_btns.save_btn.start()

            is_exist = await self.patient_controller.check_if_patient_exist(data["national_id_number"])
            if is_exist:
                self.save_and_cancel_btns.save_btn.stop()
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.setText('This National ID Number already exist.')
                msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg.exec()
            else:
                data = await self.patient_controller.create_patient(data)
                if not data:
                    self.signals.globalCreateMessageNotificationSignal.emit({
                        "message_type": "error",
                        "message": "Could not create new patient",
                        "duration": 2000,
                    })
                    self.save_and_cancel_btns.save_btn.stop()
                else:
                    self.parent.refresh_table()
                    self.save_and_cancel_btns.save_btn.stop()
                    self.close()
                    self.signals.globalCreateMessageNotificationSignal.emit({
                        "message_type": "success",
                        "message": "Successful Added New Patient.",
                        "duration": 5000,
                    })

    @pyqtSlot()
    @asyncSlot()
    async def update_patient(self):
        if self.validate_data():
            data = self.get_data()
            modified_data = {'updated_at': datetime.datetime.now().isoformat()}
            modified_data.update(data)
            self.update_btn.start()

            is_exist = await self.patient_controller.check_if_updated_patient_exist(self.parent.table_view.current_id,
                                                                                    data["national_id_number"])
            if is_exist:
                self.update_btn.stop()
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.setText('This National ID Number already exist.')
                msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg.exec()
            else:
                data = await self.patient_controller.update_patient(
                    self.parent.table_view.current_id,
                    modified_data)
                if not data:
                    self.signals.globalCreateMessageNotificationSignal.emit({
                        "message_type": "error",
                        "message": "An unexpected error occurred",
                        "duration": 2000,
                    })
                    self.update_btn.stop()
                else:
                    # Store the operation in patient history logs
                    patient_history_log_data = {
                        "change_type": 'update',
                        "patient_id": data["patient_id"],
                        "data_before": json.dumps(self.patient_controller.store.get_patient()),
                        "data_after": json.dumps(modified_data),
                        "changed_by": self.auth_user["email"],
                    }
                    history_data = await self.patient_history_log_controller.create_history(patient_history_log_data)
                    if not history_data:
                        self.signals.globalCreateMessageNotificationSignal.emit({
                            "message_type": "error",
                            "message": "An unexpected error occurred",
                            "duration": 2000,
                        })
                        self.update_btn.stop()
                    else:
                        self.parent.refresh_table()
                        self.update_btn.stop()
                        self.close()
                        self.signals.globalCreateMessageNotificationSignal.emit({
                            "message_type": "success",
                            "message": "Successfully updated patient",
                            "duration": 2000,
                        })

    def get_data(self):
        patient_gender = self.form_widget.current_selected_gender

        coverage_percentage = self.form_widget.coverage_percentage_input.text()

        return {
            'national_id_number': self.form_widget.national_id_number_input.text(),
            'first_name': self.form_widget.firstname_input.text(),
            'last_name': self.form_widget.lastname_input.text(),
            'patient_age': self.form_widget.age_input.text(),
            'patient_age_unit': self.form_widget.age_unit_selection.currentText(),
            'patient_gender': patient_gender,
            'patient_address': self.form_widget.address_input.toPlainText(),
            'patient_phone_number': self.form_widget.phone_number_input.text(),
            'patient_clinical_data': self.form_widget.patient_clinical_data_input.toPlainText(),
            'notes': self.form_widget.notes_input.toPlainText(),
            "insurance_provider": self.form_widget.insurance_provider_input.text(),
            "insurance_policy_number": self.form_widget.insurance_policy_number_input.text(),
            "coverage_percentage": 0.0 if not coverage_percentage else coverage_percentage
        }
