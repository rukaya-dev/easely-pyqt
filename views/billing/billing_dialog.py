import datetime
from PyQt6.QtCore import Qt, QSize, pyqtSlot
from PyQt6.QtGui import QFont, QPixmap, QDoubleValidator
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QMessageBox, QHBoxLayout, QWidget, QLabel
from qasync import asyncSlot

from configs.app_config import locale
from loggers.logger_configs import set_up_logger
from services.supabase.controllers.clinic.clinic_controller import ClinicController
from services.supabase.controllers.image.image_controller import ImageController
from signals import SignalRepositorySingleton
from views.billing.invoice_dialog import InvoiceDialog, ViewInvoiceDialog
from views.componenets.customsComponents.buttons.button_with_loader import ButtonWithLoader
from views.componenets.customsComponents.custom_combobox import CustomComboBox
from views.componenets.customsComponents.custom_line_edit_with_icon import CustomLineEditWithIcon
from views.componenets.customsComponents.custom_rounded_line_edit import CustomRoundedLineEdit
from views.componenets.customsComponents.custom_scroll_area import CustomScrollArea
from views.componenets.customsComponents.loaders.internal_loader import InternalLoader
from views.componenets.customsComponents.table.form_componenets.custom_label import CustomLabel
from views.componenets.customsComponents.table.form_componenets.custom_text_edit import CustomTextEdit
from views.componenets.customsComponents.table.save_and_cancel_buttons import SaveAndCancelButtonsWithLoader
from views.componenets.customsComponents.table.form_componenets.custom_input import CustomLineEdit

logger = set_up_logger('main.views.billing.billing_dialog')


class BillingDialog(QDialog):
    def __init__(self, billing_controller, appointments_controller, data, appointment_id, parent=None):
        super().__init__(parent)

        self.parent = parent
        self.appointment_id = appointment_id
        self.data = data

        self.appointments_controller = appointments_controller
        self.billing_controller = billing_controller
        self.clinic_controller = ClinicController()
        self.image_controller = ImageController()

        self.header = self.BillingHeaderWidget(parent=self)

        self.form_widget = self.FormWidget(parent=self)
        self.form_widget.total_amount_input.textChanged.connect(self.on_text_change)
        self.form_widget.coverage_percentage_input.textChanged.connect(self.on_text_change)

        self.save_and_cancel_btns = SaveAndCancelButtonsWithLoader(text="Finish")
        self.save_and_cancel_btns.save_btn.clicked.connect(self.finish)
        self.save_and_cancel_btns.cancel_btn.clicked.connect(self.close)

        self.finish_and_generate_invoice_btn = ButtonWithLoader("Finish && Generate Invoice", QSize(200, 34))
        finish_and_generate_invoice_btn_policy = self.finish_and_generate_invoice_btn.sizePolicy()
        finish_and_generate_invoice_btn_policy.setRetainSizeWhenHidden(False)

        self.finish_and_generate_invoice_btn.clicked.connect(self.finish_and_make_invoice)

        self.update_billing_btn = ButtonWithLoader("Update", QSize(83, 34))
        finish_and_generate_invoice_btn_policy = self.update_billing_btn.sizePolicy()
        finish_and_generate_invoice_btn_policy.setRetainSizeWhenHidden(False)

        self.update_billing_btn.clicked.connect(self.update_billing)

        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)
        controls_layout.setContentsMargins(20, 20, 20, 20)

        controls_layout.addWidget(self.save_and_cancel_btns, 1, Qt.AlignmentFlag.AlignRight)
        controls_layout.addWidget(self.finish_and_generate_invoice_btn, 0, Qt.AlignmentFlag.AlignRight)
        controls_layout.addWidget(self.update_billing_btn, 0, Qt.AlignmentFlag.AlignRight)

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self.header)
        layout.addWidget(self.form_widget)
        layout.addLayout(controls_layout, Qt.AlignmentFlag.AlignRight)

        self.setLayout(layout)
        self.setFixedWidth(700)
        self.setMaximumHeight(650)

    @pyqtSlot()
    def on_text_change(self):
        self.calculate_net_amount()

    def calculate_net_amount(self):
        total_amount = self.form_widget.total_amount_input.text()
        coverage_percentage = self.form_widget.coverage_percentage_input.text()

        try:
            total_amount = float(total_amount)
            coverage_percentage = float(coverage_percentage)
            net_amount = total_amount - (total_amount * (coverage_percentage / 100))
            self.form_widget.net_amount_input.setText(f"{net_amount:.2f}")
        except ValueError:
            self.form_widget.net_amount_input.setText(str(0))

    @asyncSlot()
    async def finish(self):
        if self.validate_data():
            self.save_and_cancel_btns.save_btn.start()

        billing_data = {
            "appointment_id": self.data["appointment_id"],
            "patient_id": self.data["patient_id"],
            "total_amount": self.form_widget.total_amount_input.text(),
            "insurance_provider": self.form_widget.insurance_provider_input.text(),
            "insurance_policy_number": self.form_widget.insurance_policy_number_input.text(),
            "coverage_percentage": self.form_widget.coverage_percentage_input.text(),
            "net_amount": self.form_widget.net_amount_input.text(),
            "status": "paid",
            "payment_method": self.form_widget.payment_method_combo.currentText(),
            "notes": self.form_widget.notes_input.toPlainText(),

        }
        patient_data = {
            "patient_firstname": self.data["patient_first_name"],
            "patient_lastname": self.data["patient_last_name"],
            "patient_address": self.data["patient_address"],
            "patient_phone_number": self.data["patient_phone_number"],
        }
        res = await self.billing_controller.finish_billing(billing_data=billing_data, patient_data=patient_data)
        if not res:
            self.save_and_cancel_btns.save_btn.stop()
            msg = QMessageBox()
            msg.setText('Error occurred')
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setDetailedText(
                "error occurred while creating billing, please contact your service provider.")
            msg.exec()
        else:
            res = await self.appointments_controller.update_appointment(appointment_id=self.data["appointment_id"],
                                                                        data={"payment_status": "paid",
                                                                              "appointment_status": "invoiced"},
                                                                        patient_data=patient_data)
            if not res:
                self.save_and_cancel_btns.save_btn.stop()
                msg = QMessageBox()
                msg.setText('Error occurred')
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.setDetailedText(
                    "error occurred while creating billing, please contact your service provider.")
                msg.exec()
            else:
                self.save_and_cancel_btns.save_btn.stop()
                self.close()
                msg = QMessageBox()
                msg.setText('Billing Created Successfully.')
                msg.setIcon(QMessageBox.Icon.Information)
                msg.exec()

    @asyncSlot()
    async def finish_and_make_invoice(self):
        if not self.validate_data():
            return

        self.finish_and_generate_invoice_btn.start()
        clinic_data = await self.clinic_controller.get_data()

        if not clinic_data:
            self.finish_and_generate_invoice_btn.stop()
            QMessageBox().critical(None, "Error",
                                   "Error occurred\n\nerror occurred while getting clinic data for invoice, please contact your service provider.")
            return

        if clinic_data.get("logo_image_path"):
            logo_file = await self.image_controller.get_image_from_storage(clinic_data["logo_image_path"])
            if logo_file:
                clinic_data["logo_image_data"] = logo_file

        billing_data = {
            "appointment_id": self.data["appointment_id"],
            "patient_id": self.data["patient_id"],
            "total_amount": self.form_widget.total_amount_input.text(),
            "insurance_provider": self.form_widget.insurance_provider_input.text(),
            "insurance_policy_number": self.form_widget.insurance_policy_number_input.text(),
            "coverage_percentage": self.form_widget.coverage_percentage_input.text(),
            "net_amount": self.form_widget.net_amount_input.text(),
            "status": "paid",
            "payment_method": self.form_widget.payment_method_combo.currentText(),
        }

        patient_data = {
            "patient_firstname": self.data["patient_first_name"],
            "patient_lastname": self.data["patient_last_name"],
            "patient_address": self.data["patient_address"],
            "patient_phone_number": self.data["patient_phone_number"],
        }

        res = await self.billing_controller.finish_billing(billing_data=billing_data, patient_data=patient_data)
        if not res:
            self.finish_and_generate_invoice_btn.stop()
            QMessageBox().critical(None, "Error",
                                   "Error occurred\n\nerror occurred while creating billing, please contact your service provider.")
            return

        billing_data["billing_id"] = res["billing_id"]
        billing_data["service_name"] = self.data["service_name"]
        billing_data["payment_method"] = res["payment_method"]

        res = await self.appointments_controller.update_appointment(
            appointment_id=self.data["appointment_id"],
            data={"payment_status": "paid", "appointment_status": "invoiced"},
            patient_data=patient_data
        )
        if not res:
            self.finish_and_generate_invoice_btn.stop()
            QMessageBox().critical(None, "Error",
                                   "Error occurred\n\nerror occurred while updating appointment status, please contact your service provider.")
            return

        super_data = {**clinic_data, **billing_data, **patient_data}
        self.finish_and_generate_invoice_btn.stop()
        self.close()
        invoice_dialog = ViewInvoiceDialog(super_data, parent=self)
        invoice_dialog.show()

    @asyncSlot()
    async def update_billing(self):
        if self.validate_data():
            self.save_and_cancel_btns.save_btn.start()

        billing_data = {
            "total_amount": self.form_widget.total_amount_input.text(),
            "insurance_provider": self.form_widget.insurance_provider_input.text(),
            "insurance_policy_number": self.form_widget.insurance_policy_number_input.text(),
            "coverage_percentage": self.form_widget.coverage_percentage_input.text(),
            "net_amount": self.form_widget.net_amount_input.text(),
            "status": "paid",
            "payment_method": self.form_widget.payment_method_combo.currentText(),
            "updated_at": datetime.datetime.now().isoformat(),

        }
        patient_data = {
            "patient_name": self.data["patient_name"],
            "patient_national_id_number": self.data["patient_national_id_number"],
            "billing_date": self.data["billing_date"],
            "doctor_name": self.data["doctor_name"],
            "service_name": self.data["service_name"],
            "service_duration": self.data["service_duration"]
        }

        res = await self.billing_controller.update_billing(billing_id=self.parent.table_view.get_current_id(),
                                                           data=billing_data, patient_data=patient_data)
        if not res:
            self.save_and_cancel_btns.save_btn.stop()
            msg = QMessageBox()
            msg.setText('Error occurred')
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setDetailedText(
                "error occurred while updating billing, please contact your service provider.")
            msg.exec()
        else:
            self.save_and_cancel_btns.save_btn.stop()
            self.close()
            await self.parent.refresh_table()
            msg = QMessageBox()
            msg.setText('Billing Updated Successfully.')
            msg.setIcon(QMessageBox.Icon.Information)
            msg.exec()

    def validate_data(self):
        total_amount = self.form_widget.total_amount_input.text()
        net_amount = self.form_widget.net_amount_input.text()

        if not total_amount:
            QMessageBox.critical(self, "Critical", "Total Amount is required.")

        if not net_amount:
            QMessageBox.critical(self, "Critical", "Net Amount is required.")

        return True

    class FormWidget(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)

            self.parent = parent

            double_validator = QDoubleValidator()
            double_validator.setLocale(locale)
            double_validator.setNotation(QDoubleValidator.Notation.StandardNotation)
            double_validator.setBottom(0)

            self.insurance_provider_label = CustomLabel(name="Insurance Provider")

            self.insurance_provider_input = CustomLineEdit(placeholder_text="", parent=self)

            insurance_provider_vertical_layout = QVBoxLayout()
            insurance_provider_vertical_layout.setContentsMargins(0, 0, 0, 0)
            insurance_provider_vertical_layout.setSpacing(10)

            insurance_provider_vertical_layout.addWidget(self.insurance_provider_label)
            insurance_provider_vertical_layout.addWidget(self.insurance_provider_input, 1)
            # -----------------------------------------------------------
            self.insurance_policy_number_label = CustomLabel(name="Insurance Policy Number")

            self.insurance_policy_number_input = CustomLineEdit(placeholder_text="", parent=self)

            insurance_policy_number_vertical_layout = QVBoxLayout()
            insurance_policy_number_vertical_layout.setContentsMargins(0, 0, 0, 0)
            insurance_policy_number_vertical_layout.setSpacing(10)

            insurance_policy_number_vertical_layout.addWidget(self.insurance_policy_number_label)
            insurance_policy_number_vertical_layout.addWidget(self.insurance_policy_number_input, 1)

            insurance_provider_and_policy_number_vertical_layout = QHBoxLayout()
            insurance_provider_and_policy_number_vertical_layout.setContentsMargins(0, 0, 0, 0)
            insurance_policy_number_vertical_layout.setSpacing(10)

            insurance_provider_and_policy_number_vertical_layout.addLayout(insurance_provider_vertical_layout)
            insurance_provider_and_policy_number_vertical_layout.addLayout(insurance_policy_number_vertical_layout)
            # -----------------------------------------------------------

            total_amount_label = CustomLabel(name="Total Amount")

            self.total_amount_input = CustomLineEdit(placeholder_text="", parent=self)
            self.total_amount_input.setValidator(double_validator)

            total_amount_vertical_layout = QVBoxLayout()
            total_amount_vertical_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            total_amount_vertical_layout.setContentsMargins(0, 0, 0, 0)
            total_amount_vertical_layout.setSpacing(10)

            total_amount_vertical_layout.addWidget(total_amount_label)
            total_amount_vertical_layout.addWidget(self.total_amount_input)
            # -----------------------------------------------------------

            coverage_percentage_label = CustomLabel(name="Coverage Percentage %")

            self.coverage_percentage_input = CustomLineEdit(placeholder_text="", parent=self)
            self.coverage_percentage_input.setValidator(double_validator)

            coverage_percentage_vertical_layout = QVBoxLayout()
            coverage_percentage_vertical_layout.setContentsMargins(0, 0, 0, 0)
            coverage_percentage_vertical_layout.setSpacing(10)

            coverage_percentage_vertical_layout.addWidget(coverage_percentage_label)
            coverage_percentage_vertical_layout.addWidget(self.coverage_percentage_input)
            # -----------------------------------------------------------

            net_amount_label = CustomLabel(name="Net Amount")

            self.net_amount_input = CustomLineEdit(placeholder_text="", parent=self)
            self.net_amount_input.setValidator(double_validator)

            net_amount_vertical_layout = QVBoxLayout()
            net_amount_vertical_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            net_amount_vertical_layout.setContentsMargins(0, 0, 0, 0)
            net_amount_vertical_layout.setSpacing(10)

            net_amount_vertical_layout.addWidget(net_amount_label)
            net_amount_vertical_layout.addWidget(self.net_amount_input)
            # -----------------------------------------------------------
            self.combo_style_sheet = """
            QComboBox {
                border:1px solid #C7C7C7;
                border-radius:7px;
                background-color:white;
                color:black;
                padding-left:10px;
                padding-right:5px;
            }
            QComboBox QAbstractItemView 
            {
                min-width: 150px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border-left-width: 0px;
                padding-right:5px;
            }
            QComboBox::down-arrow {
                image: url(:resources/icons/expand_more.svg);
            }

            QComboBox::down-arrow:on { /* shift the arrow when popup is open */
                top: 1px;
                left: 1px;
            }
            """

            payment_method_label = CustomLabel(name="Payment Method")

            self.payment_method_combo = CustomComboBox()
            self.payment_method_combo.addItem("Card")
            self.payment_method_combo.addItem("Cash")

            self.payment_method_combo.setStyleSheet(self.combo_style_sheet)

            payment_method_layout = QVBoxLayout()
            payment_method_layout.setContentsMargins(0, 0, 0, 0)
            payment_method_layout.setSpacing(10)

            payment_method_layout.addWidget(payment_method_label)
            payment_method_layout.addWidget(self.payment_method_combo)
            # --------------------------------------------------------------

            notes_label = CustomLabel(name="Notes")

            self.notes_input = CustomTextEdit(border_radius=5, placeholder_text="", parent=self)

            notes_layout = QVBoxLayout()
            notes_layout.setContentsMargins(0, 0, 0, 0)
            notes_layout.setSpacing(10)

            notes_layout.addWidget(notes_label)
            notes_layout.addWidget(self.notes_input)
            # --------------------------------------------------------------

            main_vertical_layout = QVBoxLayout()
            main_vertical_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            main_vertical_layout.setSpacing(30)
            main_vertical_layout.setContentsMargins(20, 0, 20, 20)

            main_vertical_layout.addLayout(insurance_provider_and_policy_number_vertical_layout)
            main_vertical_layout.addLayout(total_amount_vertical_layout)
            main_vertical_layout.addLayout(coverage_percentage_vertical_layout)
            main_vertical_layout.addLayout(net_amount_vertical_layout)
            main_vertical_layout.addLayout(payment_method_layout)
            main_vertical_layout.addLayout(notes_layout)

            self.appointment_information_widget = self.AppointmentInformationWidget(parent=self)

            central_widget = QWidget()

            central_widget_layout = QVBoxLayout(central_widget)
            central_widget_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            central_widget_layout.setContentsMargins(20, 0, 20, 0)

            central_widget_layout.addLayout(main_vertical_layout)
            central_widget_layout.addWidget(self.appointment_information_widget)

            scroll_area = CustomScrollArea()
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            scroll_area.setWidget(central_widget)

            layout = QVBoxLayout()
            layout.setSpacing(0)
            layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(scroll_area)

            self.setLayout(layout)

        def toggle_insurance_provider_visibility(self, state):
            self.insurance_provider_label.setVisible(state)
            self.insurance_provider_input.setVisible(state)
            self.insurance_provider_input.setReadOnly(True)

        def toggle_insurance_policy_number_visibility(self, state):
            self.insurance_policy_number_label.setVisible(state)
            self.insurance_policy_number_input.setVisible(state)
            self.insurance_policy_number_input.setReadOnly(True)

        def toggle_inputs_state(self, state, action):
            # set ReadOnly
            self.coverage_percentage_input.setReadOnly(state)
            self.total_amount_input.setReadOnly(state)
            self.net_amount_input.setReadOnly(state)
            self.payment_method_combo.setDisabled(state)

            if action == "view":
                self.appointment_information_widget.patient_name_input.setReadOnly(state)
                self.appointment_information_widget.patient_national_id_number_input.line_edit.setReadOnly(
                    state)
                self.appointment_information_widget.doctor_input.setReadOnly(state)
                self.appointment_information_widget.service_input.setReadOnly(state)
                self.appointment_information_widget.duration_input.setReadOnly(state)
                self.appointment_information_widget.appointment_date_input.line_edit.setReadOnly(
                    state)
                self.appointment_information_widget.appointment_time_input.line_edit.setReadOnly(state)
                self.parent.update_billing_btn.setVisible(False)

            else:
                self.appointment_information_widget.hide()
                self.parent.update_billing_btn.setVisible(True)

            self.parent.finish_and_generate_invoice_btn.setVisible(False)
            self.parent.save_and_cancel_btns.save_btn.setVisible(False)

        class AppointmentInformationWidget(QWidget):
            def __init__(self, parent=None):
                super().__init__(parent)

                self.calendar_icon_path = ":/resources/icons/calendar.svg"

                service_and_duration_label = CustomLabel(name="Service & Duration")

                self.service_input = CustomRoundedLineEdit(placeholder_text="")
                self.duration_input = CustomRoundedLineEdit(placeholder_text="")

                service_and_duration_h_layout = QHBoxLayout()
                service_and_duration_h_layout.setContentsMargins(0, 0, 0, 0)
                service_and_duration_h_layout.setSpacing(10)

                service_and_duration_h_layout.addWidget(self.service_input)
                service_and_duration_h_layout.addWidget(self.duration_input)

                service_and_duration_v_layout = QVBoxLayout()
                service_and_duration_v_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
                service_and_duration_v_layout.setContentsMargins(0, 0, 0, 0)
                service_and_duration_v_layout.setSpacing(10)

                service_and_duration_v_layout.addWidget(service_and_duration_label)
                service_and_duration_v_layout.addLayout(service_and_duration_h_layout)

                # # --------------------------------------------------------------

                doctor_label = CustomLabel(name="Doctor")

                self.doctor_input = CustomRoundedLineEdit(placeholder_text="")
                self.doctor_input.setText("Rukaya Abdul-hussien Jabbar")

                doctor_vertical_layout = QVBoxLayout()
                doctor_vertical_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
                doctor_vertical_layout.setContentsMargins(0, 0, 0, 0)
                doctor_vertical_layout.setSpacing(10)

                doctor_vertical_layout.addWidget(doctor_label)
                doctor_vertical_layout.addWidget(self.doctor_input)
                # --------------------------------------------------------------
                appointment_dates_and_time_label = CustomLabel(name="Appointment Date & Time")

                self.appointment_date_input = CustomLineEditWithIcon(icon_path=self.calendar_icon_path,
                                                                     placeholder_text="")
                self.appointment_date_input.line_edit.setText("Wed, July 17 , 2024")
                self.appointment_date_input.container_widget.setFixedHeight(40)

                self.appointment_time_input = CustomLineEditWithIcon(icon_path=":/resources/icons/clock.svg",
                                                                     placeholder_text="")
                self.appointment_time_input.line_edit.setText("08:00:00")

                appointment_dates_and_time_horizontal_layout = QHBoxLayout()
                appointment_dates_and_time_horizontal_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
                appointment_dates_and_time_horizontal_layout.setContentsMargins(0, 0, 0, 0)
                appointment_dates_and_time_horizontal_layout.setSpacing(10)

                appointment_dates_and_time_horizontal_layout.addWidget(self.appointment_date_input)
                appointment_dates_and_time_horizontal_layout.addWidget(self.appointment_time_input)

                appointment_dates_and_time_vertical_layout = QVBoxLayout()
                appointment_dates_and_time_vertical_layout.setContentsMargins(0, 0, 0, 0)
                appointment_dates_and_time_vertical_layout.setSpacing(10)

                appointment_dates_and_time_vertical_layout.addWidget(appointment_dates_and_time_label)
                appointment_dates_and_time_vertical_layout.addLayout(appointment_dates_and_time_horizontal_layout)
                # ------------------------------------------------------------------------
                doctor_label = CustomLabel(name="Doctor")

                self.doctor_input = CustomRoundedLineEdit(placeholder_text="")

                doctor_vertical_layout = QVBoxLayout()
                doctor_vertical_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
                doctor_vertical_layout.setContentsMargins(0, 0, 0, 0)
                doctor_vertical_layout.setSpacing(10)

                doctor_vertical_layout.addWidget(doctor_label)
                doctor_vertical_layout.addWidget(self.doctor_input)
                # -----------------------------------------------------------------------
                self.patient_national_id_number_input = CustomLineEditWithIcon(
                    icon_path=":/resources/icons/filled_person.svg",
                    placeholder_text="")
                self.patient_national_id_number_input.container_widget.setFixedHeight(40)

                self.patient_name_input = CustomRoundedLineEdit(placeholder_text="")
                self.patient_name_input.setFixedHeight(40)

                patient_name_and_national_id_number_label = CustomLabel(name="Patient Name & National ID Number")

                patient_name_and_national_id_number_horizontal_layout = QHBoxLayout()
                patient_name_and_national_id_number_horizontal_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
                patient_name_and_national_id_number_horizontal_layout.setContentsMargins(0, 0, 0, 0)
                patient_name_and_national_id_number_horizontal_layout.setSpacing(10)

                patient_name_and_national_id_number_horizontal_layout.addWidget(self.patient_name_input)
                patient_name_and_national_id_number_horizontal_layout.addWidget(self.patient_national_id_number_input)

                patient_name_and_national_id_number_vertical_layout = QVBoxLayout()
                patient_name_and_national_id_number_vertical_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
                patient_name_and_national_id_number_vertical_layout.setContentsMargins(0, 0, 0, 0)
                patient_name_and_national_id_number_vertical_layout.setSpacing(10)

                patient_name_and_national_id_number_vertical_layout.addWidget(patient_name_and_national_id_number_label)
                patient_name_and_national_id_number_vertical_layout.addLayout(
                    patient_name_and_national_id_number_horizontal_layout)
                # -------------------------------------------------------------
                create_at_label = CustomLabel(name="Created At")

                self.created_at_input = CustomLineEditWithIcon(icon_path=self.calendar_icon_path,
                                                               placeholder_text="")

                created_at_label_vertical_layout = QVBoxLayout()
                created_at_label_vertical_layout.setContentsMargins(0, 0, 0, 0)
                created_at_label_vertical_layout.setSpacing(10)

                created_at_label_vertical_layout.addWidget(create_at_label)
                created_at_label_vertical_layout.addWidget(self.created_at_input)

                updated_at_label = CustomLabel(name="Updated At")

                self.updated_at_input = CustomLineEditWithIcon(icon_path=self.calendar_icon_path,
                                                               placeholder_text="")

                updated_at_vertical_layout = QVBoxLayout()
                updated_at_vertical_layout.setContentsMargins(0, 0, 0, 0)
                updated_at_vertical_layout.setSpacing(10)

                updated_at_vertical_layout.addWidget(updated_at_label)
                updated_at_vertical_layout.addWidget(self.updated_at_input)

                created_updated_at_horizontal_layout = QHBoxLayout()
                created_updated_at_horizontal_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
                created_updated_at_horizontal_layout.setContentsMargins(0, 0, 0, 0)
                created_updated_at_horizontal_layout.setSpacing(10)

                created_updated_at_horizontal_layout.addLayout(created_at_label_vertical_layout)
                created_updated_at_horizontal_layout.addLayout(updated_at_vertical_layout)
                # ------------------------------------------------------------------------

                main_vertical_layout = QVBoxLayout()
                main_vertical_layout.setSpacing(30)
                main_vertical_layout.setContentsMargins(20, 20, 20, 20)

                main_vertical_layout.addLayout(patient_name_and_national_id_number_vertical_layout)
                main_vertical_layout.addLayout(doctor_vertical_layout)
                main_vertical_layout.addLayout(service_and_duration_v_layout)
                main_vertical_layout.addLayout(appointment_dates_and_time_vertical_layout)

                layout = QVBoxLayout()
                layout.setAlignment(Qt.AlignmentFlag.AlignTop)
                layout.setSpacing(10)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.addLayout(main_vertical_layout)

                self.setLayout(layout)

    class BillingHeaderWidget(QWidget):

        def __init__(self, parent=None):
            super().__init__(parent)

            calendar_icon = QPixmap(":/resources/icons/dollar.svg")
            calendar_icon.scaled(QSize(25, 25), Qt.AspectRatioMode.KeepAspectRatio,
                                 Qt.TransformationMode.SmoothTransformation)

            calendar_icon_label = QLabel()
            calendar_icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            calendar_icon_label.setFixedSize(QSize(30, 30))
            calendar_icon_label.setStyleSheet(" QLabel { border:0; }")
            calendar_icon_label.setPixmap(calendar_icon)

            icon_widget = QWidget()
            icon_widget.setFixedSize(40, 40)
            icon_widget.setStyleSheet("border:1px solid #e5e7eb;background-color:transparent;border-radius:7px;")

            icon_widget_layout = QVBoxLayout()
            icon_widget_layout.setSpacing(0)
            icon_widget_layout.setContentsMargins(5, 5, 5, 5)
            icon_widget_layout.addWidget(calendar_icon_label)

            icon_widget.setLayout(icon_widget_layout)

            make_an_appointment_label = QLabel("Billing information")
            make_an_appointment_label.setStyleSheet("border:0;background-color:transparent;color:black;")

            make_an_appointment_font = make_an_appointment_label.font()
            make_an_appointment_font.setWeight(make_an_appointment_font.Weight.Medium)
            make_an_appointment_font.setPointSize(14)

            make_an_appointment_label.setFont(make_an_appointment_font)

            fill_in_data_label = QLabel("Complete billing details to make payment.")
            fill_in_data_label.setStyleSheet("border:0;background-color:transparent;color:#696969")

            fill_in_data_font = fill_in_data_label.font()
            fill_in_data_font.setPointSize(12)

            fill_in_data_label.setFont(fill_in_data_font)

            labels_layout = QVBoxLayout()
            labels_layout.setSpacing(10)
            labels_layout.addWidget(make_an_appointment_label)
            labels_layout.addWidget(fill_in_data_label)

            self.internal_loader = InternalLoader(height=30, parent=self)

            main_h_layout = QHBoxLayout()
            main_h_layout.setSpacing(15)
            main_h_layout.setContentsMargins(28, 17, 28, 25)

            main_h_layout.addWidget(icon_widget)
            main_h_layout.addLayout(labels_layout)
            main_h_layout.addWidget(self.internal_loader)

            central_widget = QWidget()
            central_widget.setObjectName("appointment_header_widget")
            central_widget.setStyleSheet("""
                QWidget#appointment_header_widget {
                    border:0;
                    border-bottom:1px solid #E3E0E0;
                }
                """)
            central_widget.setLayout(main_h_layout)

            main_v_layout = QVBoxLayout()
            main_v_layout.setContentsMargins(0, 0, 0, 0)
            main_v_layout.setSpacing(0)
            main_v_layout.addWidget(central_widget)

            self.setObjectName("appointment_header_widget")

            self.setLayout(main_v_layout)

        @pyqtSlot(bool)
        def handle_internal_loader_status(self, status: bool):
            if status:
                self.internal_loader.start()
            else:
                self.internal_loader.stop()
