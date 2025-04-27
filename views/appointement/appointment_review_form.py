from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout

from services.supabase.controllers.staff.doctor.doctor_schedule_controller import DoctorScheduleController
from services.supabase.controllers.staff.doctor.doctor_service_relation_controller import \
    DoctorServiceRelationController
from views.componenets.customsComponents.custom_combobox import CustomComboBox
from views.componenets.customsComponents.custom_line_edit_with_icon import CustomLineEditWithIcon
from views.componenets.customsComponents.custom_rounded_line_edit import CustomRoundedLineEdit
from views.componenets.customsComponents.table.form_componenets.custom_label import CustomLabel
from PyQt6.QtCore import Qt
from views.componenets.customsComponents.table.form_componenets.custom_text_edit import CustomTextEdit


class AppointmentReviewForm(QWidget):
    def __init__(self, appointment_controller, appointment_types_controller, service_controller, parent=None):
        super().__init__(parent)

        self.data = None
        self.parent = parent

        self.doctor_service_controller = DoctorServiceRelationController()
        self.doctor_schedule_controller = DoctorScheduleController()
        self.appointments_controller = appointment_controller
        self.appointments_types_controller = appointment_types_controller
        self.service_controller = service_controller

        self.appointment_specification_form = AppointmentSpecificationsForm(appointment_types_controller=self.appointments_types_controller)
        self.appointment_details_and_patient_review = AppointmentDetailsAndPatientReview(parent=self)

        main_vertical_layout = QHBoxLayout()
        main_vertical_layout.setSpacing(20)
        main_vertical_layout.setContentsMargins(0, 0, 0, 0)

        main_vertical_layout.addWidget(self.appointment_specification_form)
        main_vertical_layout.addWidget(self.appointment_details_and_patient_review)

        central_widget = QWidget()
        central_widget.setStyleSheet("background-color:transparent;")
        central_widget.setLayout(main_vertical_layout)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(central_widget)

        self.setLayout(layout)

    def set_data(self, patient_data, appointment_details_data):
        self.data = patient_data
        appointment_details_data = {k: v for k, v in appointment_details_data.items() if 'key' not in k.lower()}
        self.data.update(appointment_details_data)
        self.appointment_details_and_patient_review.set_appointment_details_and_patient_review_data(self.data)


class AppointmentDetailsAndPatientReview(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        service_label = CustomLabel(name="Service")

        self.service_input = CustomRoundedLineEdit(placeholder_text="")
        self.service_input.setFixedWidth(314)
        self.service_input.setText("Ultrasound")

        service_layout = QVBoxLayout()
        service_layout.setContentsMargins(0, 0, 0, 0)
        service_layout.setSpacing(10)

        service_layout.addWidget(service_label)
        service_layout.addWidget(self.service_input)
        # --------------------------------------------------------------

        doctor_label = CustomLabel(name="Doctor")

        self.doctor_input = CustomRoundedLineEdit(placeholder_text="")
        self.doctor_input.setFixedWidth(314)
        self.doctor_input.setText("Rukaya Abdul-hussien Jabbar")

        doctor_vertical_layout = QVBoxLayout()
        doctor_vertical_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        doctor_vertical_layout.setContentsMargins(0, 0, 0, 0)
        doctor_vertical_layout.setSpacing(10)

        doctor_vertical_layout.addWidget(doctor_label)
        doctor_vertical_layout.addWidget(self.doctor_input)
        # # --------------------------------------------------------------
        dates_and_time_label = CustomLabel(name="Dates & Times")

        self.date_input = CustomLineEditWithIcon(icon_path=":/resources/icons/calendar.svg", placeholder_text="")
        self.date_input.line_edit.setText("Wed, July 17 , 2024")
        self.date_input.container_widget.setFixedHeight(40)

        self.time_input = CustomLineEditWithIcon(icon_path=":/resources/icons/clock.svg", placeholder_text="")
        self.time_input.line_edit.setText("08:00:00")
        self.time_input.line_edit.setFixedSize(100, 30)
        self.time_input.container_widget.setFixedSize(150, 40)

        dates_and_time_horizontal_layout = QHBoxLayout()
        dates_and_time_horizontal_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        dates_and_time_horizontal_layout.setContentsMargins(0, 0, 0, 0)
        dates_and_time_horizontal_layout.setSpacing(10)

        dates_and_time_horizontal_layout.addWidget(self.date_input, 0)
        dates_and_time_horizontal_layout.addWidget(self.time_input, 0)

        dates_and_time_vertical_layout = QVBoxLayout()
        dates_and_time_vertical_layout.setContentsMargins(0, 0, 0, 0)
        dates_and_time_vertical_layout.setSpacing(10)

        dates_and_time_vertical_layout.addWidget(dates_and_time_label)
        dates_and_time_vertical_layout.addLayout(dates_and_time_horizontal_layout)
        # ------------------------------------------------------------------------
        doctor_label = CustomLabel(name="Doctor")

        self.doctor_input = CustomRoundedLineEdit(placeholder_text="")
        self.doctor_input.setFixedWidth(314)
        self.doctor_input.setText("Rukaya Abdul-hussien Jabbar")

        doctor_vertical_layout = QVBoxLayout()
        doctor_vertical_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        doctor_vertical_layout.setContentsMargins(0, 0, 0, 0)
        doctor_vertical_layout.setSpacing(10)

        doctor_vertical_layout.addWidget(doctor_label)
        doctor_vertical_layout.addWidget(self.doctor_input)
        # # --------------------------------------------------------------
        cost_and_duration_label = CustomLabel(name="Cost & Duration")

        self.cost_input = CustomLineEditWithIcon(icon_path=":/resources/icons/dollar.svg", placeholder_text="")
        self.cost_input.line_edit.setText("500")
        self.cost_input.container_widget.setFixedWidth(200)
        self.cost_input.line_edit.setFixedWidth(100)
        self.cost_input.container_widget.setFixedHeight(40)

        self.duration_input = CustomRoundedLineEdit(placeholder_text="")
        self.duration_input.setText("40 min")
        self.duration_input.setFixedWidth(150)

        cost_and_duration_horizontal_layout = QHBoxLayout()
        cost_and_duration_horizontal_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        cost_and_duration_horizontal_layout.setContentsMargins(0, 0, 0, 0)
        cost_and_duration_horizontal_layout.setSpacing(10)

        cost_and_duration_horizontal_layout.addWidget(self.cost_input, 0, Qt.AlignmentFlag.AlignLeft)
        cost_and_duration_horizontal_layout.addWidget(self.duration_input, 1, Qt.AlignmentFlag.AlignLeft)

        cost_and_duration_vertical_layout = QVBoxLayout()
        cost_and_duration_vertical_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        cost_and_duration_vertical_layout.setContentsMargins(0, 0, 0, 0)
        cost_and_duration_vertical_layout.setSpacing(10)

        cost_and_duration_vertical_layout.addWidget(cost_and_duration_label)
        cost_and_duration_vertical_layout.addLayout(cost_and_duration_horizontal_layout)
        # ------------------------------------------------------------------------
        patient_national_id_number_label = CustomLabel(name="Patient National ID Number")

        self.patient_national_id_number_input = CustomLineEditWithIcon(icon_path=":/resources/icons/filled_person.svg",
                                                                       placeholder_text="")
        self.patient_national_id_number_input.container_widget.setFixedHeight(40)

        patient_national_id_number_vertical_layout = QVBoxLayout()
        patient_national_id_number_vertical_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        patient_national_id_number_vertical_layout.setContentsMargins(0, 0, 0, 0)
        patient_national_id_number_vertical_layout.setSpacing(10)

        patient_national_id_number_vertical_layout.addWidget(patient_national_id_number_label)
        patient_national_id_number_vertical_layout.addWidget(self.patient_national_id_number_input)
        # # --------------------------------------------------------------
        patient_firstname_label = CustomLabel(name="Patient First Name")

        self.patient_first_name_input = CustomRoundedLineEdit(placeholder_text="")
        self.patient_first_name_input.setFixedHeight(40)

        patient_first_name_vertical_layout = QVBoxLayout()
        patient_first_name_vertical_layout.setContentsMargins(0, 0, 0, 0)
        patient_first_name_vertical_layout.setSpacing(10)

        patient_first_name_vertical_layout.addWidget(patient_firstname_label)
        patient_first_name_vertical_layout.addWidget(self.patient_first_name_input)

        patient_lastname_label = CustomLabel(name="Patient Last Name")

        self.patient_lastname_input = CustomRoundedLineEdit(placeholder_text="")
        self.patient_lastname_input.setFixedHeight(40)

        patient_lastname_vertical_layout = QVBoxLayout()
        patient_lastname_vertical_layout.setContentsMargins(0, 0, 0, 0)
        patient_lastname_vertical_layout.setSpacing(10)

        patient_lastname_vertical_layout.addWidget(patient_lastname_label)
        patient_lastname_vertical_layout.addWidget(self.patient_lastname_input)

        patient_first_last_name_and_age_horizontal_layout = QHBoxLayout()
        patient_first_last_name_and_age_horizontal_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        patient_first_last_name_and_age_horizontal_layout.setContentsMargins(0, 0, 0, 0)
        patient_first_last_name_and_age_horizontal_layout.setSpacing(10)

        patient_first_last_name_and_age_horizontal_layout.addLayout(patient_first_name_vertical_layout)
        patient_first_last_name_and_age_horizontal_layout.addLayout(patient_lastname_vertical_layout)
        # --------------------------------------------------------------

        patient_age_label = CustomLabel(name="Age")

        self.patient_age_input = CustomRoundedLineEdit(placeholder_text="")
        self.patient_age_input.setFixedWidth(75)
        self.patient_age_input.setText("23")

        patient_age_vertical_layout = QVBoxLayout()
        patient_age_vertical_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        patient_age_vertical_layout.setContentsMargins(0, 0, 0, 0)
        patient_age_vertical_layout.setSpacing(10)

        patient_age_vertical_layout.addWidget(patient_age_label)
        patient_age_vertical_layout.addWidget(self.patient_age_input)
        # --------------------------------------------------------------

        wrapper_widget = QWidget()
        wrapper_widget.setStyleSheet("background-color:#F9FBFC; border:0; border-left:1px solid #F5F4F4;")

        main_vertical_layout = QVBoxLayout(wrapper_widget)
        main_vertical_layout.setSpacing(30)
        main_vertical_layout.setContentsMargins(20, 20, 20, 20)

        main_vertical_layout.addLayout(patient_national_id_number_vertical_layout)
        main_vertical_layout.addLayout(patient_first_last_name_and_age_horizontal_layout)
        main_vertical_layout.addLayout(doctor_vertical_layout)
        main_vertical_layout.addLayout(service_layout)
        main_vertical_layout.addLayout(dates_and_time_vertical_layout)
        main_vertical_layout.addLayout(cost_and_duration_vertical_layout)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 30, 0)
        layout.addWidget(wrapper_widget)

        self.setLayout(layout)

    def set_appointment_details_and_patient_review_data(self, data):
        self.service_input.setText(data["service_name"])
        self.doctor_input.setText(data["doctor_name"])
        self.date_input.line_edit.setText(data["appointment_date"])
        self.time_input.line_edit.setText(data["appointment_time"] + ":00")
        self.cost_input.line_edit.setText(str(data["doctor_service_relation_data"]["doctor_service_cost"]))
        self.duration_input.setText(str(data["doctor_service_relation_data"]["doctor_service_duration"]))
        self.time_input.line_edit.setText(data["appointment_time"] + ":00")
        self.patient_first_name_input.setText(data["first_name"])
        self.patient_lastname_input.setText(data["last_name"])
        self.patient_national_id_number_input.line_edit.setText(data["national_id_number"])

        self.service_input.setReadOnly(True)
        self.doctor_input.setReadOnly(True)
        self.date_input.line_edit.setReadOnly(True)
        self.time_input.line_edit.setReadOnly(True)
        self.patient_first_name_input.setReadOnly(True)
        self.patient_lastname_input.setReadOnly(True)
        self.patient_national_id_number_input.line_edit.setReadOnly(True)
        self.cost_input.line_edit.setReadOnly(True)
        self.duration_input.setReadOnly(True)


class AppointmentSpecificationsForm(QWidget):
    def __init__(self, appointment_types_controller, parent=None):
        super().__init__(parent)

        self.appointment_types_controller = appointment_types_controller

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
        self.populate_appointment_types()

        appointment_type_layout = QVBoxLayout()
        appointment_type_layout.setContentsMargins(0, 0, 0, 0)
        appointment_type_layout.setSpacing(10)

        appointment_type_layout.addWidget(appointment_type_label)
        appointment_type_layout.addWidget(self.appointment_type_combo)
        # --------------------------------------------------------------

        reason_of_visit_label = CustomLabel(name="Reason of visit")

        self.reason_of_visit_input = CustomTextEdit(border_radius=7, placeholder_text="")
        self.reason_of_visit_input.setFixedWidth(400)

        reason_of_visit_vertical_layout = QVBoxLayout()
        reason_of_visit_vertical_layout.setContentsMargins(0, 0, 0, 0)
        reason_of_visit_vertical_layout.setSpacing(10)

        reason_of_visit_vertical_layout.addWidget(reason_of_visit_label)
        reason_of_visit_vertical_layout.addWidget(self.reason_of_visit_input)
        # --------------------------------------------------------------

        notes_label = CustomLabel(name="Notes")

        self.notes_input = CustomTextEdit(border_radius=7, placeholder_text="")
        self.notes_input.setFixedWidth(400)

        notes_vertical_layout = QVBoxLayout()
        notes_vertical_layout.setContentsMargins(0, 0, 0, 0)
        notes_vertical_layout.setSpacing(10)

        notes_vertical_layout.addWidget(notes_label)
        notes_vertical_layout.addWidget(self.notes_input)

        main_vertical_layout = QVBoxLayout()
        main_vertical_layout.setSpacing(20)
        main_vertical_layout.setContentsMargins(0, 0, 0, 0)

        main_vertical_layout.addLayout(appointment_type_layout)
        main_vertical_layout.addLayout(reason_of_visit_vertical_layout)
        main_vertical_layout.addLayout(notes_vertical_layout)

        central_widget = QWidget()
        central_widget.setLayout(main_vertical_layout)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.setContentsMargins(40, 0, 20, 20)
        layout.addWidget(central_widget)

        self.setLayout(layout)
        self.setFixedHeight(500)

    def populate_appointment_types(self):
        types = self.appointment_types_controller.store.get_data()
        if types:
            for item in types:
                standard_item = QStandardItem()
                standard_item.setData(item["type_name"], Qt.ItemDataRole.DisplayRole)
                standard_item.setData(item["type_id"], Qt.ItemDataRole.UserRole)
                self.appointment_type_model.appendRow(standard_item)

    def get_appointment_specifications_data(self):
        return {
            "appointment_type": self.appointment_type_combo.currentText(),
            "reason_for_visit": self.reason_of_visit_input.toPlainText(),
            "notes": self.notes_input.toPlainText(),
        }
