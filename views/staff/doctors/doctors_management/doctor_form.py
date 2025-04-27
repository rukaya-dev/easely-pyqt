from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout

from utils.validator import AgeIntValidator, PhoneNumberValidator, phone_number_validator
from views.componenets.customsComponents.table.form_componenets.custom_input import CustomLineEdit
from views.componenets.customsComponents.table.form_componenets.custom_label import CustomLabel
from views.componenets.customsComponents.table.form_componenets.custom_text_edit import CustomTextEdit


class DoctorForm(QWidget):
    newContentIsAddedSignal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.int_validator = AgeIntValidator()
        self.phone_number_validator = PhoneNumberValidator()

        # First name
        first_name_label = CustomLabel(name="First name")

        self.first_name_input = CustomLineEdit(placeholder_text="Jane", parent=self)

        doctor_first_name_vertical_layout = QVBoxLayout()
        doctor_first_name_vertical_layout.setSpacing(10)

        doctor_first_name_vertical_layout.addWidget(first_name_label)
        doctor_first_name_vertical_layout.addWidget(self.first_name_input)

        # Last name
        last_name_label = CustomLabel(name="Last name")

        self.last_name_input = CustomLineEdit(placeholder_text="Smith", parent=self)

        doctor_last_name_vertical_layout = QVBoxLayout()
        doctor_last_name_vertical_layout.setSpacing(10)

        doctor_last_name_vertical_layout.addWidget(last_name_label)
        doctor_last_name_vertical_layout.addWidget(self.last_name_input)

        first_last_name_layout = QHBoxLayout()
        first_last_name_layout.setSpacing(10)

        first_last_name_layout.addLayout(doctor_first_name_vertical_layout)
        first_last_name_layout.addLayout(doctor_last_name_vertical_layout)

        # doctor Specialty
        self.specialty = CustomLabel(name="Specialty")

        self.specialty_input = CustomLineEdit(placeholder_text="Neurologist", parent=self)

        specialty_vertical_layout = QVBoxLayout()
        specialty_vertical_layout.setContentsMargins(0, 0, 0, 0)
        specialty_vertical_layout.setSpacing(10)

        specialty_vertical_layout.addWidget(self.specialty)
        specialty_vertical_layout.addWidget(self.specialty_input)
        # -----------------------------------------------------------

        qualifications_label = CustomLabel(name="Qualifications")

        self.qualifications_input = CustomTextEdit(border_radius=2,placeholder_text="", parent=self)

        qualifications_vertical_layout = QVBoxLayout()
        qualifications_vertical_layout.setContentsMargins(0, 0, 0, 0)
        qualifications_vertical_layout.setSpacing(10)

        qualifications_vertical_layout.addWidget(qualifications_label)
        qualifications_vertical_layout.addWidget(self.qualifications_input)
        # -----------------------------------------------------------
        # doctor Specialty
        self.email = CustomLabel(name="Email")

        self.email_input = CustomLineEdit(placeholder_text="drjanesmith@gmail.com", parent=self)

        email_vertical_layout = QVBoxLayout()
        email_vertical_layout.setContentsMargins(0, 0, 0, 0)
        email_vertical_layout.setSpacing(10)

        email_vertical_layout.addWidget(self.email)
        email_vertical_layout.addWidget(self.email_input)
        # -----------------------------------------------------------

        phone_number_label = CustomLabel(name="Phone Number")

        self.phone_number_input = CustomLineEdit(placeholder_text="(217) 555-1234", parent=self)
        self.phone_number_input.setValidator(phone_number_validator)

        phone_number_vertical_layout = QVBoxLayout()
        phone_number_vertical_layout.setContentsMargins(0, 0, 0, 0)
        phone_number_vertical_layout.setSpacing(10)

        phone_number_vertical_layout.addWidget(phone_number_label)
        phone_number_vertical_layout.addWidget(self.phone_number_input)

        phon_number_email_layout = QHBoxLayout()
        phon_number_email_layout.setSpacing(10)

        phon_number_email_layout.addLayout(email_vertical_layout)
        phon_number_email_layout.addLayout(phone_number_vertical_layout)

        address_label = CustomLabel(name="Address")

        self.address_input = CustomTextEdit(border_radius=2,placeholder_text="", parent=self)

        address_vertical_layout = QVBoxLayout()
        address_vertical_layout.setContentsMargins(0, 0, 0, 0)
        address_vertical_layout.setSpacing(10)

        address_vertical_layout.addWidget(address_label)
        address_vertical_layout.addWidget(self.address_input)
        # -----------------------------------------------------

        # doctor Specialty
        self.room_number = CustomLabel(name="Room number")

        self.room_number_input = CustomLineEdit(placeholder_text="1001", parent=self)

        room_number_vertical_layout = QVBoxLayout()
        room_number_vertical_layout.setContentsMargins(0, 0, 0, 0)
        room_number_vertical_layout.setSpacing(10)

        room_number_vertical_layout.addWidget(self.room_number)
        room_number_vertical_layout.addWidget(self.room_number_input)
        # -----------------------------------------------------------

        self.main_vertical_layout = QVBoxLayout()
        self.main_vertical_layout.setContentsMargins(0, 0, 0, 0)
        self.main_vertical_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.main_vertical_layout.setSpacing(32)

        self.main_vertical_layout.addLayout(first_last_name_layout)
        self.main_vertical_layout.addLayout(phon_number_email_layout)
        self.main_vertical_layout.addLayout(specialty_vertical_layout)
        self.main_vertical_layout.addLayout(qualifications_vertical_layout)
        self.main_vertical_layout.addLayout(address_vertical_layout)
        self.main_vertical_layout.addLayout(room_number_vertical_layout)

        central_widget = QWidget()
        central_widget.setLayout(self.main_vertical_layout)

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(central_widget)

        self.setLayout(layout)
