import asyncio
from datetime import datetime

from PyQt6.QtCore import Qt, pyqtSlot, QDate, QTime
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QMessageBox, QStackedWidget
from qasync import asyncSlot

from loggers.logger_configs import set_up_logger
from services.supabase.controllers.settings.log_controller import LogController

from services.supabase.controllers.settings.user_auth_controller import UserAuthController
from signals import SignalRepositorySingleton
from views.appointement.appointment_view_dialog import AppointmentViewDialog
from views.appointement.table.table_header_filteration import TableHeaderFiltration
from views.appointement.table.table_layout import TableLayout
from views.appointement.upadate_appointment_additional_data import UpdateAppointmentAdditionalDataDialog
from views.appointement.update_appointment_status_dialog import UpdateAppointmentStatusDialog
from views.appointement.re_schedule_appointment_dialog import RescheduleAppointmentDialog
from views.patient.patients_management_view.patient_dialog import PatientDialog
from views.report.reports_management.report_dialog import ReportDialog

logger = set_up_logger('main.views.appointment.appointments_management_view')


class AppointmentManagementView(QWidget):

    def __init__(self, data, appointment_controller, appointment_types_controller, appointment_status_controller,
                 service_controller, parent=None):
        super().__init__(parent)

        self.re_schedule_appointment_dialog_view = None
        self.parent = parent

        # Table Data types
        self.data = data
        self.all_data_tab = data
        self.upcoming_data_tab = self.parent.upcoming_data
        self.canceled_data_tab = {}
        self.expired_data_tab = {}
        self.search_filter_tab_data = {}

        self.edit_appointment_additional_data_dialog_view = None
        self.edit_appointment_status_dialog_view = None
        self.appointment_information_widget = None
        self.setStyleSheet("background-color:white;")
        self.tab_buttons = None

        self.is_search_enabled = False
        self.is_filter_enabled = False

        self.central_widget = None
        self.table_view = None
        self.table_header_filtration = None
        self.appointment_view_dialog = None
        self.filter_widget = None

        self.error_message = "An unexpected error occurred"

        self.stacked_content_widget = QStackedWidget()

        # Signals
        self.signals = SignalRepositorySingleton.instance()
        self.signals.globalAppointmentUpComingSessionCardClickedSignal.connect(self.set_current_appointment_id)

        # API model
        self.appointment_controller = appointment_controller
        self.appointment_types_controller = appointment_types_controller
        self.appointment_status_controller = appointment_status_controller
        self.service_controller = service_controller

        self.log_controller = LogController()
        self.user_auth_controller = UserAuthController()
        self.auth_user = self.user_auth_controller.user_auth_store.get_user()

        # Loading animation layout
        self.main_h_layout = QHBoxLayout()
        self.main_h_layout.setContentsMargins(0, 0, 0, 0)
        self.main_h_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.main_h_layout.addWidget(self.stacked_content_widget)

        # Set Layouts
        self.setLayout(self.main_h_layout)

        asyncio.create_task(self.setup_table_ui())

    async def setup_table_ui(self):
        self.table_view = TableLayout(data_controller=self.appointment_controller,
                                      data_columns=[
                                          "appointment_id",
                                          "patient_first_name",
                                          "patient_last_name",
                                          "appointment_date",
                                          "appointment_time",
                                          "appointment_status",
                                          "service_name",
                                          "doctor_name",
                                          "created_at",
                                      ], column_display_names=
                                      {
                                          "id": "ID",
                                          "patient_first_name": "First Name",
                                          "patient_last_name": "Last Name",
                                          "appointment_date": "Date",
                                          "appointment_time": "Time",
                                          "appointment_status": "Status",
                                          "service_name": "Service",
                                          "doctor_name": "Doctor",
                                          "created_at": "Created at",
                                      },
                                      parent=self)

        self.table_header_filtration = TableHeaderFiltration(appointments_controller=self.appointment_controller,
                                                             appointment_statuses_controller=self.appointment_status_controller,
                                                             service_controller=self.service_controller,
                                                             parent=self)

        self.signals.refreshAppointmentsTableSignal.connect(self.refresh_table)

        self.table_view.update_table_view()

        self.central_widget = QWidget()

        table_content_v_layout = QVBoxLayout()
        self.central_widget.setLayout(table_content_v_layout)
        table_content_v_layout.setContentsMargins(0, 0, 0, 0)
        table_content_v_layout.setSpacing(0)

        table_header_with_table_layout = QVBoxLayout()
        table_header_with_table_layout.setContentsMargins(0, 10, 0, 0)
        table_header_with_table_layout.setSpacing(0)

        table_header_with_table_layout.addWidget(self.table_header_filtration)
        table_header_with_table_layout.addWidget(self.table_view)

        table_content_v_layout.addLayout(table_header_with_table_layout)

        self.table_view.viewSignal.connect(self.view_appointment)
        self.table_view.editStatusSignal.connect(self.edit_appointment_status)
        self.table_view.editAdditionalDataSignal.connect(self.edit_appointment_additional_data)
        self.table_view.re_scheduleAppointmentSignal.connect(self.re_schedule_appointment)
        self.table_view.cancelAppointmentSignal.connect(self.cancel_appointment)
        self.table_view.makeReportSignal.connect(self.show_report_dialog)

        self.set_main_content(self.central_widget)

    def set_main_content(self, content_widget):
        self.stacked_content_widget.addWidget(content_widget)
        self.stacked_content_widget.setCurrentWidget(content_widget)

    @pyqtSlot()
    @asyncSlot()
    async def refresh_table(self):
        await self.appointment_controller.get_items(page_number=1, item_per_page=15)
        self.signals.globalAppointmentUpdateTableViewSignal.emit()

    @pyqtSlot()
    @asyncSlot()
    async def view_appointment(self):
        self.signals.globalCreateLoadingNotificationSignal.emit("VIEW_APPOINTMENT")
        data = await self.appointment_controller.get_appointment_by_id(self.table_view.get_current_id())
        if not data:
            self.signals.globalCreateMessageNotificationSignal.emit({
                "message_type": "error",
                "message": self.error_message,
                "duration": 2000,
            })
            self.signals.globalLoadingNotificationControllerSignal.emit("VIEW_APPOINTMENT")
        else:
            self.appointment_view_dialog = AppointmentViewDialog(parent=self)
            self.appointment_information_widget = self.appointment_view_dialog.form_widget

            # Patient Info.
            self.appointment_information_widget.patient_national_id_number_input.line_edit.setText(
                data["patient_national_id_number"])
            self.appointment_information_widget.patient_first_name_input.setText(data["patient_first_name"])
            self.appointment_information_widget.patient_lastname_input.setText(data["patient_last_name"])

            # Doctor Info.
            self.appointment_information_widget.doctor_input.setText(data["doctor_name"])

            # Appointment Info
            self.appointment_information_widget.service_input.setText(data["service_name"])
            self.appointment_information_widget.date_input.line_edit.setText(
                datetime.fromisoformat(data["appointment_date"]).strftime("%a, %B %d, %Y"))
            self.appointment_information_widget.time_input.line_edit.setText(data["appointment_time"])

            self.appointment_information_widget.cost_input.line_edit.setText(str(data["doctor_service_cost"]))
            self.appointment_information_widget.duration_input.setText(str(data["doctor_service_duration"]))

            self.appointment_information_widget.check_in_input.line_edit.setText(data["check_in_time"])
            self.appointment_information_widget.check_out_input.line_edit.setText(data["check_out_time"])

            self.appointment_information_widget.appointment_status_input.setText(data["appointment_status"])
            self.appointment_information_widget.appointment_type_input.setText(data["appointment_type"])

            if data["appointment_status"] == "re-scheduled":
                self.appointment_information_widget.re_scheduled_date_input.line_edit.setText(data["re_scheduled_date"])
                self.appointment_information_widget.re_scheduled_time_input.line_edit.setText(data["re_scheduled_time"])
                self.appointment_information_widget.toggle_reschedule_show_hide_status(True)

            elif data["appointment_status"] == "canceled":
                self.appointment_information_widget.cancellation_date_input.line_edit.setText(data["cancellation_date"])
                self.appointment_information_widget.cancellation_time_input.line_edit.setText(data["cancellation_time"])

                self.appointment_information_widget.toggle_cancelled_show_hide_status(True)

            self.appointment_information_widget.reason_of_visit_input.setText(data["reason_for_visit"])
            self.appointment_information_widget.notes_input.setText(data["notes"])

            self.appointment_information_widget.payment_status_input.setText(data["payment_status"])

            created_at = datetime.fromisoformat(data["created_at"]).strftime("%a, %B %d, %Y, %H:%M")
            self.appointment_information_widget.created_at_input.line_edit.setText(created_at)

            if data["updated_at"]:
                updated_at = datetime.fromisoformat(data["updated_at"]).strftime("%a, %B %d, %Y, %H:%M")
                self.appointment_information_widget.updated_at_input.line_edit.setText(updated_at)

            self.signals.globalLoadingNotificationControllerSignal.emit("VIEW_APPOINTMENT")
            self.appointment_view_dialog.show()

    @pyqtSlot()
    def show_add_patient_dialog(self):
        add_patient_dialog_view = PatientDialog("add_patient", parent=self)
        add_patient_dialog_view.update_btn.hide()
        add_patient_dialog_view.show()

    @pyqtSlot()
    @asyncSlot()
    async def re_schedule_appointment(self):
        self.signals.globalCreateLoadingNotificationSignal.emit("VIEW_APPOINTMENT")
        data = await self.appointment_controller.get_appointment_by_id(self.table_view.get_current_id())

        if not data:
            self.signals.globalCreateMessageNotificationSignal.emit({
                "message_type": "error",
                "message": self.error_message,
                "duration": 2000,
            })
            self.signals.globalLoadingNotificationControllerSignal.emit("VIEW_APPOINTMENT")
        else:
            data.update({"appointment_id": self.table_view.get_current_id(),
                         "patient_id": data["patient_id"],
                         "re_scheduled_date": data["appointment_date"],
                         "re_scheduled_time": data["appointment_time"]})
            self.re_schedule_appointment_dialog_view = RescheduleAppointmentDialog(fetched_data=data,
                                                                                   appointment_controller=self.appointment_controller,
                                                                                   appointment_types_controller=self.appointment_types_controller,
                                                                                   service_controller=self.service_controller,
                                                                                   parent=self)

            await self.re_schedule_appointment_dialog_view.appointment_details_form.populate_services()

            self.re_schedule_appointment_dialog_view.appointment_details_form.service_selection_combo.setCurrentText(
                data["service_name"])
            self.re_schedule_appointment_dialog_view.appointment_details_form.available_doctors_combo.setCurrentText(
                data["doctor_name"])
            self.re_schedule_appointment_dialog_view.appointment_details_form.calendar_selection_widget.setSelectedDate(
                QDate.fromString(data["appointment_date"], 'yyyy-MM-dd'))
            self.signals.globalLoadingNotificationControllerSignal.emit("VIEW_APPOINTMENT")
            self.re_schedule_appointment_dialog_view.show()

    @pyqtSlot()
    @asyncSlot()
    async def edit_appointment_status(self):
        self.signals.globalCreateLoadingNotificationSignal.emit("VIEW_APPOINTMENT_STATUS")
        data = await self.appointment_controller.get_appointment_status_by_id(self.table_view.get_current_id())

        if not data:
            self.signals.globalCreateMessageNotificationSignal.emit({
                "message_type": "error",
                "message": self.error_message,
                "duration": 2000,
            })
            self.signals.globalLoadingNotificationControllerSignal.emit("VIEW_APPOINTMENT_STATUS")
        else:

            self.edit_appointment_status_dialog_view = UpdateAppointmentStatusDialog(
                controller=self.appointment_controller, appointment_id=self.table_view.get_current_id(), parent=self)

            await self.edit_appointment_status_dialog_view.populate_statuses()

            self.edit_appointment_status_dialog_view.appointment_status_combo.setCurrentText("ready-to-invoice")

            self.signals.globalLoadingNotificationControllerSignal.emit("VIEW_APPOINTMENT_STATUS")
            self.edit_appointment_status_dialog_view.show()

    @pyqtSlot()
    @asyncSlot()
    async def edit_appointment_additional_data(self):
        self.signals.globalCreateLoadingNotificationSignal.emit("VIEW_APPOINTMENT_ADDITIONAL_DATA")
        data = await self.appointment_controller.get_appointment_additional_data_by_id(self.table_view.get_current_id())

        if not data:
            self.signals.globalCreateMessageNotificationSignal.emit({
                "message_type": "error",
                "message": self.error_message,
                "duration": 2000,
            })
            self.signals.globalLoadingNotificationControllerSignal.emit("VIEW_APPOINTMENT_ADDITIONAL_DATA")
        else:
            self.edit_appointment_additional_data_dialog_view = UpdateAppointmentAdditionalDataDialog(
                appointment_controller=self.appointment_controller,
                appointment_types_controller=self.appointment_types_controller,
                parent=self)

            await self.edit_appointment_additional_data_dialog_view.populate_appointment_types()

            self.edit_appointment_additional_data_dialog_view.appointment_type_combo.setCurrentText(
                data["appointment_type"])

            self.edit_appointment_additional_data_dialog_view.check_in_input.setTime(
                QTime.fromString(data["check_in_time"]))

            self.edit_appointment_additional_data_dialog_view.check_out_input.setTime(
                QTime.fromString(data["check_out_time"]))

            self.edit_appointment_additional_data_dialog_view.reason_for_visit_input.setText(data["reason_for_visit"])
            self.edit_appointment_additional_data_dialog_view.notes_input.setText(data["notes"])

            self.signals.globalLoadingNotificationControllerSignal.emit("VIEW_APPOINTMENT_ADDITIONAL_DATA")
            self.edit_appointment_additional_data_dialog_view.show()

    @pyqtSlot()
    @asyncSlot()
    async def cancel_appointment(self):
        msg = QMessageBox()
        msg.setText('Are you sure you want to cancel?')
        msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        reply = msg.exec()

        if reply == QMessageBox.StandardButton.Ok:
            self.signals.globalCreateLoadingNotificationSignal.emit("CANCEL_APPOINTMENT")
            appointment_data = await self.appointment_controller.get_appointment_by_id(self.table_view.get_current_id())
            if not appointment_data:
                self.signals.globalCreateMessageNotificationSignal.emit({
                    "message_type": "error",
                    "message": self.error_message,
                    "duration": 2000,
                })
                self.signals.globalLoadingNotificationControllerSignal.emit("CANCEL_APPOINTMENT")
            else:
                cancellation_date = datetime.now().strftime("%a, %B %d, %Y")
                cancellation_time = datetime.now().time().strftime("%H:%M:00")

                cancellation_data = {
                    "cancellation_date": cancellation_date,
                    "cancellation_time": cancellation_time,
                    "appointment_status": "canceled",
                    "updated_at": datetime.now().isoformat()
                }
                res = await self.appointment_controller.update_appointment(self.table_view.get_current_id(),
                                                                           data=cancellation_data,
                                                                           patient_data=appointment_data)
                if not res:
                    self.signals.globalCreateMessageNotificationSignal.emit({
                        "message_type": "error",
                        "message": "Error while cancelling appointment",
                        "duration": 5000,
                    })
                    self.signals.globalLoadingNotificationControllerSignal.emit("CANCEL_APPOINTMENT")
                else:
                    await self.refresh_table()
                self.signals.globalLoadingNotificationControllerSignal.emit("CANCEL_APPOINTMENT")

    @pyqtSlot(int)
    def set_current_appointment_id(self, appointment_id):
        self.table_view.set_current_id(appointment_id)
        self.view_appointment()

    @pyqtSlot()
    @asyncSlot()
    async def show_report_dialog(self):
        self.signals.globalCreateLoadingNotificationSignal.emit("GET_APPOINTMENT")

        patient_appointment_data = await self.appointment_controller.get_appointment_by_id(self.table_view.get_current_id())
        if not patient_appointment_data:
            self.signals.globalLoadingNotificationControllerSignal.emit("CANCEL_APPOINTMENT")
            self.signals.globalCreateMessageNotificationSignal.emit({
                "message_type": "error",
                "message": "Error while getting appointment data",
                "duration": 2000,
            })
            self.signals.globalLoadingNotificationControllerSignal.emit("CANCEL_APPOINTMENT")
        else:
            report_dialog = ReportDialog(action_type="create", patient_appointment_data=patient_appointment_data, parent=self)
            self.signals.globalLoadingNotificationControllerSignal.emit("GET_APPOINTMENT")
            report_dialog.showMaximized()

