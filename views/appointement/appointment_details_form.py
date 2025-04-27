from datetime import datetime
from PyQt6.QtCore import pyqtSignal, QDate, QRect, QPoint
from PyQt6.QtGui import QStandardItem, QStandardItemModel, QPen
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QButtonGroup, \
    QAbstractButton, QMessageBox, QStackedWidget
from qasync import asyncSlot

from services.supabase.controllers.appointment.apponitment_controller import AppointmentController
from services.supabase.controllers.staff.doctor.doctor_schedule_controller import DoctorScheduleController
from services.supabase.controllers.staff.doctor.doctor_service_relation_controller import \
    DoctorServiceRelationController
from signals import SignalRepositorySingleton
from views.componenets.customsComponents.custom_combobox import CustomComboBox
from views.componenets.customsComponents.custom_scroll_area import CustomScrollArea
from views.componenets.customsComponents.flow_layout import FlowLayout
from views.componenets.customsComponents.table.form_componenets.custom_label import CustomLabel
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon, QFont, QColor, QImage
from PyQt6.QtWidgets import QCalendarWidget


class AppointmentDetailsForm(QWidget):
    toggleNextButtonStatusSignal = pyqtSignal(bool)

    def __init__(self, service_controller, parent=None):
        super().__init__(parent)

        self.rendered_time_slot_widget_wrapper = None
        self.time_slots_button_group = None
        self.rendered_time_slots = None
        self.currently_selected_doctor_schedules = None
        self.currently_selected_doctor_service_id = None
        self.currently_selected_doctor_service_data = None
        self.currently_selected_time_slot_id = None
        self.service_selection_form_data = None

        # Signals
        self.signals = SignalRepositorySingleton.instance()

        self.doctor_service_controller = DoctorServiceRelationController()
        self.doctor_schedule_controller = DoctorScheduleController()
        self.appointments_controller = AppointmentController()
        self.service_controller = service_controller

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

        service_selection_label = CustomLabel(name="Select Service")

        self.service_name_model = QStandardItemModel()

        self.service_selection_combo = CustomComboBox()
        self.service_selection_combo.setFixedWidth(450)
        self.service_selection_combo.currentIndexChanged.connect(self.on_service_index_changed)
        self.service_selection_combo.setStyleSheet(self.combo_style_sheet)
        self.service_selection_combo.setModel(self.service_name_model)

        service_selection_layout = QVBoxLayout()
        service_selection_layout.setContentsMargins(0, 0, 0, 0)
        service_selection_layout.setSpacing(10)

        service_selection_layout.addWidget(service_selection_label)
        service_selection_layout.addWidget(self.service_selection_combo)
        # --------------------------------------------------------------

        available_doctors_label = CustomLabel(name="Available Doctors")

        self.available_doctors_model = QStandardItemModel()

        self.available_doctors_combo = CustomComboBox()
        self.available_doctors_combo.setFixedWidth(450)
        self.available_doctors_combo.setStyleSheet(self.combo_style_sheet)

        self.available_doctors_combo.currentIndexChanged.connect(self.on_available_doctors_index_changed)
        self.available_doctors_combo.setModel(self.available_doctors_model)

        available_doctors_layout = QVBoxLayout()
        available_doctors_layout.setContentsMargins(0, 0, 0, 0)
        available_doctors_layout.setSpacing(10)

        available_doctors_layout.addWidget(available_doctors_label)
        available_doctors_layout.addWidget(self.available_doctors_combo)

        service_doctors_layout = QHBoxLayout()
        service_doctors_layout.setContentsMargins(0, 0, 0, 0)
        service_doctors_layout.setSpacing(20)

        service_doctors_layout.addLayout(service_selection_layout)
        service_doctors_layout.addLayout(available_doctors_layout)
        # --------------------------------------------------------------

        self.calendar_selection_widget = CustomCalendarWidget(self)
        self.calendar_selection_widget.dateActivated.connect(self.get_available_time_slots)
        self.calendar_selection_widget.dateDisActive.connect(self.delete_rendered_time_slots)

        self.rendered_time_slots_stack_widget_stack_widget = QStackedWidget(self)

        self.calendar_time_slots_layout = QHBoxLayout()
        self.calendar_time_slots_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.calendar_time_slots_layout.setContentsMargins(0, 30, 0, 0)
        self.calendar_time_slots_layout.setSpacing(20)

        self.calendar_time_slots_layout.addWidget(self.calendar_selection_widget)
        self.calendar_time_slots_layout.addWidget(self.rendered_time_slots_stack_widget_stack_widget)

        main_vertical_layout = QVBoxLayout()
        main_vertical_layout.setContentsMargins(0, 0, 0, 0)

        main_vertical_layout.addLayout(service_doctors_layout)
        main_vertical_layout.addLayout(self.calendar_time_slots_layout)

        central_widget = QWidget()
        central_widget.setLayout(main_vertical_layout)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.setContentsMargins(40, 20, 40, 20)
        layout.addWidget(central_widget)

        self.setLayout(layout)

    def set_appointment_details_data(self, data):
        self.currently_selected_time_slot_id = data["appointment_time"]
        year, month, day = map(int, data["appointment_date"].split('-'))
        qdate = QDate(year, month, day)
        self.calendar_selection_widget.setSelectedDate(qdate)

    def get_appointment_details_data(self):
        rendered_time_slot_widget = self.rendered_time_slots_stack_widget_stack_widget.currentWidget()
        if not rendered_time_slot_widget:
            return None
        else:
            return {
                "service_name": self.service_selection_combo.currentText(),
                "doctor_name": self.available_doctors_combo.currentText(),
                "doctor_service_relation_id": self.currently_selected_doctor_service_id,
                "doctor_service_relation_data": self.currently_selected_doctor_service_data,
                "appointment_date": self.calendar_selection_widget.selectedDate().toString(),
                "appointment_time": self.currently_selected_time_slot_id
            }

    def set_currently_selected_doctor_service_id(self, doctor_service_id):
        self.currently_selected_doctor_service_id = doctor_service_id

    def set_currently_selected_time_slot_id(self, time_slot_id):
        self.currently_selected_time_slot_id = time_slot_id

    def get_currently_selected_time_slot_id(self):
        return self.currently_selected_time_slot_id

    def set_currently_selected_doctor_schedules(self, schedules):
        self.currently_selected_doctor_schedules = schedules

    def get_currently_selected_doctor_schedules(self):
        return self.currently_selected_doctor_schedules

    @asyncSlot(QDate)
    async def get_available_time_slots(self, date: QDate):
        day = date.toString('dddd')

        # Check if appointments exist with this date
        scheduled_appointments = await self.appointments_controller.check_if_any_taken_doctor_service_time_slots(
            date=date.toString(), doctor_service_relation_id=self.currently_selected_doctor_service_id)

        un_available_time_slots = []

        if scheduled_appointments:
            for appointment in scheduled_appointments:
                if appointment["appointment_status"] == "scheduled" or appointment[
                    "appointment_status"] == "re-scheduled":
                    formatted_time_slot = (
                        datetime.strptime(appointment["appointment_time"], "%H:%M:%S").strftime("%H:%M"))
                    un_available_time_slots.append(formatted_time_slot)

        current_time_slots = []
        for schedule in self.currently_selected_doctor_schedules:
            if day == schedule["day"]:
                for time_slot in schedule["time_slots"]:
                    if time_slot in un_available_time_slots:
                        current_time_slots.append({"is_available": False, "time_slot": time_slot})
                    else:
                        current_time_slots.append({"is_available": True, "time_slot": time_slot})

        self.refresh_rendered_time_slots(current_time_slots)

    def delete_rendered_time_slots(self):
        self.refresh_rendered_time_slots([])

    @asyncSlot(int)
    async def on_service_index_changed(self, index):
        service_name = self.service_selection_combo.currentText()
        if service_name:
            doctors = await self.doctor_service_controller.get_all_doctors_by_service_name(service_name)
            if doctors:
                self.available_doctors_combo.clear()
                for doctor in doctors:
                    standard_item = QStandardItem()
                    name = doctor["first_name"] + " " + doctor["last_name"]
                    standard_item.setData(name, Qt.ItemDataRole.DisplayRole)
                    standard_item.setData(doctor["doctor_service_relation_id"], Qt.ItemDataRole.UserRole)
                    self.available_doctors_model.appendRow(standard_item)
                    self.available_doctors_combo.update()
            else:
                self.available_doctors_combo.clear()
                await self.calendar_selection_widget.set_available_days([])
                self.toggleNextButtonStatusSignal.emit(False)
                self.refresh_rendered_time_slots([])
                self.set_currently_selected_time_slot_id("")
                self.signals.appointmentHeaderInternalLoaderSignal.emit(False)

    @asyncSlot(int)
    async def on_available_doctors_index_changed(self, index):
        item = self.available_doctors_model.item(index)
        if item:
            doctor_service_relation_id = item.data(QtCore.Qt.ItemDataRole.UserRole)
            doctor_service_relation_and_schedule_data = await self.doctor_service_controller.get_doctor_service_relation_and_schedule_by_id(
                doctor_service_relation_id)

            if doctor_service_relation_and_schedule_data:
                self.set_currently_selected_doctor_service_id(doctor_service_relation_id)

                self.set_currently_selected_doctor_schedules(
                    doctor_service_relation_and_schedule_data["doctors_schedules"])

                doctor_available_days = [schedule["day"] for schedule in
                                         doctor_service_relation_and_schedule_data["doctors_schedules"]]

                await self.calendar_selection_widget.set_available_days(doctor_available_days)

                doctor_service_relation_and_schedule_data.pop("doctors_schedules")
                doctor_service_relation_and_schedule_data.pop("doctor_service_assistants_relation")
                self.currently_selected_doctor_service_data = doctor_service_relation_and_schedule_data

                self.toggleNextButtonStatusSignal.emit(False)
                self.refresh_rendered_time_slots([])
                self.set_currently_selected_time_slot_id("")
                self.signals.appointmentHeaderInternalLoaderSignal.emit(False)

    async def populate_services(self):
        services = self.service_controller.store.get_data()
        if not services:
            msg = QMessageBox()
            msg.setText('Error occurred')
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setDetailedText("error occurred while deleting, please contact your service provider.")
            msg.exec()
        else:
            self.signals.appointmentHeaderInternalLoaderSignal.emit(True)
            for item in services:
                standard_item = QStandardItem()
                standard_item.setData(item["name"], Qt.ItemDataRole.DisplayRole)
                standard_item.setData(item["service_id"], Qt.ItemDataRole.UserRole)
                self.service_name_model.appendRow(standard_item)

    def render_time_slots(self, data):
        if data:
            self.signals.appointmentHeaderInternalLoaderSignal.emit(True)
            self.rendered_time_slot_widget_wrapper = RenderedTimeSlotsWidgets()

            content_widget = QWidget()
            content_widget.setStyleSheet("border:0;")

            content_layout = QVBoxLayout(content_widget)
            content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            content_layout.setContentsMargins(0, 0, 0, 0)
            content_layout.setSpacing(20)

            scroll_area = CustomScrollArea(self)
            scroll_area.setContentsMargins(10, 10, 10, 10)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            scroll_area.setWidget(content_widget)

            buttons_layout = FlowLayout(h_spacing=30, v_spacing=30)
            buttons_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            for time_slot in data:
                button = TimeSlotButton(time_slot["time_slot"])
                buttons_layout.addWidget(button)

                if time_slot["is_available"]:
                    button.setStyleSheet(button.available_setStyleSheet)
                    button.setProperty("id", time_slot["time_slot"])
                    self.rendered_time_slot_widget_wrapper.time_slots_button_group.addButton(button)
                else:
                    button.setDisabled(True)
                    button.setToolTip("unavailable")
                    button.setStyleSheet(button.un_available_setStyleSheet)

            self.rendered_time_slot_widget_wrapper.time_slots_button_group.buttonClicked.connect(
                self.change_time_slot_btn_style)

            content_layout.addLayout(buttons_layout)
            self.rendered_time_slot_widget_wrapper.wrapper_layout.addWidget(scroll_area)
            self.signals.appointmentHeaderInternalLoaderSignal.emit(False)
            return self.rendered_time_slot_widget_wrapper
        else:
            return QLabel()

    def refresh_rendered_time_slots(self, data):
        newly_rendered_time_slots = self.render_time_slots(data)

        if self.rendered_time_slots is not None:
            self.calendar_time_slots_layout.removeWidget(self.rendered_time_slots)
            self.rendered_time_slots.deleteLater()

        # Update the reference to the new widget
        self.rendered_time_slots = newly_rendered_time_slots

        # Insert the new widget at the correct position
        if self.rendered_time_slots:
            self.rendered_time_slots_stack_widget_stack_widget.addWidget(self.rendered_time_slots)
            self.rendered_time_slots_stack_widget_stack_widget.setCurrentWidget(self.rendered_time_slots)

        self.toggleNextButtonStatusSignal.emit(False)

    @asyncSlot(QAbstractButton)
    async def change_time_slot_btn_style(self, button: QPushButton):
        # Update styles
        for btn in self.rendered_time_slots_stack_widget_stack_widget.currentWidget().time_slots_button_group.buttons():
            if btn == button:
                btn.setChecked(True)
                btn.style().unpolish(btn)
                btn.style().polish(btn)
                btn.setStyleSheet("""
                    border:0;
                    border-radius:7px;
                    color:white;
                    background-color:#2563EB;
                    font-weight:bold;
                """)
                btn.update()
                btn.repaint()
                self.set_currently_selected_time_slot_id(button.property("id"))
                self.toggleNextButtonStatusSignal.emit(True)
            else:
                btn.style().unpolish(btn)
                btn.setStyleSheet("""
                    border:1px solid #D5D5D5;
                    border-radius:7px;
                    color:#2C2D33;
                    background-color:white;
                """)
                btn.style().polish(btn)
                btn.update()


class RenderedTimeSlotsWidgets(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        wrapper_widget = QWidget()
        wrapper_widget.setObjectName("rendered_ime_slots_widgets")
        wrapper_widget.setStyleSheet("""
        QWidget#rendered_ime_slots_widgets {
            border:1px solid #D5D5D5;
            background-color:#F6F8FA;
            border-radius:7px;
        }
        """)

        doctor_available_time_slots_label = QLabel("Doctor Available Times Slots")
        doctor_available_time_slots_label.setStyleSheet("background-color:transparent;border:0;color:black;")

        font = doctor_available_time_slots_label.font()
        font.setWeight(QFont.Weight.Medium)
        font.setPointSize(16)
        doctor_available_time_slots_label.setFont(font)

        self.time_slots_button_group = QButtonGroup()

        self.wrapper_layout = QVBoxLayout(wrapper_widget)
        self.wrapper_layout.setContentsMargins(20, 20, 10, 10)
        self.wrapper_layout.setSpacing(20)
        self.wrapper_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.wrapper_layout.addWidget(doctor_available_time_slots_label)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(wrapper_widget)

        self.setLayout(layout)
        self.setStyleSheet("background-color:transparent;")


class TimeSlotButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)

        font = self.font()
        font.setPixelSize(13)
        font.setWeight(font.Weight.DemiBold)
        self.setFont(font)

        self.available_setStyleSheet = """
        border:1px solid #D5D5D5;
        border-radius:7px;
        color:#2C2D33;
        background-color:white;
        """
        self.un_available_setStyleSheet = """
        border:0;
        border-radius:7px;
        color:#a4a4a4;
        background-color:#ebebeb;
        """

        self.setFixedSize(QSize(100, 35))


QSS = '''
QCalendarWidget QMenu {
        width: 150px;
        left: 20px;
        color: #2C2D33;
        font-size: 16px;
        background-color: #F6F8FA;
}

QCalendarWidget QSpinBox { 
        width: 50px;
        font-size: 18px;
        font-weight:bold;
        color: #4B4E58; 
        background-color: white; 
        selection-background-color:white ;
        selection-color: #2C2D33;
}
QCalendarWidget QSpinBox::up-button { subcontrol-origin: border;  subcontrol-position: top right;  width:16px; border:0; }
QCalendarWidget QSpinBox::down-button {subcontrol-origin: border; subcontrol-position: bottom right;  width:16px; border:0;}
QCalendarWidget QSpinBox::up-arrow { width:20px;  height:20px; image: url(:/resources/icons/spin_up.svg); }
QCalendarWidget QSpinBox::down-arrow { width:20px;  height:20px; image: url(:/resources/icons/spin_down.svg);}

QCalendarWidget QAbstractItemView
{ 
        selection-background-color: transparent;
        border:0;
}

QCalendarWidget QTableView
{
    border-width:0px;
    background-color:white;
    color:#2C2D33;
    font-size:14px;
    selection-background-color: white;
}
#qt_calendar_prevmonth {
     background-color:transparent;
     margin-left:20px;
}

#qt_calendar_prevmonth:hover {
     border:0;
}

#qt_calendar_nextmonth{
     background:#2563EB;
     margin-right:20px;
}

#qt_calendar_nextmonth:hover{
     border:0;
}

#qt_calendar_navigationbar {
    background: #2563EB;
    border:0;
    border-radius:7px;
    font-size:14px;
}
QCalendarWidget QToolButton#qt_calendar_monthbutton {
    /* General button properties */
    background-color: #2563EB;
    border: 0;
    padding: 5px;
    color:white;
    margin-right: 10px;  /* Adjust as needed */

}

QCalendarWidget QToolButton#qt_calendar_monthbutton:hover {
    /* Styling when button is hovered */
    background-color: #2563EB;
}

QCalendarWidget QToolButton#qt_calendar_monthbutton:pressed {
    /* Styling when button is pressed */
    background-color: #2563EB;
}

QCalendarWidget QToolButton#qt_calendar_monthbutton::menu-indicator {
    /* Hide the menu indicator (down arrow) if desired */
    image: none;
}
QCalendarWidget QToolButton#qt_calendar_yearbutton {
    background-color: #2563EB;
    border: 0;
    padding: 5px;
    color:white;
    margin-left: 10px;  /* Adjust as needed */
}

QCalendarWidget QToolButton#qt_calendar_yearbutton:hover {
    background-color:  #2563EB;
}

QCalendarWidget QToolButton#qt_calendar_yearbutton:pressed {
        background-color:  #2563EB;
}

QCalendarWidget QToolButton#qt_calendar_yearbutton::menu-indicator {
    image: none;
}
'''

Enabled_date_style = '''
    QDateEdit {
        border:1px solid #8D8D8D;
        color:#112C41;
        background-color:white;
        border-radius:3px;
    }
    QDateEdit::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 15px;
        padding-right: 5px;
        border: none;
        image: url(:/resources/icons/calendar.svg);
    }
'''

Disabled_date_style = '''
    QDateEdit {
        border:1px solid #CACACA;
        border-radius:3px;
        color:#2C2D33;
        background-color:white;
    }
    QDateEdit::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 15px;
        padding-right: 5px;
        border: none;
        image: url(:/resources/icons/calendar.svg);
    }
'''


class CustomCalendarWidget(QCalendarWidget):
    availableDaysChanged = pyqtSignal()
    dateActivated = pyqtSignal(QDate)
    dateDisActive = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._events = set()
        self.day_name_to_number = {
            'Monday': 1,
            'Tuesday': 2,
            'Wednesday': 3,
            'Thursday': 4,
            'Friday': 5,
            'Saturday': 6,
            'Sunday': 7
        }
        self.available_days = None

        self.highlighted_dates = self.get_highlighted_dates(QDate.currentDate().month(), QDate.currentDate().year())
        self.availableDaysChanged.connect(self.update_highlighted_dates)
        self.selectionChanged.connect(self.update_highlighted_dates)
        self.clicked.connect(self.day_selected)

        self.setGridVisible(False)

        self.setFixedHeight(400)
        self.setFixedWidth(450)

        prev_button = self.findChild(QtWidgets.QToolButton, "qt_calendar_prevmonth")
        next_button = self.findChild(QtWidgets.QToolButton, "qt_calendar_nextmonth")

        self.currentPageChanged.connect(self.on_navigation_changed)

        # Create QIcon instances for your icons
        prev_icon = QIcon(":resources/icons/arrow_back.svg")
        next_icon = QIcon(":resources/icons/arrow_forward.svg")

        # Set the icons to the buttons
        prev_button.setIcon(prev_icon)
        next_button.setIcon(next_icon)

        navigation = self.findChild(QtWidgets.QWidget, "qt_calendar_navigationbar")
        navigation.setFixedHeight(45)
        navigation.setContentsMargins(10, 10, 10, 10)

        for btn in (prev_button, next_button):
            btn.setIconSize(QtCore.QSize(15, 15))

        for d in (
                Qt.DayOfWeek.Saturday, Qt.DayOfWeek.Sunday, Qt.DayOfWeek.Monday,
                Qt.DayOfWeek.Tuesday, Qt.DayOfWeek.Wednesday, Qt.DayOfWeek.Thursday, Qt.DayOfWeek.Friday):
            fmt = self.weekdayTextFormat(d)
            fmt.setFontPointSize(12)
            fmt.setForeground(QColor('#000'))
            fmt.setBackground(QColor('white'))
            fmt.setFontWeight(QFont.Weight.Medium)
            self.setWeekdayTextFormat(d, fmt)

        self.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)

        self.setStyleSheet(QSS)
        self.setHorizontalHeaderFormat(QCalendarWidget.HorizontalHeaderFormat.ShortDayNames)
        self.setDateRange(QDate.currentDate(), QDate.currentDate().addYears(1))

    def on_navigation_changed(self, year, month):
        self.get_highlighted_dates(year=year, month=month)
        self.update_highlighted_dates()

    def get_highlighted_dates(self, month, year):
        if self.available_days:
            highlighted_dates = []
            current_date = QDate.currentDate()
            start_date = QDate(year, month, 1)
            end_date = QDate.currentDate().addDays(40)

            if year >= current_date.year() or (year == current_date.year() and month >= current_date.month()):
                # If it's the current month, start from today
                if month == current_date.month() and year == current_date.year():
                    start_date = current_date

                # Generate dates for the whole month
                while start_date.month() == month or (start_date.month() == end_date.month()):
                    if start_date.dayOfWeek() in self.available_days and start_date >= current_date:
                        highlighted_dates.append(start_date)
                    start_date = start_date.addDays(1)
            return highlighted_dates

    def day_selected(self, date: QDate):
        if self.highlighted_dates:
            if date in self.highlighted_dates:
                self.dateActivated.emit(self.selectedDate())
            else:
                self.dateDisActive.emit()

    def update_highlighted_dates(self):
        month = self.selectedDate().month()
        year = self.selectedDate().year()
        self.highlighted_dates = self.get_highlighted_dates(month=month, year=year)
        self.update()

    async def set_available_days(self, available_days):
        if available_days:
            self.available_days = [self.day_name_to_number[day] for day in available_days]
        else:
            self.available_days = []
        self.availableDaysChanged.emit()

    def paintCell(self, painter, rect, date):
        rect.adjust(0, 5, 0, -5)
        if self.highlighted_dates:
            if date in self.highlighted_dates and date.month() == self.monthShown():
                painter.save()
                r = QRect(QPoint(), QSize(min(rect.width(), rect.height()), min(rect.width(), rect.height())))
                r.moveCenter(rect.center())
                img = QImage(":resources/icons/available_date.svg")
                scaled_img = img.scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio,
                                        Qt.TransformationMode.SmoothTransformation)
                painter.drawImage(r, scaled_img)
                painter.setPen(QPen(QColor("white")))
                painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(date.day()))
                painter.restore()
                if date == self.selectedDate():
                    painter.save()
                    r = QtCore.QRect(QtCore.QPoint(), min(rect.width(), rect.height()) * QtCore.QSize(1, 1))
                    r.moveCenter(rect.center())
                    img = QImage(":resources/icons/selected_date.svg")
                    scaled_img = img.scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio,
                                            Qt.TransformationMode.SmoothTransformation)
                    painter.drawImage(r, scaled_img)
                    painter.setPen(QtGui.QPen(QtGui.QColor("white")))

                    painter.drawText(rect, QtCore.Qt.AlignmentFlag.AlignCenter, str(date.day()))
                    painter.restore()
            else:
                if date.month() != self.monthShown():
                    pass
                else:
                    painter.fillRect(rect, QColor(255, 255, 255, 100))
                    painter.setPen(QColor('#DFDFE3'))
                    painter.drawText(rect, QtCore.Qt.AlignmentFlag.AlignCenter, str(date.day()))
