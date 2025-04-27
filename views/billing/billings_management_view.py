import asyncio

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QMessageBox, QStackedWidget
from qasync import asyncSlot

from loggers.logger_configs import set_up_logger
from services.supabase.controllers.appointment.apponitment_controller import AppointmentController
from services.supabase.controllers.settings.service_controller import ServiceController
from services.supabase.controllers.billing.billing_controller import BillingController
from services.supabase.controllers.clinic.clinic_controller import ClinicController
from services.supabase.controllers.image.image_controller import ImageController
from signals import SignalRepositorySingleton
from views.billing.billing_dialog import BillingDialog
from views.billing.billing_filter_widget import FilterWidget
from views.billing.invoice_dialog import InvoiceDialog, ViewInvoiceDialog
from views.billing.table.billing_table_layout import BillingTableLayout
from views.componenets.table.mangement.table_header_filtration_component import TableHeaderFiltration

logger = set_up_logger('main.views.billing.billings_management_view')


class BillingsManagementView(QWidget):

    def __init__(self):
        super().__init__()

        self.setStyleSheet("background-color:white;")
        self.tab_buttons = None

        self.is_search_enabled = False
        self.is_filter_enabled = False

        self.central_widget = None
        self.table_view = None
        self.table_header_filtration = None
        self.add_billing_dialog_view = None
        self.billing_view_dialog = None
        self.edit_billing_information_widget = None
        self.edit_billing_dialog_view = None
        self.filter_widget = None
        self.data = []

        self.stacked_content_widget = QStackedWidget()

        # Signals
        self.signals = SignalRepositorySingleton.instance()

        # API model
        self.billing_controller = BillingController()
        self.appointment_controller = AppointmentController()
        self.service_controller = ServiceController()
        self.clinic_controller = ClinicController()
        self.image_controller = ImageController()

        # Loading animation layout
        self.main_h_layout = QHBoxLayout()
        self.main_h_layout.setContentsMargins(0, 0, 0, 0)
        self.main_h_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.main_h_layout.addWidget(self.stacked_content_widget)

        # Set Layouts
        self.setLayout(self.main_h_layout)

        asyncio.create_task(self.get_initial_data())

    async def get_initial_data(self):
        self.signals.globalCreateLoadingNotificationSignal.emit("GET_BILLINGS_INITIAL_DATA")
        self.data = await self.billing_controller.get_items(1, 20)
        await self.populate_services()
        self.setup_table_ui()

        self.signals.globalLoadingNotificationControllerSignal.emit("GET_BILLINGS_INITIAL_DATA")

    def setup_table_ui(self):
        self.table_view = BillingTableLayout(data_controller=self.billing_controller,
                                             data_columns=[
                                                 "billing_id",
                                                 "patient_name",
                                                 "total_amount",
                                                 "coverage_percentage",
                                                 "net_amount",
                                                 "status",
                                                 "payment_method",
                                                 "billing_date"

                                             ], column_display_names=
                                             {
                                                 "billing_id": "ID",
                                                 "patient_name": "Patient",
                                                 "total_amount": "Total Amount",
                                                 "coverage_percentage": "Discount",
                                                 "net_amount": "Net Amount",
                                                 "status": "Status",
                                                 "payment_method": "Payment Method",
                                                 "billing_date": "Billing Date",

                                             },
                                             is_pagination=True, parent=self)

        self.table_view.update_table_view()

        self.filter_widget = FilterWidget(billing_controller=self.billing_controller,
                                          service_controller=self.service_controller,
                                          parent=self)

        self.table_header_filtration = TableHeaderFiltration(add_btn_name="billing",
                                                             controller=self.billing_controller,
                                                             apply_filter=True, page_filter_widget=self.filter_widget,
                                                             apply_search=True,
                                                             search_place_holder="search by payment method,insurance provider and insurance policy number",
                                                             parent=self)
        self.table_header_filtration.add_btn.hide()
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

        self.table_view.viewSignal.connect(self.view_billing)
        self.table_view.deleteSignal.connect(self.delete_billing)
        self.table_view.downloadSignal.connect(self.download_invoice)

        self.set_main_content(self.central_widget)

    def set_main_content(self, content_widget):
        self.stacked_content_widget.addWidget(content_widget)
        self.stacked_content_widget.setCurrentWidget(content_widget)

    def fetch_and_update_table_view(self):
        self.table_view.update_table_view()

    @pyqtSlot()
    @asyncSlot()
    async def refresh_table(self):
        self.data = await self.billing_controller.get_items(self.data["current_page"], 10)
        self.fetch_and_update_table_view()

    @pyqtSlot(str)
    @asyncSlot()
    async def view_billing(self, action):
        current_id = self.table_view.get_current_id()
        if not current_id:
            return

        self.signals.globalCreateLoadingNotificationSignal.emit("VIEW_BILLING")
        data = await self.billing_controller.get_billing_by_id(current_id)

        self.signals.globalLoadingNotificationControllerSignal.emit("VIEW_BILLING")
        if not data:
            self.signals.globalCreateMessageNotificationSignal.emit({
                "message_type": "error",
                "message": "Error while getting billing data.",
                "duration": 2000,
            })
            return

        self.billing_view_dialog = BillingDialog(
            billing_controller=self.billing_controller,
            appointments_controller=self.appointment_controller,
            appointment_id=current_id,
            data=data,
            parent=self
        )
        view_billing_information_widget = self.billing_view_dialog.form_widget

        self.set_insurance_fields(data, view_billing_information_widget)
        self.set_billing_fields(data, view_billing_information_widget)

        if action == "view":
            view_billing_information_widget.toggle_inputs_state(True, action)
        else:
            view_billing_information_widget.toggle_inputs_state(False, action)

        self.billing_view_dialog.show()

    @staticmethod
    def set_insurance_fields(data, widget):
        insurance_provider = data.get("insurance_provider")
        insurance_policy_number = data.get("insurance_policy_number")
        coverage_percentage = data.get("coverage_percentage", 0.0)

        widget.insurance_provider_input.setText(insurance_provider or "")
        widget.toggle_insurance_provider_visibility(bool(insurance_provider))

        widget.insurance_policy_number_input.setText(insurance_policy_number or "")
        widget.toggle_insurance_policy_number_visibility(bool(insurance_policy_number))

        widget.coverage_percentage_input.setText(str(coverage_percentage))

    @staticmethod
    def set_billing_fields(data, widget):
        widget.total_amount_input.setText(str(data["total_amount"]))
        widget.payment_method_combo.setCurrentText(data["payment_method"])
        widget.notes_input.setText(data["notes"])
        widget.notes_input.setReadOnly(True)

        appointment_info_widget = widget.appointment_information_widget
        appointment_info_widget.patient_name_input.setText(data["patient_name"])
        appointment_info_widget.patient_national_id_number_input.line_edit.setText(data["patient_national_id_number"])
        appointment_info_widget.doctor_input.setText(data["doctor_name"])
        appointment_info_widget.service_input.setText(data["service_name"])
        appointment_info_widget.duration_input.setText(str(data["service_duration"]))
        appointment_info_widget.appointment_date_input.line_edit.setText(data["appointment_date"])
        appointment_info_widget.appointment_time_input.line_edit.setText(data["appointment_time"])

    @pyqtSlot()
    @asyncSlot()
    async def download_invoice(self):
        current_id = self.table_view.get_current_id()
        if not current_id:
            return

        self.signals.globalCreateLoadingNotificationSignal.emit("DOWNLOAD_BILLING")
        data = await self.billing_controller.get_billing_by_id(current_id)

        self.signals.globalLoadingNotificationControllerSignal.emit("DOWNLOAD_BILLING")
        if not data:
            self.show_error_message("Error while downloading billing.")
            return

        clinic_data = await self.clinic_controller.get_data()
        if not clinic_data:
            self.show_error_message("Error while downloading billing.")
            return

        if clinic_data.get("logo_image_path"):
            logo_file = await self.image_controller.get_image_from_storage(clinic_data["logo_image_path"])
            if logo_file:
                clinic_data["logo_image_data"] = logo_file

        billing_data = {
            "billing_id": data["billing_id"],
            "appointment_id": data["appointment_id"],
            "patient_id": data["patient_id"],
            "total_amount": data["total_amount"],
            "insurance_provider": data["insurance_provider"],
            "insurance_policy_number": data["insurance_policy_number"],
            "coverage_percentage": data["coverage_percentage"],
            "net_amount": data["net_amount"],
            "status": data["status"],
            "payment_method": data["payment_method"],
            "service_name": data["service_name"],
        }

        patient_data = {
            "patient_firstname": data["patient_name"],
            "patient_lastname": "",
            "patient_address": data["patient_address"],
            "patient_phone_number": data["patient_phone_number"],
        }

        super_data = {**clinic_data, **billing_data, **patient_data}
        invoice_dialog = ViewInvoiceDialog(super_data, parent=self)
        invoice_dialog.show()

    def show_error_message(self, message):
        self.signals.globalCreateMessageNotificationSignal.emit({
            "message_type": "error",
            "message": message,
            "duration": 2000,
        })

    @pyqtSlot()
    @asyncSlot()
    async def delete_billing(self):
        if self.table_view.get_current_id():
            msg = QMessageBox()
            msg.setText('Are you sure you want to delete?')
            msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            reply = msg.exec()

            if reply == QMessageBox.StandardButton.Ok:
                self.signals.globalCreateLoadingNotificationSignal.emit("DELETE_BILLING")
                data = await self.billing_controller.delete_billing(self.table_view.get_current_id())
                if not data:
                    self.signals.globalCreateMessageNotificationSignal.emit({
                        "message_type": "error",
                        "message": "Could not delete billing.",
                        "duration": 3000,
                    })
                    self.signals.globalLoadingNotificationControllerSignal.emit("DELETE_BILLING")
                else:
                    await self.refresh_table()
                    self.signals.globalCreateMessageNotificationSignal.emit({
                        "message_type": "success",
                        "message": "Billing successfully deleted",
                        "duration": 2000,
                    })
                self.signals.globalLoadingNotificationControllerSignal.emit("DELETE_BILLING")

    @asyncSlot()
    async def populate_services(self):
        await self.service_controller.get_all_services()
