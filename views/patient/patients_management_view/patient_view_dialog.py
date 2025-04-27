from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QDialog
from signals import SignalRepositorySingleton
from views.componenets.customsComponents.custom_scroll_area import CustomScrollArea
from views.patient.history_management_view.patient_history_widget import PatientHistoryWidget
from views.patient.patients_management_view.patients_form import PatientForm


class PatientViewDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setStyleSheet("background-color:#f3f4f6;")

        self.parent = parent
        self.is_patient_data_widget = None
        self.history_widget = None
        self.form_widget = None

        # Signals
        self.signals = SignalRepositorySingleton.instance()

        central_widget = QWidget(self)
        central_widget.setObjectName("central_widget")

        main_vertical_layout = QVBoxLayout()
        main_vertical_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_vertical_layout.setContentsMargins(0, 0, 0, 0)

        self.main_patient_data_horizontal_layout = QHBoxLayout()
        self.main_patient_data_horizontal_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.main_patient_data_horizontal_layout.setSpacing(50)
        self.main_patient_data_horizontal_layout.setContentsMargins(0, 0, 0, 0)

        self.form_widget = PatientForm(parent=self)
        self.history_widget = PatientHistoryWidget(data=None, parent=self)

        self.main_patient_data_horizontal_layout.addWidget(self.form_widget)
        self.main_patient_data_horizontal_layout.addWidget(self.history_widget)

        main_vertical_layout.addLayout(self.main_patient_data_horizontal_layout)

        central_widget.setLayout(main_vertical_layout)

        scroll_area = CustomScrollArea(self)
        scroll_area.setWidget(central_widget)

        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.setContentsMargins(30, 30, 10, 30)

        self.layout.addWidget(scroll_area)
        self.setLayout(self.layout)

        self.setMinimumWidth(1366)
        self.setMinimumHeight(768)

    def render_patient_history(self, data):
        self.history_widget = PatientHistoryWidget(data=data, parent=self)
        self.main_patient_data_horizontal_layout.addWidget(self.history_widget)

