from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QMessageBox
from qasync import asyncSlot

from services.supabase.controllers.settings.service_controller import ServiceController
from signals import SignalRepositorySingleton
from utils.validator import AgeIntValidator
from views.componenets.customsComponents.custom_combobox import CustomComboBox
from views.componenets.customsComponents.table.form_componenets.custom_input import CustomLineEdit
from views.componenets.customsComponents.table.form_componenets.custom_label import CustomLabel
from views.componenets.customsComponents.table.form_componenets.custom_text_edit import CustomTextEdit
from views.staff.doctors.doctor_service_management.assistants_selection_widget import AssistantsSelectionWidget
from views.staff.doctors.doctors_management.available_days_widget import AvailableDaysWidget


class DoctorServiceForm(QWidget):
    def __init__(self, action_type, parent=None):
        super().__init__(parent)

        self.action_type = action_type

        self.generated_time_slots = []

        # Signals
        self.signals = SignalRepositorySingleton.instance()

        # Controllers
        self.service_controller = ServiceController()

        self.int_validator = AgeIntValidator()

        self.service_name_label = CustomLabel(name="Service Name")

        self.service_name_model = QStandardItemModel()

        self.service_name_selection_widget = CustomComboBox()
        self.service_name_selection_widget.setModel(self.service_name_model)

        if self.action_type == "add":
            self.populate_services()

        service_name_selection_vertical_layout = QVBoxLayout()
        service_name_selection_vertical_layout.setContentsMargins(0, 0, 0, 0)
        service_name_selection_vertical_layout.setSpacing(10)

        service_name_selection_vertical_layout.addWidget(self.service_name_label)
        service_name_selection_vertical_layout.addWidget(self.service_name_selection_widget)
        # -----------------------------------------------------------

        cost_label = CustomLabel(name="Service Cost")

        self.cost_input = CustomLineEdit(placeholder_text="", parent=self)

        cost_range_vertical_layout = QVBoxLayout()
        cost_range_vertical_layout.setContentsMargins(0, 0, 0, 0)
        cost_range_vertical_layout.setSpacing(10)

        cost_range_vertical_layout.addWidget(cost_label)
        cost_range_vertical_layout.addWidget(self.cost_input)
        # -----------------------------------------------------------
        duration = CustomLabel(name="Service Duration")

        self.duration_input = CustomLineEdit(placeholder_text="30", parent=self)

        duration_vertical_layout = QVBoxLayout()
        duration_vertical_layout.setContentsMargins(0, 0, 0, 0)
        duration_vertical_layout.setSpacing(10)

        duration_vertical_layout.addWidget(duration)
        duration_vertical_layout.addWidget(self.duration_input)
        # -----------------------------------------------------------

        cost_range_duration_layout = QHBoxLayout()
        cost_range_duration_layout.setSpacing(10)

        cost_range_duration_layout.addLayout(cost_range_vertical_layout)
        cost_range_duration_layout.addLayout(duration_vertical_layout)

        status_label = CustomLabel(name="Service Status")

        self.status_selection_widget = CustomComboBox()
        self.status_selection_widget.addItems(["Active", "Inactive"])

        status_vertical_layout = QVBoxLayout()
        status_vertical_layout.setContentsMargins(0, 0, 0, 0)
        status_vertical_layout.setSpacing(10)

        status_vertical_layout.addWidget(status_label)
        status_vertical_layout.addWidget(self.status_selection_widget)
        # -----------------------------------------------------

        additional_data_label = CustomLabel(name="Additional Data")

        self.additional_data_input = CustomTextEdit(border_radius=2,placeholder_text="", parent=self)
        self.additional_data_input.setMaximumHeight(200)

        service_additional_data_vertical_layout = QVBoxLayout()
        service_additional_data_vertical_layout.setSpacing(10)

        service_additional_data_vertical_layout.addWidget(additional_data_label)
        service_additional_data_vertical_layout.addWidget(self.additional_data_input, 0)
        # -----------------------------------------------------

        doctor_schedule_label = CustomLabel(name="Doctor Schedule")

        self.days_widget_and_time_slots_widget = AvailableDaysWidget()

        self.available_days_vertical_layout = QVBoxLayout()
        self.available_days_vertical_layout.setContentsMargins(20, 20, 20, 20)
        self.available_days_vertical_layout.setSpacing(30)

        self.available_days_vertical_layout.addWidget(self.days_widget_and_time_slots_widget)

        self.dates_and_times_widget = QWidget()
        self.dates_and_times_widget.setObjectName("dates_and_times_widget")
        self.dates_and_times_widget.setStyleSheet("""
            QWidget#dates_and_times_widget {
                border:1px solid #D5D6D8;
                background-color:white;
            }
            QLabel {
                border:0;
                background-color:transparent;
            }
            """)

        self.dates_and_times_widget.setLayout(self.available_days_vertical_layout)

        dates_and_times_layout = QVBoxLayout()
        dates_and_times_layout.setSpacing(10)

        dates_and_times_layout.addWidget(doctor_schedule_label)
        dates_and_times_layout.addWidget(self.dates_and_times_widget)
        # ------------------------------------------------------------

        assistants_schedule_label = CustomLabel(name="Doctor Service Assistants")

        self.assistants_selection_widget = AssistantsSelectionWidget()

        self.assistants_selection_vertical_layout = QVBoxLayout()
        self.assistants_selection_vertical_layout.setContentsMargins(20, 20, 20, 20)
        self.assistants_selection_vertical_layout.setSpacing(30)

        self.assistants_selection_vertical_layout.addWidget(self.assistants_selection_widget)

        self.assistants_widget = QWidget()
        self.assistants_widget.setObjectName("assistants_widget")
        self.assistants_widget.setStyleSheet("""
            QWidget#assistants_widget {
                border:1px solid #D5D6D8;
                background-color:white;
            }
            QLabel {
                border:0;
                background-color:transparent;
            }
            """)
        self.assistants_widget.setLayout(self.assistants_selection_vertical_layout)

        assistants_schedule_layout = QVBoxLayout()
        assistants_schedule_layout.setSpacing(10)

        assistants_schedule_layout.addWidget(assistants_schedule_label)
        assistants_schedule_layout.addWidget(self.assistants_widget)

        self.main_vertical_layout = QVBoxLayout()
        self.main_vertical_layout.setContentsMargins(0, 0, 0, 0)
        self.main_vertical_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.main_vertical_layout.setSpacing(32)

        self.main_vertical_layout.addLayout(service_name_selection_vertical_layout)
        self.main_vertical_layout.addLayout(cost_range_duration_layout)
        self.main_vertical_layout.addLayout(status_vertical_layout)
        self.main_vertical_layout.addLayout(service_additional_data_vertical_layout)
        self.main_vertical_layout.addLayout(dates_and_times_layout)
        self.main_vertical_layout.addLayout(assistants_schedule_layout)

        central_widget = QWidget()
        central_widget.setLayout(self.main_vertical_layout)

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(central_widget)

        self.setLayout(layout)

    @asyncSlot()
    async def populate_services(self):
        services = await self.service_controller.get_all_services()
        if not services:
            msg = QMessageBox()
            msg.setText('Error occurred')
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setDetailedText("error occurred while deleting, please contact your service provider.")
            msg.exec()
        else:
            self.service_name_model.clear()
            for item in services:
                standardItem = QStandardItem()
                standardItem.setData(item["name"], Qt.ItemDataRole.DisplayRole)
                standardItem.setData(item["service_id"], Qt.ItemDataRole.UserRole)
                self.service_name_model.appendRow(standardItem)
