from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout

from services.supabase.controllers.staff.doctor.doctor_controller import DoctorController
from signals import SignalRepositorySingleton
from views.componenets.customsComponents.table.form_componenets.custom_input import CustomLineEdit
from views.componenets.customsComponents.table.form_componenets.custom_label import CustomLabel
from views.componenets.customsComponents.table.form_componenets.custom_text_edit import CustomTextEdit


class ServiceForm(QWidget):
    newContentIsAddedSignal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Signals
        self.signals = SignalRepositorySingleton.instance()

        self.doctor_controller = DoctorController()

        # Name
        name_label = CustomLabel(name="Name")

        self.name_input = CustomLineEdit(placeholder_text="Abdominal Ultrasound", parent=self)

        service_name_vertical_layout = QVBoxLayout()
        service_name_vertical_layout.setSpacing(10)

        service_name_vertical_layout.addWidget(name_label)
        service_name_vertical_layout.addWidget(self.name_input)

        description_label = CustomLabel(name="Description")

        self.description_input = CustomTextEdit(border_radius=2,placeholder_text="", parent=self)

        service_description_vertical_layout = QVBoxLayout()
        service_description_vertical_layout.setSpacing(10)

        service_description_vertical_layout.addWidget(description_label)
        service_description_vertical_layout.addWidget(self.description_input)

        self.main_vertical_layout = QVBoxLayout()
        self.main_vertical_layout.setContentsMargins(0, 0, 0, 0)
        self.main_vertical_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.main_vertical_layout.setSpacing(32)

        self.main_vertical_layout.addLayout(service_name_vertical_layout)
        self.main_vertical_layout.addLayout(service_description_vertical_layout)

        central_widget = QWidget()
        central_widget.setLayout(self.main_vertical_layout)

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(central_widget)

        self.setLayout(layout)

