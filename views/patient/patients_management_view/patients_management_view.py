import asyncio
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QMessageBox, QStackedWidget
from qasync import asyncSlot

from loggers.logger_configs import set_up_logger
from services.supabase.controllers.appointment.appointment_types_controller import AppointmentTypesController
from services.supabase.controllers.appointment.apponitment_controller import AppointmentController
from services.supabase.controllers.settings.service_controller import ServiceController
from services.supabase.controllers.settings.log_controller import LogController
from services.supabase.controllers.patient.patient_history_change_logs_controller import \
    PatientHistoryChangeLogsController
from services.supabase.controllers.patient.patient_trash_controller import PatientTrashController
from services.supabase.controllers.settings.user_auth_controller import UserAuthController
from signals import SignalRepositorySingleton
from services.supabase.controllers.patient.patient_controller import PatientController
from views.appointement.create_appointment_dialog import CreateAppointmentDialog
from views.patient.patients_management_view.patient_dialog import PatientDialog
from views.patient.patients_management_view.patient_view_dialog import PatientViewDialog
from views.patient.patients_management_view.patients_filter_widget import FilterWidget
from views.patient.patients_management_view.table.table_header_filteration import TableHeaderFiltration
from views.patient.patients_management_view.table.table_layout import TableLayout

logger = set_up_logger('main.views.patient.patients_management_view')


class PatientsManagementView(QWidget):

    def __init__(self):
        super().__init__()

        self.setStyleSheet("background-color:white;")
        self.tab_buttons = None

        self.is_search_enabled = False
        self.is_filter_enabled = False

        self.central_widget = None
        self.table_view = None
        self.table_header_filtration = None
        self.add_patient_dialog_view = None
        self.patient_view_history_dialog = None
        self.view_patient_information_widget = None
        self.edit_patient_dialog_view = None
        self.filter_widget = None
        self.data = []

        self.stacked_content_widget = QStackedWidget()

        # Signals
        self.signals = SignalRepositorySingleton.instance()
        self.signals.updatePatientsTableSignal.connect(self.refresh_table)

        # API model
        self.patient_controller = PatientController()
        self.patient_history_controller = PatientHistoryChangeLogsController()
        self.log_controller = LogController()
        self.trash_controller = PatientTrashController()
        self.user_auth_controller = UserAuthController()
        self.appointment_controller = AppointmentController()
        self.patient_controller = PatientController()
        self.appointments_types_controller = AppointmentTypesController()
        self.service_controller = ServiceController()

        # Loading animation layout
        self.main_h_layout = QHBoxLayout()
        self.main_h_layout.setContentsMargins(0, 0, 0, 0)
        self.main_h_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.main_h_layout.addWidget(self.stacked_content_widget)

        # Set Layouts
        self.setLayout(self.main_h_layout)

        asyncio.create_task(self.get_initial_data())

    async def get_initial_data(self):
        self.signals.globalCreateLoadingNotificationSignal.emit("GET_PATIENTS_LIST")
        self.data = await self.patient_controller.get_items(item_per_page=20, page_number=1)

        await self.get_services_data()

        self.setup_table_ui()
        self.signals.globalLoadingNotificationControllerSignal.emit("GET_PATIENTS_LIST")

    async def get_services_data(self):
        if not self.service_controller.store.get_data():
            await self.service_controller.get_all_services()

    def setup_table_ui(self):
        self.table_view = TableLayout(table_name="patients", data_controller=self.patient_controller,
                                      data_columns=[
                                          "patient_id",
                                          "first_name",
                                          "last_name",
                                          "national_id_number",
                                          "patient_age",
                                          "patient_gender",
                                          "patient_address",
                                          "patient_phone_number",
                                          "created_at",
                                      ], column_display_names=
                                      {
                                          "patient_id": "ID",
                                          "first_name": "First Name",
                                          "last_name": "Last Name",
                                          "national_id_number": "National ID Number",
                                          "patient_age": "Age",
                                          "patient_gender": "Gender",
                                          "patient_address": "Address",
                                          "patient_phone_number": "Phone Number",
                                          "created_at": "Created At",
                                      },
                                      is_pagination=True, parent=self)

        self.table_view.update_table_view()

        self.filter_widget = FilterWidget(parent=self)

        self.table_header_filtration = TableHeaderFiltration(add_btn_name="Patient",
                                                             controller=self.patient_controller,
                                                             apply_filter=True, page_filter_widget=self.filter_widget,
                                                             apply_search=True,
                                                             search_place_holder="search by name, national id number",
                                                             parent=self)
        self.central_widget = QWidget()

        table_content_v_layout = QVBoxLayout()
        self.central_widget.setLayout(table_content_v_layout)
        table_content_v_layout.setContentsMargins(0, 0, 0, 0)
        table_content_v_layout.setSpacing(0)

        table_header_with_table_layout = QVBoxLayout()
        table_header_with_table_layout.setContentsMargins(0, 20, 0, 0)
        table_header_with_table_layout.setSpacing(0)

        table_header_with_table_layout.addWidget(self.table_header_filtration)
        table_header_with_table_layout.addWidget(self.table_view)

        table_content_v_layout.addLayout(table_header_with_table_layout)

        self.table_header_filtration.add_btn.clicked.connect(self.show_add_patient_dialog)

        self.table_view.viewSignal.connect(self.view_patient)
        self.table_view.editSignal.connect(self.edit_patient)
        self.table_view.deleteSignal.connect(self.delete_patient)
        self.table_view.addAppointmentSignal.connect(self.add_patient_appointment)

        self.set_main_content(self.central_widget)

    def set_main_content(self, content_widget):
        self.stacked_content_widget.addWidget(content_widget)
        self.stacked_content_widget.setCurrentWidget(content_widget)

    def fetch_and_update_table_view(self):
        self.table_view.update_table_view()

    @pyqtSlot()
    @asyncSlot()
    async def refresh_table(self):
        self.data = await self.patient_controller.get_items(page_number=self.data["current_page"])
        self.fetch_and_update_table_view()

    @pyqtSlot()
    @asyncSlot()
    async def view_patient(self):
        self.signals.globalCreateLoadingNotificationSignal.emit("VIEW_PATIENT")
        data = await self.patient_controller.get_patient_by_id(self.table_view.get_current_id())
        if not data:
            self.signals.globalCreateMessageNotificationSignal.emit({
                "message_type": "error",
                "message": "An unexpected error occurred",
                "duration": 2000,
            })
            self.signals.globalLoadingNotificationControllerSignal.emit("VIEW_PATIENT")
        else:
            self.patient_view_history_dialog = PatientViewDialog(parent=self)
            self.view_patient_information_widget = self.patient_view_history_dialog.form_widget
            # Patient Info.
            self.view_patient_information_widget.national_id_number_input.setText(data["national_id_number"])
            self.view_patient_information_widget.firstname_input.setText(data["first_name"])
            self.view_patient_information_widget.lastname_input.setText(data["last_name"])

            if data["patient_gender"] == "Male":
                self.view_patient_information_widget.change_gender_btns_style(
                    self.view_patient_information_widget.male_btn)
            else:
                self.view_patient_information_widget.change_gender_btns_style(
                    self.view_patient_information_widget.female_btn)

            self.view_patient_information_widget.age_input.setText(str(data["patient_age"]))
            self.view_patient_information_widget.age_unit_selection.setCurrentText(data["patient_age_unit"])
            self.view_patient_information_widget.address_input.setText(data["patient_address"])
            self.view_patient_information_widget.phone_number_input.setText(data["patient_phone_number"])
            self.view_patient_information_widget.insurance_provider_input.setText(data["insurance_provider"])
            self.view_patient_information_widget.insurance_policy_number_input.setText(data["insurance_policy_number"])
            self.view_patient_information_widget.coverage_percentage_input.setText(str(data["coverage_percentage"]))
            self.view_patient_information_widget.patient_clinical_data_input.setText(data["patient_clinical_data"])
            self.view_patient_information_widget.notes_input.setText(data["notes"])

            self.view_patient_information_widget.national_id_number_input.setReadOnly(True)
            self.view_patient_information_widget.firstname_input.setReadOnly(True)
            self.view_patient_information_widget.lastname_input.setReadOnly(True)
            self.view_patient_information_widget.age_input.setReadOnly(True)
            self.view_patient_information_widget.age_unit_selection.setDisabled(True)
            self.view_patient_information_widget.female_btn.setDisabled(True)
            self.view_patient_information_widget.male_btn.setDisabled(True)
            self.view_patient_information_widget.address_input.setReadOnly(True)
            self.view_patient_information_widget.phone_number_input.setReadOnly(True)
            self.view_patient_information_widget.select_clinical_data_combo.setDisabled(True)
            self.view_patient_information_widget.insurance_provider_input.setReadOnly(True)
            self.view_patient_information_widget.insurance_policy_number_input.setReadOnly(True)
            self.view_patient_information_widget.coverage_percentage_input.setReadOnly(True)
            self.view_patient_information_widget.patient_clinical_data_input.setReadOnly(True)

            self.view_patient_information_widget.notes_input.setReadOnly(True)

            # Patient History Data.
            history_data = await self.patient_history_controller.get_items(
                patient_id=self.table_view.get_current_id(),
                page_number=1, item_per_page=10)

            if not history_data:
                self.signals.globalLoadingNotificationControllerSignal.emit("VIEW_PATIENT")

            if history_data["data"]:
                self.patient_view_history_dialog.history_widget.re_render_history_content_widget(history_data["data"])
            else:
                self.patient_view_history_dialog.history_widget.filter_widget.setDisabled(True)
                self.patient_view_history_dialog.history_widget.search_bar.setDisabled(True)

            self.signals.globalLoadingNotificationControllerSignal.emit("VIEW_PATIENT")
            self.patient_view_history_dialog.show()

    @pyqtSlot()
    def show_add_patient_dialog(self):
        add_patient_dialog_view = PatientDialog("add_patient", parent=self)
        add_patient_dialog_view.update_btn.hide()
        add_patient_dialog_view.show()

    @pyqtSlot()
    @asyncSlot()
    async def edit_patient(self):
        self.signals.globalCreateLoadingNotificationSignal.emit("EDIT_PATIENT")
        data = await self.patient_controller.get_patient_by_id(self.table_view.get_current_id())
        if not data:
            self.signals.globalCreateMessageNotificationSignal.emit({
                "message_type": "error",
                "message": "An unexpected error occurred",
                "duration": 2000,
            })
            self.signals.globalLoadingNotificationControllerSignal.emit("EDIT_PATIENT")
        else:
            self.edit_patient_dialog_view = PatientDialog("edit", parent=self)

            self.edit_patient_dialog_view.form_widget.national_id_number_input.setText(data["national_id_number"])
            self.edit_patient_dialog_view.form_widget.firstname_input.setText(data["first_name"])
            self.edit_patient_dialog_view.form_widget.lastname_input.setText(data["last_name"])
            if data["patient_gender"] == "Male":
                self.edit_patient_dialog_view.form_widget.change_gender_btns_style(
                    self.edit_patient_dialog_view.form_widget.male_btn)
            else:
                self.edit_patient_dialog_view.form_widget.change_gender_btns_style(
                    self.edit_patient_dialog_view.form_widget.female_btn)

            self.edit_patient_dialog_view.form_widget.age_input.setText(str(data["patient_age"]))
            self.edit_patient_dialog_view.form_widget.age_unit_selection.setCurrentText(data["patient_age_unit"])
            self.edit_patient_dialog_view.form_widget.address_input.setText(data["patient_address"])
            self.edit_patient_dialog_view.form_widget.phone_number_input.setText(data["patient_phone_number"])
            self.edit_patient_dialog_view.form_widget.patient_clinical_data_input.setText(data["patient_clinical_data"])
            self.edit_patient_dialog_view.form_widget.insurance_provider_input.setText(data["insurance_provider"])
            self.edit_patient_dialog_view.form_widget.insurance_policy_number_input.setText(
                data["insurance_policy_number"])

            if not data["coverage_percentage"]:

                self.edit_patient_dialog_view.form_widget.coverage_percentage_input.setText("")
            else:
                self.edit_patient_dialog_view.form_widget.coverage_percentage_input.setText(
                    str(data["coverage_percentage"]))

            self.edit_patient_dialog_view.form_widget.notes_input.setText(data["notes"])

            self.edit_patient_dialog_view.save_and_cancel_btns.save_btn.hide()

            self.signals.globalLoadingNotificationControllerSignal.emit("EDIT_PATIENT")
            self.edit_patient_dialog_view.show()

    @pyqtSlot()
    @asyncSlot()
    async def delete_patient(self):
        msg = QMessageBox()
        msg.setText('Are you sure you want to delete?')
        msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        reply = msg.exec()

        if reply == QMessageBox.StandardButton.Ok:
            self.signals.globalCreateLoadingNotificationSignal.emit("DELETE_PATIENT")
            res = await self.patient_controller.delete_patient(self.table_view.get_current_id())
            if not res:
                self.signals.globalCreateMessageNotificationSignal.emit({
                    "message_type": "error",
                    "message": "Error while deleting patient.",
                    "duration": 5000,
                })
                self.signals.globalLoadingNotificationControllerSignal.emit("DELETE_PATIENT")
            else:
                self.signals.updatePatientsTrashTableSignal.emit()
                await self.refresh_table()

            self.signals.globalLoadingNotificationControllerSignal.emit("DELETE_PATIENT")

    @pyqtSlot()
    @asyncSlot()
    async def add_patient_appointment(self):
        self.signals.globalCreateLoadingNotificationSignal.emit("RENDER_APPOINTMENT_VIEW")
        appointment_dialog = CreateAppointmentDialog(patient_id=self.table_view.get_current_id(),
                                                     appointment_controller=self.appointment_controller,
                                                     appointment_types_controller=self.appointments_types_controller,
                                                     service_controller=self.service_controller,
                                                     parent=self)

        await appointment_dialog.appointment_details_form.populate_services()
        self.signals.globalLoadingNotificationControllerSignal.emit("RENDER_APPOINTMENT_VIEW")
        appointment_dialog.show()
