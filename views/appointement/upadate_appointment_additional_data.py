import datetime

from PyQt6.QtCore import Qt, QTime
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QWidget, QMessageBox, QHBoxLayout
from qasync import asyncSlot

from signals import SignalRepositorySingleton
from views.componenets.customsComponents.custom_combobox import CustomComboBox
from views.componenets.customsComponents.dates_and_times.custom_time_picker import CustomTimePicker
from views.componenets.customsComponents.table.form_componenets.custom_label import CustomLabel
from views.componenets.customsComponents.table.form_componenets.custom_text_edit import CustomTextEdit
from views.componenets.customsComponents.table.save_and_cancel_buttons import SaveAndCancelButtonsWithLoader


class UpdateAppointmentAdditionalDataDialog(QDialog):
    def __init__(self, appointment_controller, appointment_types_controller, parent=None):
        super().__init__(parent)

        self.parent = parent

        self.signals = SignalRepositorySingleton.instance()

        self.appointments_controller = appointment_controller
        self.appointments_types = appointment_types_controller

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

        appointment_type_label = CustomLabel(name="Appointment type")

        self.appointment_type_model = QStandardItemModel()

        self.appointment_type_combo = CustomComboBox()
        self.appointment_type_combo.setFixedWidth(400)

        self.appointment_type_combo.setStyleSheet(self.combo_style_sheet)
        self.appointment_type_combo.setModel(self.appointment_type_model)

        appointment_type_layout = QVBoxLayout()
        appointment_type_layout.setContentsMargins(0, 0, 0, 0)
        appointment_type_layout.setSpacing(10)

        appointment_type_layout.addWidget(appointment_type_label)
        appointment_type_layout.addWidget(self.appointment_type_combo)
        # --------------------------------------------------------------
        check_in_label = CustomLabel(name="Check in Time")

        self.check_in_input = CustomTimePicker()
        self.check_in_input.setFixedWidth(190)

        check_in_label_vertical_layout = QVBoxLayout()
        check_in_label_vertical_layout.setContentsMargins(0, 0, 0, 0)
        check_in_label_vertical_layout.setSpacing(10)

        check_in_label_vertical_layout.addWidget(check_in_label)
        check_in_label_vertical_layout.addWidget(self.check_in_input)

        check_out_label = CustomLabel(name="Check out Time")

        self.check_out_input = CustomTimePicker()
        self.check_out_input.setFixedWidth(190)

        check_out_vertical_layout = QVBoxLayout()
        check_out_vertical_layout.setContentsMargins(0, 0, 0, 0)
        check_out_vertical_layout.setSpacing(10)

        check_out_vertical_layout.addWidget(check_out_label)
        check_out_vertical_layout.addWidget(self.check_out_input)

        check_in_out_time_horizontal_layout = QHBoxLayout()
        check_in_out_time_horizontal_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        check_in_out_time_horizontal_layout.setContentsMargins(0, 0, 0, 0)
        check_in_out_time_horizontal_layout.setSpacing(20)

        check_in_out_time_horizontal_layout.addLayout(check_in_label_vertical_layout)
        check_in_out_time_horizontal_layout.addLayout(check_out_vertical_layout)
        # ------------------------------------------------------------------------

        reason_of_visit_label = CustomLabel(name="Reason of visit")

        self.reason_for_visit_input = CustomTextEdit(border_radius=7, placeholder_text="")
        self.reason_for_visit_input.setFixedWidth(400)

        reason_of_visit_vertical_layout = QVBoxLayout()
        reason_of_visit_vertical_layout.setContentsMargins(0, 0, 0, 0)
        reason_of_visit_vertical_layout.setSpacing(10)

        reason_of_visit_vertical_layout.addWidget(reason_of_visit_label)
        reason_of_visit_vertical_layout.addWidget(self.reason_for_visit_input)
        # --------------------------------------------------------------

        notes_label = CustomLabel(name="Notes")

        self.notes_input = CustomTextEdit(border_radius=7, placeholder_text="")
        self.notes_input.setFixedWidth(400)

        notes_vertical_layout = QVBoxLayout()
        notes_vertical_layout.setContentsMargins(0, 0, 0, 0)
        notes_vertical_layout.setSpacing(10)

        notes_vertical_layout.addWidget(notes_label)
        notes_vertical_layout.addWidget(self.notes_input)

        self.save_and_cancel_btns = SaveAndCancelButtonsWithLoader(text="Save")
        self.save_and_cancel_btns.save_btn.clicked.connect(self.update_appointment_additional_data)
        self.save_and_cancel_btns.cancel_btn.clicked.connect(self.close)

        main_vertical_layout = QVBoxLayout()
        main_vertical_layout.setSpacing(20)
        main_vertical_layout.setContentsMargins(0, 0, 0, 0)

        main_vertical_layout.addLayout(appointment_type_layout)
        main_vertical_layout.addLayout(check_in_out_time_horizontal_layout)
        main_vertical_layout.addLayout(reason_of_visit_vertical_layout)
        main_vertical_layout.addLayout(notes_vertical_layout)

        central_widget = QWidget()
        central_widget.setLayout(main_vertical_layout)

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.addWidget(central_widget)
        layout.addWidget(self.save_and_cancel_btns, 1, Qt.AlignmentFlag.AlignRight)

        self.setLayout(layout)
        self.setFixedSize(500, 600)

    async def populate_appointment_types(self):
        types = self.appointments_types.store.get_data()
        if types:
            for item in types:
                standard_item = QStandardItem()
                standard_item.setData(item["type_name"], Qt.ItemDataRole.DisplayRole)
                standard_item.setData(item["type_id"], Qt.ItemDataRole.UserRole)
                self.appointment_type_model.appendRow(standard_item)

    @asyncSlot()
    async def update_appointment_additional_data(self):
        self.save_and_cancel_btns.save_btn.start()
        appointment_type = self.appointment_type_combo.currentText()
        check_in_time = QTime(self.check_in_input.time().toPyTime()).toString()
        check_out_time = QTime(self.check_out_input.time().toPyTime()).toString()
        reason_for_visit = self.reason_for_visit_input.toPlainText()
        notes = self.notes_input.toPlainText()

        data = {"appointment_type": appointment_type,
                "check_in_time": check_in_time,
                "check_out_time": check_out_time,
                "reason_for_visit": reason_for_visit,
                "notes": notes,
                "updated_at": datetime.datetime.now().isoformat()}

        res = await self.appointments_controller.update_appointment_status_or_additional_data(
            self.parent.table_view.get_current_id(),
            data)
        if not res:
            self.save_and_cancel_btns.save_btn.stop()
            msg = QMessageBox()
            msg.setText('Error occurred')
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setDetailedText(
                "error occurred while updating appointment additional data, please contact your service provider.")
            msg.exec()
        else:
            self.save_and_cancel_btns.save_btn.stop()
            self.signals.globalAppointmentUpdateTableViewSignal.emit()
            self.close()
            msg = QMessageBox()
            msg.setText('Appointment Additional Data Successfully Updated.')
            msg.setIcon(QMessageBox.Icon.Information)
            msg.exec()
