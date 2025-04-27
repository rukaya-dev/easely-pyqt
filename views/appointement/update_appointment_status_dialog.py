import datetime

from PyQt6.QtCore import Qt, QSize, pyqtSlot
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QMessageBox, QHBoxLayout
from qasync import asyncSlot

from services.supabase.controllers.appointment.appointment_statuses_controller import AppointmentStatusesController
from services.supabase.controllers.billing.billing_controller import BillingController
from signals import SignalRepositorySingleton
from views.billing.billing_dialog import BillingDialog
from views.componenets.customsComponents.buttons.button_with_loader import ButtonWithLoader
from views.componenets.customsComponents.custom_combobox import CustomComboBox
from views.componenets.customsComponents.table.form_componenets.custom_label import CustomLabel
from views.componenets.customsComponents.table.save_and_cancel_buttons import SaveAndCancelButtonsWithLoader


class UpdateAppointmentStatusDialog(QDialog):
    def __init__(self, controller, appointment_id, parent=None):
        super().__init__(parent)

        self.parent = parent
        self.appointment_id = appointment_id

        # Signals
        self.signals = SignalRepositorySingleton.instance()

        self.appointments_controller = controller
        self.appointment_status_controller = AppointmentStatusesController()
        self.billing_controller = BillingController()

        self.error_message = "Error occurred Please contact your service provider."

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

        appointment_status_label = CustomLabel(name="Appointment Status")

        self.appointment_status_combo = CustomComboBox()
        self.appointment_status_combo.setFixedWidth(400)
        self.appointment_status_combo.setStyleSheet(self.combo_style_sheet)

        self.appointment_status_model = QStandardItemModel()
        self.appointment_status_combo.setModel(self.appointment_status_model)

        self.appointment_status_combo.currentIndexChanged.connect(self.update_ui_content)

        self.save_and_cancel_btns = SaveAndCancelButtonsWithLoader(text="Save")
        self.save_and_cancel_btns.save_btn.clicked.connect(self.update_appointment_status)
        self.save_and_cancel_btns.cancel_btn.clicked.connect(self.close)

        self.start_billing_btn = ButtonWithLoader("Start Billing", QSize(100, 34))
        start_billing_btn_policy = self.start_billing_btn.sizePolicy()
        start_billing_btn_policy.setRetainSizeWhenHidden(False)
        self.start_billing_btn.hide()

        self.start_billing_btn.clicked.connect(self.get_initial_billing_data)

        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)
        controls_layout.addWidget(self.save_and_cancel_btns, 1, Qt.AlignmentFlag.AlignRight)
        controls_layout.addWidget(self.start_billing_btn, 0, Qt.AlignmentFlag.AlignRight)

        self.start_billing_btn.setVisible(False)

        appointment_status_layout = QVBoxLayout()
        appointment_status_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        appointment_status_layout.setContentsMargins(0, 0, 0, 0)
        appointment_status_layout.setSpacing(10)

        appointment_status_layout.addWidget(appointment_status_label)
        appointment_status_layout.addWidget(self.appointment_status_combo)

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.setContentsMargins(20, 20, 20, 20)

        layout.addLayout(appointment_status_layout)
        layout.addLayout(controls_layout, Qt.AlignmentFlag.AlignRight)

        self.setLayout(layout)
        self.setFixedSize(500, 200)

    @asyncSlot()
    async def populate_statuses(self):
        statuses = self.appointment_status_controller.store.get_data()
        if not statuses:
            msg = QMessageBox()
            msg.setText(self.error_message)
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.exec()
        else:
            for item in statuses:
                if item["status_name"] != "invoiced":
                    standard_item = QStandardItem()
                    standard_item.setData(item["status_name"], Qt.ItemDataRole.DisplayRole)
                    standard_item.setData(item["status_id"], Qt.ItemDataRole.UserRole)
                    self.appointment_status_model.appendRow(standard_item)

    @asyncSlot()
    async def update_appointment_status(self):
        self.save_and_cancel_btns.save_btn.start()
        status = self.appointment_status_combo.currentText()
        data = {"appointment_status": status, "updated_at": datetime.datetime.now().isoformat()}
        res = await self.appointments_controller.update_appointment_status_or_additional_data(
            self.parent.table_view.get_current_id(),
            data)
        if not res:
            self.save_and_cancel_btns.save_btn.stop()
            msg = QMessageBox()
            msg.setText(self.error_message)
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.exec()
        else:
            self.save_and_cancel_btns.save_btn.stop()
            self.signals.globalAppointmentUpdateTableViewSignal.emit()
            self.close()
            msg = QMessageBox()
            msg.setText('Appointment Status Successfully Updated.')
            msg.setIcon(QMessageBox.Icon.Information)
            msg.exec()

    @pyqtSlot(int)
    def update_ui_content(self, index):
        current_status = self.appointment_status_combo.currentText()
        if current_status == "ready-to-invoice":
            self.save_and_cancel_btns.save_btn.hide()
            self.start_billing_btn.show()
        else:
            self.save_and_cancel_btns.save_btn.show()
            self.start_billing_btn.hide()

    @asyncSlot()
    async def get_initial_billing_data(self):
        self.start_billing_btn.start()
        data = await self.appointments_controller.get_appointment_data_for_billing(self.appointment_id)

        if not data:
            msg = QMessageBox()
            msg.setText(self.error_message)
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.exec()
            self.start_billing_btn.stop()
        else:
            self.start_billing_btn.stop()
            self.show_create_billing_dialog(data=data)

    @pyqtSlot()
    def show_create_billing_dialog(self, data):
        create_billing_dialog = BillingDialog(billing_controller=self.billing_controller,
                                              appointments_controller=self.appointments_controller,
                                              appointment_id=self.appointment_id, data=data, parent=self)
        create_billing_dialog.update_billing_btn.hide()

        create_billing_form_widget = create_billing_dialog.form_widget
        create_billing_form_widget.appointment_information_widget.hide()

        if data["insurance_provider"]:
            create_billing_form_widget.insurance_provider_input.setText(data["insurance_provider"])
            create_billing_form_widget.toggle_insurance_provider_visibility(True)
        else:
            create_billing_form_widget.toggle_insurance_provider_visibility(False)

        if data["insurance_policy_number"]:
            create_billing_form_widget.insurance_policy_number_input.setText(data["insurance_policy_number"])
            create_billing_form_widget.toggle_insurance_policy_number_visibility(True)
        else:
            create_billing_form_widget.toggle_insurance_policy_number_visibility(False)

        if data["coverage_percentage"]:
            create_billing_form_widget.coverage_percentage_input.setText(str(data["coverage_percentage"]))
        else:
            create_billing_form_widget.coverage_percentage_input.setText(str(0.0))

        create_billing_form_widget.total_amount_input.setText(str(data["doctor_service_cost"]))

        create_billing_form_widget.net_amount_input.setReadOnly(True)

        self.close()
        create_billing_dialog.updateGeometry()

        create_billing_dialog.show()
