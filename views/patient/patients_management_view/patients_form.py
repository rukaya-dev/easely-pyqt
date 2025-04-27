from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIntValidator
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QButtonGroup, QSizePolicy, QSpacerItem
from utils.validator import AgeIntValidator, PhoneNumberValidator, national_id_number_validator, phone_number_validator
from views.componenets.customsComponents.custom_combobox import CustomComboBox
from views.componenets.customsComponents.table.form_componenets.custom_input import CustomLineEdit
from views.componenets.customsComponents.table.form_componenets.custom_label import CustomLabel
from views.componenets.customsComponents.table.form_componenets.custom_text_edit import CustomTextEdit


class PatientForm(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.current_selected_gender = "Male"

        self.int_validator = AgeIntValidator()
        int_validator = QIntValidator(1, 200)
        self.phone_number_validator = PhoneNumberValidator()

        self.main_vertical_layout = QVBoxLayout()
        self.main_vertical_layout.setContentsMargins(0, 0, 0, 0)
        self.main_vertical_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.main_vertical_layout.setSpacing(32)

        national_id_number_label = CustomLabel(name="National ID Number")

        self.national_id_number_input = CustomLineEdit(placeholder_text="", parent=self)
        self.national_id_number_input.setValidator(national_id_number_validator)

        national_id_number_vertical_layout = QVBoxLayout()
        national_id_number_vertical_layout.setSpacing(10)

        national_id_number_vertical_layout.addWidget(national_id_number_label)
        national_id_number_vertical_layout.addWidget(self.national_id_number_input)
        # ------------------------------------------------------------------

        firstname_label = CustomLabel(name="First Name")

        self.firstname_input = CustomLineEdit(placeholder_text="", parent=self)

        patient_firstname_vertical_layout = QVBoxLayout()
        patient_firstname_vertical_layout.setSpacing(10)

        patient_firstname_vertical_layout.addWidget(firstname_label)
        patient_firstname_vertical_layout.addWidget(self.firstname_input)

        lastname_label = CustomLabel(name="Last Name")

        self.lastname_input = CustomLineEdit(placeholder_text="", parent=self)

        patient_lastname_vertical_layout = QVBoxLayout()
        patient_lastname_vertical_layout.setSpacing(10)

        patient_lastname_vertical_layout.addWidget(lastname_label)
        patient_lastname_vertical_layout.addWidget(self.lastname_input)

        first_last_name_layout = QHBoxLayout()
        first_last_name_layout.setSpacing(10)
        first_last_name_layout.setContentsMargins(0, 0, 0, 0)

        first_last_name_layout.addLayout(patient_firstname_vertical_layout)
        first_last_name_layout.addLayout(patient_lastname_vertical_layout)
        # ------------------------------------------------------------------

        # Patient Age
        age_label = CustomLabel(name="Age")

        self.age_input = CustomLineEdit(placeholder_text="23 Yrs", parent=self)
        self.age_input.setValidator(int_validator)

        self.age_unit_selection = CustomComboBox(parent=self)
        self.age_unit_selection.addItems(["years", "months", "days"])

        age_and_unit_layout = QHBoxLayout()
        age_and_unit_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        age_and_unit_layout.setContentsMargins(0, 0, 0, 0)
        age_and_unit_layout.setSpacing(10)

        age_and_unit_layout.addWidget(self.age_input)
        age_and_unit_layout.addWidget(self.age_unit_selection)

        patient_age_vertical_layout = QVBoxLayout()
        patient_age_vertical_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        patient_age_vertical_layout.setContentsMargins(0, 0, 0, 0)
        patient_age_vertical_layout.setSpacing(10)

        patient_age_vertical_layout.addWidget(age_label)
        patient_age_vertical_layout.addLayout(age_and_unit_layout)

        # -----------------------------------------------------------

        # Patient Gender
        gender_label = CustomLabel(name="Gender")

        self.male_btn = QPushButton()
        self.male_btn.setText("M")
        self.male_btn.setObjectName("Male")
        self.male_btn.setFixedSize(QSize(52, 39))
        self.male_btn.setCheckable(True)
        self.male_btn.setStyleSheet(
            "border: 1px solid #DDDDDD;font-size:16px;border-radius:3px;color:#2C2D33;")

        self.female_btn = QPushButton()
        self.female_btn.setText("F")
        self.female_btn.setObjectName("Female")
        self.female_btn.setFixedSize(QSize(52, 39))
        self.female_btn.setCheckable(True)
        self.female_btn.setStyleSheet(
            "border: 1px solid #DDDDDD;font-size:16px;border-radius:3px;color:#2C2D33;")

        self.gender_group = QButtonGroup()

        self.gender_group.addButton(self.male_btn)
        self.gender_group.addButton(self.female_btn)

        self.gender_group.setId(self.female_btn, 1)
        self.gender_group.setId(self.male_btn, 0)

        self.gender_group.buttonClicked.connect(self.change_gender_btns_style)
        self.change_gender_btns_style(self.male_btn)

        patient_gender_buttons_horizontal_layout = QHBoxLayout()
        patient_gender_buttons_horizontal_layout.setContentsMargins(0, 0, 0, 0)
        patient_gender_buttons_horizontal_layout.setSpacing(0)
        patient_gender_buttons_horizontal_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        patient_gender_buttons_horizontal_layout.addWidget(self.male_btn)
        patient_gender_buttons_horizontal_layout.addWidget(self.female_btn)

        patient_gender_vertical_layout = QVBoxLayout()
        patient_gender_vertical_layout.setContentsMargins(0, 0, 0, 0)
        patient_gender_vertical_layout.setSpacing(10)

        patient_gender_vertical_layout.addWidget(gender_label)
        patient_gender_vertical_layout.addLayout(patient_gender_buttons_horizontal_layout)

        patient_age_and_gender_layout = QHBoxLayout()
        patient_age_and_gender_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        patient_age_and_gender_layout.setContentsMargins(0, 0, 0, 0)
        patient_age_and_gender_layout.setSpacing(100)

        patient_age_and_gender_layout.addLayout(patient_age_vertical_layout)
        patient_age_and_gender_layout.addLayout(patient_gender_vertical_layout)
        # -----------------------------------------------------------

        phone_number_label = CustomLabel(name="Phone Number")

        self.phone_number_input = CustomLineEdit(placeholder_text="", parent=self)
        self.phone_number_input.setValidator(phone_number_validator)

        phone_number_vertical_layout = QVBoxLayout()
        phone_number_vertical_layout.setContentsMargins(0, 0, 0, 0)
        phone_number_vertical_layout.setSpacing(10)

        phone_number_vertical_layout.addWidget(phone_number_label)
        phone_number_vertical_layout.addWidget(self.phone_number_input)

        address_label = CustomLabel(name="Address")

        self.address_input = CustomTextEdit(border_radius=2, placeholder_text="", parent=self)

        address_vertical_layout = QVBoxLayout()
        address_vertical_layout.setContentsMargins(0, 0, 0, 0)
        address_vertical_layout.setSpacing(10)

        address_vertical_layout.addWidget(address_label)
        address_vertical_layout.addWidget(self.address_input)

        patient_clinical_data_label = CustomLabel(name="Clinical Data")

        self.select_clinical_data_combo = CustomComboBox()

        self.select_clinical_data_combo.currentIndexChanged.connect(self.setClinicalDataContent)

        self.patient_clinical_data_input = CustomTextEdit(border_radius=2, placeholder_text="", parent=self)
        self.patient_clinical_data_input.setText("No clinical data available.")

        patient_clinical_data_label_and_drop_down_horizontal_layout = QHBoxLayout()
        patient_clinical_data_label_and_drop_down_horizontal_layout.setContentsMargins(0, 0, 0, 0)
        patient_clinical_data_label_and_drop_down_horizontal_layout.setSpacing(0)

        patient_clinical_data_label_and_drop_down_horizontal_layout.addWidget(patient_clinical_data_label,
                                                                              Qt.AlignmentFlag.AlignLeft)

        patient_clinical_data_vertical_layout = QVBoxLayout()
        patient_clinical_data_vertical_layout.setContentsMargins(0, 0, 0, 0)
        patient_clinical_data_vertical_layout.setSpacing(10)

        patient_clinical_data_vertical_layout.addLayout(patient_clinical_data_label_and_drop_down_horizontal_layout)
        patient_clinical_data_vertical_layout.addWidget(self.patient_clinical_data_input)

        notes_label = CustomLabel(name="Notes")

        self.notes_input = CustomTextEdit(border_radius=2, placeholder_text="", parent=self)

        notes_vertical_layout = QVBoxLayout()
        notes_vertical_layout.setContentsMargins(0, 0, 0, 0)
        notes_vertical_layout.setSpacing(10)

        notes_vertical_layout.addWidget(notes_label)
        notes_vertical_layout.addWidget(self.notes_input)
        # -----------------------------------------------------------
        insurance_provider_label = CustomLabel(name="Insurance Provider")

        self.insurance_provider_input = CustomLineEdit(placeholder_text="", parent=self)

        insurance_provider_vertical_layout = QVBoxLayout()
        insurance_provider_vertical_layout.setContentsMargins(0, 0, 0, 0)
        insurance_provider_vertical_layout.setSpacing(10)

        insurance_provider_vertical_layout.addWidget(insurance_provider_label)
        insurance_provider_vertical_layout.addWidget(self.insurance_provider_input)
        # -----------------------------------------------------------
        insurance_policy_number_label = CustomLabel(name="Insurance Policy Number")

        self.insurance_policy_number_input = CustomLineEdit(placeholder_text="", parent=self)

        insurance_policy_number_vertical_layout = QVBoxLayout()
        insurance_policy_number_vertical_layout.setContentsMargins(0, 0, 0, 0)
        insurance_policy_number_vertical_layout.setSpacing(10)

        insurance_policy_number_vertical_layout.addWidget(insurance_policy_number_label)
        insurance_policy_number_vertical_layout.addWidget(self.insurance_policy_number_input)
        # -----------------------------------------------------------
        coverage_percentage_label = CustomLabel(name="Coverage Percentage %")

        self.coverage_percentage_input = CustomLineEdit(placeholder_text="", parent=self)

        coverage_percentage_vertical_layout = QVBoxLayout()
        coverage_percentage_vertical_layout.setContentsMargins(0, 0, 0, 0)
        coverage_percentage_vertical_layout.setSpacing(10)

        coverage_percentage_vertical_layout.addWidget(coverage_percentage_label)
        coverage_percentage_vertical_layout.addWidget(self.coverage_percentage_input)
        # -----------------------------------------------------------

        central_widget = QWidget()
        central_widget.setLayout(self.main_vertical_layout)

        self.main_vertical_layout.addLayout(national_id_number_vertical_layout)
        self.main_vertical_layout.addLayout(first_last_name_layout)
        self.main_vertical_layout.addLayout(patient_age_and_gender_layout)
        self.main_vertical_layout.addLayout(phone_number_vertical_layout)
        self.main_vertical_layout.addLayout(address_vertical_layout)
        self.main_vertical_layout.addLayout(insurance_provider_vertical_layout)
        self.main_vertical_layout.addLayout(insurance_policy_number_vertical_layout)
        self.main_vertical_layout.addLayout(coverage_percentage_vertical_layout)
        self.main_vertical_layout.addLayout(patient_clinical_data_vertical_layout)
        self.main_vertical_layout.addLayout(notes_vertical_layout)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(central_widget)

        self.setLayout(layout)

        self.setMinimumWidth(500)
        self.setMaximumWidth(800)

    def set_current_selected_gender(self, gender):
        self.current_selected_gender = gender

    def change_gender_btns_style(self, button):
        button.setStyleSheet(
            "font-size:16px;border-radius:0;border:1px solid #0DBAB5;color:white;background-color:#2563EB;")

        self.set_current_selected_gender(button.objectName())
        print("current_selected_gender", self.current_selected_gender)

        for btn in self.gender_group.buttons():
            if btn != button:
                btn.setStyleSheet("border: 1px solid #DDDDDD;font-size:16px;border-radius:3px;color:#2C2D33")

    def setClinicalDataContent(self):
        clinical_data_content = self.select_clinical_data_combo.getClinicalDataContent()
        self.patient_clinical_data_input.setPlainText(clinical_data_content)
