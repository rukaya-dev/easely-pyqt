from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout, QDialog

from views.componenets.customsComponents.custom_line_edit_with_icon import CustomLineEditWithIcon
from views.componenets.customsComponents.custom_rounded_line_edit import CustomRoundedLineEdit
from views.componenets.customsComponents.custom_scroll_area import CustomScrollArea
from views.componenets.customsComponents.table.form_componenets.custom_label import CustomLabel
from views.componenets.customsComponents.table.form_componenets.custom_text_edit import CustomTextEdit
from views.componenets.customsComponents.table.save_and_cancel_buttons import SaveAndCancelButtonsWithLoader


class AppointmentForm(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.clock_icon_path = ":/resources/icons/clock.svg"
        self.calendar_icon_path = ":/resources/icons/calendar.svg"

        service_label = CustomLabel(name="Service")

        self.service_input = CustomRoundedLineEdit(placeholder_text="")

        service_layout = QVBoxLayout()
        service_layout.setContentsMargins(0, 0, 0, 0)
        service_layout.setSpacing(10)

        service_layout.addWidget(service_label)
        service_layout.addWidget(self.service_input)
        # --------------------------------------------------------------
        appointment_status_label = CustomLabel(name="Appointment Status")

        self.appointment_status_input = CustomRoundedLineEdit(placeholder_text="")
        self.appointment_status_input.setFixedHeight(40)

        appointment_status_vertical_layout = QVBoxLayout()
        appointment_status_vertical_layout.setContentsMargins(0, 0, 0, 0)
        appointment_status_vertical_layout.setSpacing(10)

        appointment_status_vertical_layout.addWidget(appointment_status_label)
        appointment_status_vertical_layout.addWidget(self.appointment_status_input)

        appointment_type_label = CustomLabel(name="Appointment Type")

        self.appointment_type_input = CustomRoundedLineEdit(placeholder_text="")
        self.appointment_type_input.setFixedHeight(40)

        appointment_type_vertical_layout = QVBoxLayout()
        appointment_type_vertical_layout.setContentsMargins(0, 0, 0, 0)
        appointment_type_vertical_layout.setSpacing(10)

        appointment_type_vertical_layout.addWidget(appointment_type_label)
        appointment_type_vertical_layout.addWidget(self.appointment_type_input)

        appointment_status_and_type_horizontal_layout = QHBoxLayout()
        appointment_status_and_type_horizontal_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        appointment_status_and_type_horizontal_layout.setContentsMargins(0, 0, 0, 0)
        appointment_status_and_type_horizontal_layout.setSpacing(10)

        appointment_status_and_type_horizontal_layout.addLayout(appointment_status_vertical_layout)
        appointment_status_and_type_horizontal_layout.addLayout(appointment_type_vertical_layout)
        # --------------------------------------------------------------
        reason_of_visit_label = CustomLabel(name="Reason of visit")

        self.reason_of_visit_input = CustomTextEdit(border_radius=7, placeholder_text="", parent=self)

        reason_of_visit_vertical_layout = QVBoxLayout()
        reason_of_visit_vertical_layout.setContentsMargins(0, 0, 0, 0)
        reason_of_visit_vertical_layout.setSpacing(10)

        reason_of_visit_vertical_layout.addWidget(reason_of_visit_label)
        reason_of_visit_vertical_layout.addWidget(self.reason_of_visit_input)

        notes_label = CustomLabel(name="Notes")

        self.notes_input = CustomTextEdit(border_radius=7, placeholder_text="", parent=self)

        notes_vertical_layout = QVBoxLayout()
        notes_vertical_layout.setContentsMargins(0, 0, 0, 0)
        notes_vertical_layout.setSpacing(10)

        notes_vertical_layout.addWidget(notes_label)
        notes_vertical_layout.addWidget(self.notes_input)

        reason_of_visit_and_notes_horizontal_layout = QHBoxLayout()
        reason_of_visit_and_notes_horizontal_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        reason_of_visit_and_notes_horizontal_layout.setContentsMargins(0, 0, 0, 0)
        reason_of_visit_and_notes_horizontal_layout.setSpacing(10)

        reason_of_visit_and_notes_horizontal_layout.addLayout(reason_of_visit_vertical_layout)
        reason_of_visit_and_notes_horizontal_layout.addLayout(notes_vertical_layout)
        # -------------------------------------------------------------
        check_in_label = CustomLabel(name="Check in Time")

        self.check_in_input = CustomLineEditWithIcon(icon_path=self.clock_icon_path, placeholder_text="")

        check_in_label_vertical_layout = QVBoxLayout()
        check_in_label_vertical_layout.setContentsMargins(0, 0, 0, 0)
        check_in_label_vertical_layout.setSpacing(10)

        check_in_label_vertical_layout.addWidget(check_in_label)
        check_in_label_vertical_layout.addWidget(self.check_in_input)

        check_out_label = CustomLabel(name="Check out Time")

        self.check_out_input = CustomLineEditWithIcon(icon_path=self.clock_icon_path, placeholder_text="")

        check_out_vertical_layout = QVBoxLayout()
        check_out_vertical_layout.setContentsMargins(0, 0, 0, 0)
        check_out_vertical_layout.setSpacing(10)

        check_out_vertical_layout.addWidget(check_out_label)
        check_out_vertical_layout.addWidget(self.check_out_input)

        check_in_out_time_horizontal_layout = QHBoxLayout()
        check_in_out_time_horizontal_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        check_in_out_time_horizontal_layout.setContentsMargins(0, 0, 0, 0)
        check_in_out_time_horizontal_layout.setSpacing(10)

        check_in_out_time_horizontal_layout.addLayout(check_in_label_vertical_layout)
        check_in_out_time_horizontal_layout.addLayout(check_out_vertical_layout)
        # ------------------------------------------------------------------------
        self.re_scheduled_dates_and_time_label = CustomLabel(name="Re-Scheduled Date & Time")

        self.re_scheduled_date_input = CustomLineEditWithIcon(icon_path=self.calendar_icon_path,
                                                              placeholder_text="")
        self.re_scheduled_date_input.container_widget.setFixedHeight(40)

        self.re_scheduled_time_input = CustomLineEditWithIcon(icon_path=self.clock_icon_path,
                                                              placeholder_text="")

        re_scheduled_dates_and_time_horizontal_layout = QHBoxLayout()
        re_scheduled_dates_and_time_horizontal_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        re_scheduled_dates_and_time_horizontal_layout.setContentsMargins(0, 0, 0, 0)
        re_scheduled_dates_and_time_horizontal_layout.setSpacing(10)

        re_scheduled_dates_and_time_horizontal_layout.addWidget(self.re_scheduled_date_input)
        re_scheduled_dates_and_time_horizontal_layout.addWidget(self.re_scheduled_time_input)

        re_scheduled_dates_and_time_vertical_layout = QVBoxLayout()
        re_scheduled_dates_and_time_vertical_layout.setContentsMargins(0, 0, 0, 0)
        re_scheduled_dates_and_time_vertical_layout.setSpacing(10)

        re_scheduled_dates_and_time_vertical_layout.addWidget(self.re_scheduled_dates_and_time_label)
        re_scheduled_dates_and_time_vertical_layout.addLayout(re_scheduled_dates_and_time_horizontal_layout)
        # ------------------------------------------------------------------------
        self.cancellation_dates_and_time_label = CustomLabel(name="Cancellation Date & Time")

        self.cancellation_date_input = CustomLineEditWithIcon(icon_path=self.calendar_icon_path,
                                                              placeholder_text="")
        self.cancellation_date_input.container_widget.setFixedHeight(40)

        self.cancellation_time_input = CustomLineEditWithIcon(icon_path=self.clock_icon_path,
                                                              placeholder_text="")

        cancellation_dates_and_time_horizontal_layout = QHBoxLayout()
        cancellation_dates_and_time_horizontal_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        cancellation_dates_and_time_horizontal_layout.setContentsMargins(0, 0, 0, 0)
        re_scheduled_dates_and_time_horizontal_layout.setSpacing(10)

        cancellation_dates_and_time_horizontal_layout.addWidget(self.cancellation_date_input)
        cancellation_dates_and_time_horizontal_layout.addWidget(self.cancellation_time_input)

        cancellation_dates_and_time_vertical_layout = QVBoxLayout()
        cancellation_dates_and_time_vertical_layout.setContentsMargins(0, 0, 0, 0)
        cancellation_dates_and_time_vertical_layout.setSpacing(10)

        cancellation_dates_and_time_vertical_layout.addWidget(self.cancellation_dates_and_time_label)
        cancellation_dates_and_time_vertical_layout.addLayout(cancellation_dates_and_time_horizontal_layout)
        # ------------------------------------------------------------------------

        payment_status_label = CustomLabel(name="Payment Status")

        self.payment_status_input = CustomRoundedLineEdit(placeholder_text="")

        payment_status_vertical_layout = QVBoxLayout()
        payment_status_vertical_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        payment_status_vertical_layout.setContentsMargins(0, 0, 0, 0)
        payment_status_vertical_layout.setSpacing(10)

        payment_status_vertical_layout.addWidget(payment_status_label)
        payment_status_vertical_layout.addWidget(self.payment_status_input)
        # --------------------------------------------------------------

        doctor_label = CustomLabel(name="Doctor")

        self.doctor_input = CustomRoundedLineEdit(placeholder_text="")

        doctor_vertical_layout = QVBoxLayout()
        doctor_vertical_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        doctor_vertical_layout.setContentsMargins(0, 0, 0, 0)
        doctor_vertical_layout.setSpacing(10)

        doctor_vertical_layout.addWidget(doctor_label)
        doctor_vertical_layout.addWidget(self.doctor_input)
        # --------------------------------------------------------------
        dates_and_time_label = CustomLabel(name="Appointment Date & Time")

        self.date_input = CustomLineEditWithIcon(icon_path=self.calendar_icon_path, placeholder_text="")
        self.date_input.container_widget.setFixedHeight(40)

        self.time_input = CustomLineEditWithIcon(icon_path=self.clock_icon_path, placeholder_text="")


        dates_and_time_horizontal_layout = QHBoxLayout()
        dates_and_time_horizontal_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        dates_and_time_horizontal_layout.setContentsMargins(0, 0, 0, 0)
        dates_and_time_horizontal_layout.setSpacing(10)

        dates_and_time_horizontal_layout.addWidget(self.date_input)
        dates_and_time_horizontal_layout.addWidget(self.time_input)

        dates_and_time_vertical_layout = QVBoxLayout()
        dates_and_time_vertical_layout.setContentsMargins(0, 0, 0, 0)
        dates_and_time_vertical_layout.setSpacing(10)

        dates_and_time_vertical_layout.addWidget(dates_and_time_label)
        dates_and_time_vertical_layout.addLayout(dates_and_time_horizontal_layout)
        # ------------------------------------------------------------------------
        doctor_label = CustomLabel(name="Doctor")

        self.doctor_input = CustomRoundedLineEdit(placeholder_text="")

        doctor_vertical_layout = QVBoxLayout()
        doctor_vertical_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        doctor_vertical_layout.setContentsMargins(0, 0, 0, 0)
        doctor_vertical_layout.setSpacing(10)

        doctor_vertical_layout.addWidget(doctor_label)
        doctor_vertical_layout.addWidget(self.doctor_input)
        # # --------------------------------------------------------------
        cost_and_duration_label = CustomLabel(name="Cost & Duration")

        self.cost_input = CustomLineEditWithIcon(icon_path=":/resources/icons/dollar.svg", placeholder_text="")
        self.cost_input.container_widget.setFixedHeight(40)

        self.duration_input = CustomRoundedLineEdit(placeholder_text="")

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
        # -------------------------------------------------------------
        create_at_label = CustomLabel(name="Created At")

        self.created_at_input = CustomLineEditWithIcon(icon_path=self.calendar_icon_path, placeholder_text="")

        created_at_label_vertical_layout = QVBoxLayout()
        created_at_label_vertical_layout.setContentsMargins(0, 0, 0, 0)
        created_at_label_vertical_layout.setSpacing(10)

        created_at_label_vertical_layout.addWidget(create_at_label)
        created_at_label_vertical_layout.addWidget(self.created_at_input)

        updated_at_label = CustomLabel(name="Updated At")

        self.updated_at_input = CustomLineEditWithIcon(icon_path=self.calendar_icon_path, placeholder_text="")

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

        wrapper_widget = QWidget()

        scroll_area = CustomScrollArea(self)
        scroll_area.setContentsMargins(20, 0, 20, 0)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setWidget(wrapper_widget)

        main_vertical_layout = QVBoxLayout(wrapper_widget)
        main_vertical_layout.setSpacing(30)
        main_vertical_layout.setContentsMargins(0, 0, 0, 0)

        main_vertical_layout.addLayout(patient_national_id_number_vertical_layout)
        main_vertical_layout.addLayout(patient_first_last_name_and_age_horizontal_layout)
        main_vertical_layout.addLayout(doctor_vertical_layout)
        main_vertical_layout.addLayout(service_layout)
        main_vertical_layout.addLayout(dates_and_time_vertical_layout)
        main_vertical_layout.addLayout(cost_and_duration_vertical_layout)
        main_vertical_layout.addLayout(check_in_out_time_horizontal_layout)
        main_vertical_layout.addLayout(appointment_status_and_type_horizontal_layout)
        main_vertical_layout.addLayout(re_scheduled_dates_and_time_vertical_layout)
        main_vertical_layout.addLayout(cancellation_dates_and_time_vertical_layout)
        main_vertical_layout.addLayout(reason_of_visit_and_notes_horizontal_layout)
        main_vertical_layout.addLayout(payment_status_vertical_layout)
        main_vertical_layout.addLayout(created_updated_at_horizontal_layout)

        self.patient_national_id_number_input.line_edit.setReadOnly(True)
        self.patient_first_name_input.setReadOnly(True)
        self.patient_lastname_input.setReadOnly(True)
        self.doctor_input.setReadOnly(True)
        self.service_input.setReadOnly(True)
        self.date_input.line_edit.setReadOnly(True)
        self.time_input.line_edit.setReadOnly(True)
        self.cost_input.line_edit.setReadOnly(True)
        self.duration_input.setReadOnly(True)
        self.check_in_input.line_edit.setReadOnly(True)
        self.check_out_input.line_edit.setReadOnly(True)
        self.appointment_status_input.setReadOnly(True)
        self.appointment_type_input.setReadOnly(True)
        self.re_scheduled_date_input.line_edit.setReadOnly(True)
        self.re_scheduled_time_input.line_edit.setReadOnly(True)
        self.cancellation_date_input.line_edit.setReadOnly(True)
        self.cancellation_time_input.line_edit.setReadOnly(True)
        self.reason_of_visit_input.setDisabled(True)
        self.notes_input.setReadOnly(True)
        self.payment_status_input.setReadOnly(True)
        self.created_at_input.line_edit.setReadOnly(True)
        self.updated_at_input.line_edit.setReadOnly(True)

        self.toggle_reschedule_show_hide_status(False)
        self.toggle_cancelled_show_hide_status(False)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(wrapper_widget)

        self.setLayout(layout)

    def toggle_reschedule_show_hide_status(self, status):
        self.re_scheduled_dates_and_time_label.setVisible(status)
        self.re_scheduled_date_input.setVisible(status)
        self.re_scheduled_time_input.setVisible(status)

    def toggle_cancelled_show_hide_status(self, status):
        self.cancellation_dates_and_time_label.setVisible(status)
        self.cancellation_date_input.setVisible(status)
        self.cancellation_time_input.setVisible(status)


class AppointmentViewDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setStyleSheet("background-color:#F9FBFC;")

        self.parent = parent

        central_widget = QWidget(self)
        central_widget.setObjectName("central_widget")

        main_patient_data_vertical_layout = QVBoxLayout()
        main_patient_data_vertical_layout.setContentsMargins(0, 0, 0, 0)

        self.form_widget = AppointmentForm(parent=self)

        self.save_and_cancel_btns = SaveAndCancelButtonsWithLoader(text="Save")
        self.save_and_cancel_btns.cancel_btn.clicked.connect(self.close)

        self.save_and_cancel_btns.save_btn.hide()

        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)
        controls_layout.setContentsMargins(20, 20, 20, 20)
        controls_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        controls_layout.addWidget(self.save_and_cancel_btns)

        main_patient_data_vertical_layout.addWidget(self.form_widget)

        main_vertical_layout = QHBoxLayout()


        main_vertical_layout.addLayout(main_patient_data_vertical_layout, 1)

        central_widget.setLayout(main_vertical_layout)

        scroll_area = CustomScrollArea(self)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setWidget(central_widget)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 5, 20)
        layout.addWidget(scroll_area)
        layout.addLayout(controls_layout)

        self.setLayout(layout)
        self.setMinimumWidth(700)
        self.setMinimumHeight(600)
