import asyncio
import datetime

from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QSize, pyqtSlot, pyqtSignal
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget, QDialog, QSpacerItem, QSizePolicy, \
    QLabel, QPushButton, QMessageBox
from qasync import asyncSlot

from loggers.logger_configs import set_up_logger
from services.supabase.controllers.appointment.apponitment_controller import AppointmentController
from services.supabase.controllers.patient.patient_controller import PatientController
from services.supabase.controllers.staff.doctor.doctor_service_relation_controller import \
    DoctorServiceRelationController
from signals import SignalRepositorySingleton
from views.appointement.appointment_details_form import AppointmentDetailsForm
from views.appointement.appointment_review_form import AppointmentReviewForm
from views.componenets.customsComponents.buttons.button_with_loader import ButtonWithLoader
from views.componenets.customsComponents.custom_scroll_area import CustomScrollArea
from views.componenets.customsComponents.loaders.internal_loader import InternalLoader

logger = set_up_logger('main.appointment.appointment_main_view_dialog')


def disable_button_style(button: QPushButton):
    button.setStyleSheet("""
    QPushButton {
        border:0;
        border-radius:3px;
        font-size:13pt;
        background-color:#ebebeb;
        color:#a4a4a4;
    }
    """)


def enable_button_style(button: QPushButton):
    button.setStyleSheet("""
    QPushButton {
        border:0;
        border-radius:3px;
        font-size:13pt;
        background-color:#2563EB;
        color:#F5F5F5;
    }
    QPushButton:pressed {
        border:0;
        border-radius:3px;
        font-size:13pt;
        color:#F5F5F5;
        padding-top: 2px;
        padding-left: 2px;
    }

    """)


class RescheduleAppointmentDialog(QDialog):
    def __init__(self, fetched_data, appointment_controller, appointment_types_controller, service_controller, parent=None):
        super().__init__(parent)

        self.patient_data = None
        self.fetched_data = fetched_data
        self.patient_id = fetched_data["patient_id"]
        self.appointment_id = fetched_data["appointment_id"]

        self.setStyleSheet("background-color:white;")
        self.tab_buttons = None
        self.parent = parent

        self.central_widget = None
        self.data = []

        # Signals
        self.signals = SignalRepositorySingleton.instance()

        # API model
        self.appointment_controller = appointment_controller
        self.appointment_types_controller = appointment_types_controller
        self.service_controller = service_controller

        self.patient_controller = PatientController()

        self.stacked_content_widget = QStackedWidget()
        self.stacked_content_widget.setContentsMargins(0, 0, 0, 0)

        appointment_header_widget = AppointmentHeaderWidget(parent=self)

        scroll_area = CustomScrollArea(self)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setWidget(self.stacked_content_widget)

        self.appointment_details_form = AppointmentDetailsForm(service_controller=self.service_controller)
        self.appointment_details_form.toggleNextButtonStatusSignal.connect(self.activate_next_button)

        self.appointment_review_form = AppointmentReviewForm(appointment_controller=self.appointment_controller,
                                                             appointment_types_controller=self.appointment_types_controller,
                                                             service_controller=self.service_controller)
        self.appointment_review_form.appointment_specification_form.hide()

        self.back_btn = ButtonWithLoader("Back", size=QSize(95, 34))
        self.back_btn.clicked.connect(lambda: self.set_main_content(self.appointment_details_form))

        self.next_btn = ButtonWithLoader("Next", size=QSize(95, 34))
        self.next_btn.setDisabled(True)
        disable_button_style(self.next_btn)
        self.next_btn.clicked.connect(lambda: self.set_main_content(self.appointment_review_form))

        self.save_btn = ButtonWithLoader("Save", size=QSize(95, 34))
        self.save_btn.setDisabled(True)
        self.save_btn.clicked.connect(self.re_schedule_appointment)

        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)
        controls_layout.setContentsMargins(20, 20, 20, 20)
        controls_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        controls_layout.addWidget(self.back_btn)
        controls_layout.addWidget(self.next_btn)
        controls_layout.addWidget(self.save_btn)

        main_h_layout = QHBoxLayout()
        main_h_layout.setContentsMargins(0, 0, 0, 0)

        main_h_layout.addWidget(scroll_area)

        self.main_v_layout = QVBoxLayout()
        self.main_v_layout.setSpacing(0)
        self.main_v_layout.setContentsMargins(0, 0, 0, 0)
        self.main_v_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.main_v_layout.addWidget(appointment_header_widget)
        self.main_v_layout.addLayout(main_h_layout)
        self.main_v_layout.addLayout(controls_layout)

        self.set_main_content(self.appointment_details_form)

        # Set Layouts
        self.setLayout(self.main_v_layout)
        self.setFixedSize(1000, 700)

        asyncio.create_task(self.get_patient_data())

    def set_main_content(self, content_widget):
        self.stacked_content_widget.addWidget(content_widget)
        self.stacked_content_widget.setCurrentWidget(content_widget)

        if content_widget == self.appointment_details_form:
            self.appointment_details_form.set_appointment_details_data(self.fetched_data)
            self.next_btn.show()
            self.back_btn.hide()
            self.save_btn.hide()

        elif content_widget == self.appointment_review_form:
            self.appointment_review_form.set_data(self.patient_data, self.appointment_details_form.get_appointment_details_data())
            self.next_btn.hide()
            self.back_btn.show()
            self.save_btn.show()

            self.back_btn.setEnabled(True)
            self.save_btn.setEnabled(True)

    async def get_patient_data(self):
        self.patient_data = await self.patient_controller.get_patient_by_id(patient_id=self.patient_id)
        if not self.patient_data:
            msg = QMessageBox()
            msg.setText('Could not get patient data.')
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setDetailedText("error occurred while creating, please contact your service provider.")
            msg.exec()
            self.close()

    @pyqtSlot(bool)
    def activate_next_button(self, status):
        if not status or not self.appointment_details_form.get_appointment_details_data():
            self.next_btn.setDisabled(True)
            disable_button_style(self.next_btn)
        else:
            self.next_btn.setDisabled(False)
            enable_button_style(self.next_btn)

    @pyqtSlot()
    @asyncSlot()
    async def re_schedule_appointment(self):
        data = self.get_appointment_data()
        if data:
            data.update({"appointment_status": "re-scheduled",
                         "re_scheduled_date": self.fetched_data["re_scheduled_date"],
                         "re_scheduled_time": self.fetched_data["re_scheduled_time"],
                         "updated_at": datetime.datetime.now().isoformat()})
            self.save_btn.start()
            is_exits = await self.appointment_controller.check_if_appointment_exist(data)
            if is_exits:
                self.save_btn.stop()
                msg = QMessageBox()
                msg.setText('appointment already taken.')
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.exec()
            else:
                res = await self.appointment_controller. update_appointment(
                    appointment_id=self.appointment_id, data=data, patient_data=self.patient_data)
                if not res:
                    self.save_btn.stop()
                    msg = QMessageBox()
                    msg.setText('Could not update appointment')
                    msg.setIcon(QMessageBox.Icon.Critical)
                    msg.setDetailedText("error occurred while creating, please contact your service provider.")
                    msg.exec()
                else:
                    self.signals.globalAppointmentUpdateTableViewSignal.emit()
                    self.save_btn.stop()
                    self.close()
                    msg = QMessageBox()
                    msg.setText('Appointment Successfully Updated.')
                    msg.setIcon(QMessageBox.Icon.Information)
                    msg.exec()

    def get_appointment_data(self):
        appointment_details_data = self.appointment_details_form.get_appointment_details_data()
        appointment_details_data.pop('service_name')
        appointment_details_data.pop('doctor_name')
        appointment_details_data.pop('doctor_service_relation_data')
        appointment_specifications_data = self.appointment_review_form.appointment_specification_form.get_appointment_specifications_data()

        data = {
            "patient_id": self.patient_id,
            "appointment_date": appointment_details_data["appointment_date"],
            "appointment_time": appointment_details_data["appointment_time"],
        }
        data.update(appointment_details_data)
        data.update(appointment_specifications_data)
        return data


class AppointmentHeaderWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # Signals
        self.signals = SignalRepositorySingleton.instance()
        self.signals.appointmentHeaderInternalLoaderSignal.connect(self.handle_internal_loader_status)

        calendar_icon = QPixmap(":/resources/icons/re_schedule.svg")
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

        make_an_appointment_label = QLabel("Re-Schedule an Appointment")
        make_an_appointment_label.setStyleSheet("border:0;background-color:transparent;color:black;")

        make_an_appointment_font = make_an_appointment_label.font()
        make_an_appointment_font.setWeight(make_an_appointment_font.Weight.Medium)
        make_an_appointment_font.setPointSize(14)

        make_an_appointment_label.setFont(make_an_appointment_font)

        fill_in_data_label = QLabel("Fill in the data below to update an appointment")
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
