from PyQt6.QtCore import Qt, QSize, pyqtSlot, QTime, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QButtonGroup, QLabel, QStackedWidget, \
    QMessageBox
from qasync import asyncSlot

from loggers.logger_configs import set_up_logger
from signals import SignalRepositorySingleton
from utils.validator import AgeIntValidator
from views.componenets.customsComponents.buttons.button_with_loader import ButtonWithLoader
from views.componenets.customsComponents.custom_combobox import CustomComboBox
from views.componenets.customsComponents.flow_layout import FlowLayout
from views.componenets.customsComponents.table.form_componenets.custom_input import CustomLineEdit
from views.componenets.customsComponents.dates_and_times.custom_range_time_picker import CustomRangeTimePicker
from views.componenets.customsComponents.table.form_componenets.custom_label import CustomLabel

logger = set_up_logger('main.views.staff.doctors.doctor_service_management.doctor_service_form.available_days_widget')


def connect_day_dis_activating_signal(day_button: QPushButton):
    return lambda: apply_day_dis_activate_logic(day_button)


def apply_day_dis_activate_logic(day_button):
    day_button.setProperty("is_active", False)
    apply_focus_button_style(day_button)


def apply_day_activated_logic(day_button):
    day_button.setProperty("is_active", True)
    apply_active_and_focused_button_style(day_button)


def connect_day_activated_signal(day_button: QPushButton):
    return lambda: apply_day_activated_logic(day_button)


class AvailableDaysWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.available_days_data = []
        self.available_days_buttons = []
        self.days_views = {}

        self.days = [
            {
                "name": "Sunday",
                "id": 1,
                "is_active": False,
            },
            {
                "name": "Monday",
                "id": 2,
                "is_active": False,

            },
            {
                "name": "Tuesday",
                "id": 3,
                "is_active": False,

            },
            {
                "name": "Wednesday",
                "id": 4,

                "is_active": False,

            },
            {
                "name": "Thursday",
                "id": 5,

                "is_active": False,

            },
            {
                "name": "Friday",
                "id": 6,
                "is_active": False,

            },
            {
                "name": "Saturday",
                "id": 7,
                "is_active": False,

            },
        ]

        self.days_buttons_group = QButtonGroup()

        self.days_buttons_group.buttonClicked.connect(self.change_day_button_style)

        days_layout = self.create_days_layout()
        self.stacked_widget = self.create_stacked_widget()

        # Set first Day
        self.set_main_content("Sunday")
        self.change_day_button_style(self.available_days_buttons[0])

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.setSpacing(20)

        layout.addLayout(days_layout)
        layout.addWidget(self.stacked_widget)

        self.setStyleSheet("""
            QWidget {
                background-color:white;
            }
        """)

        self.setLayout(layout)

    def create_days_layout(self):
        days_layout = QHBoxLayout()
        days_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        days_layout.setSpacing(20)

        include_these_days_label = CustomLabel("Days")

        font = include_these_days_label.font()
        font.setPixelSize(18)
        font.setWeight(QFont.Weight.Bold)
        include_these_days_label.setFont(font)
        include_these_days_label.setFixedSize(QSize(150, 30))

        days_layout.addWidget(include_these_days_label)

        for day in self.days:
            button = QPushButton(day["name"][:3])
            self.configure_button(button, day)
            self.days_buttons_group.addButton(button, day["id"])
            self.available_days_buttons.append(button)
            days_layout.addWidget(button)

        return days_layout

    def configure_button(self, button, day):
        button.setCheckable(True)
        button.setFixedSize(QSize(50, 50))
        apply_default_style(button)

        button.setObjectName(day["name"])

        button_id = day["id"]
        button.setProperty("id", button_id)
        button.setProperty("is_active", False)
        button.clicked.connect(lambda _, b=button.objectName(): self.set_main_content(b))

    def create_stacked_widget(self):
        stack_widget = QStackedWidget()

        for day in self.days:
            day_view = self.TimeSlotsSelectionWidget(day["name"])
            stack_widget.addWidget(day_view)
            self.days_views[day["name"]] = day_view

            day_button = self.days_buttons_group.button(day["id"])
            day_view.dayActivatedSignal.connect(connect_day_activated_signal(day_button))
            day_view.dayDisActivatingSignal.connect(connect_day_dis_activating_signal(day_button))

        return stack_widget

    def change_day_button_style(self, button):
        if button.property("is_active"):
            apply_active_and_focused_button_style(button)
        else:
            apply_focus_button_style(button)

        for btn in self.days_buttons_group.buttons():
            if btn != button:
                if btn.property("is_active"):
                    apply_active_button_style(btn)
                else:
                    apply_default_style(btn)

    def set_main_content(self, day):
        widget = self.days_views.get(day)
        if widget:
            self.stacked_widget.setCurrentWidget(widget)

    def get_days_and_time_slots_data(self):
        available_days_data = []
        days_stack_widget = self.stacked_widget
        for i in range(days_stack_widget.count()):
            day_widget = days_stack_widget.widget(i)
            if day_widget and day_widget.day_data["time_slots"]:
                available_days_data.append(day_widget.day_data)

        return available_days_data

    class TimeSlotsSelectionWidget(QWidget):
        dayActivatedSignal = pyqtSignal(str)
        dayDisActivatingSignal = pyqtSignal(str)

        def __init__(self, day, parent=None):
            super().__init__(parent)

            # Signals
            self.signals = SignalRepositorySingleton.instance()

            self.generated_time_slots = None
            self.day = day

            self.day_data = {
                "day": self.day,
                "time_slots": [],
                "time_increment": int,
                "time_increment_unit": str,
                "start_time": QTime(),
                "end_time": QTime(),
            }
            self.setObjectName(self.day)

            day_label = CustomLabel(day)

            font = day_label.font()
            font.setPixelSize(16)
            font.setWeight(QFont.Weight.Bold)
            day_label.setFont(font)
            day_label.setFixedSize(150, 30)

            time_picker_label = CustomLabel("Time Range")
            time_picker_label.setFixedSize(150, 30)

            self.time_picker = CustomRangeTimePicker()

            time_picker_layout = QHBoxLayout()
            time_picker_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            time_picker_layout.setSpacing(20)

            time_picker_layout.addWidget(time_picker_label, 0, Qt.AlignmentFlag.AlignLeft)
            time_picker_layout.addWidget(self.time_picker, 1, Qt.AlignmentFlag.AlignLeft)

            time_increment_label = CustomLabel("Time Slot Increment")
            time_increment_label.setFixedSize(160, 30)

            every_label = CustomLabel(name="Every")
            every_label.setFixedWidth(50)

            self.time_increment_value = CustomLineEdit(placeholder_text="", parent=self)
            self.time_increment_value.setValidator(AgeIntValidator())
            self.time_increment_value.setFixedSize(QSize(50, 30))

            self.time_unit = CustomComboBox()
            self.time_unit.setFixedSize(QSize(100, 30))

            self.time_unit.addItem("Hours")
            self.time_unit.addItem("Minutes")

            time_increment_layout = QHBoxLayout()
            time_increment_layout.setContentsMargins(0, 0, 0, 0)
            time_increment_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            time_increment_layout.setSpacing(10)

            time_increment_layout.addWidget(every_label)
            time_increment_layout.addWidget(self.time_increment_value)
            time_increment_layout.addWidget(self.time_unit, Qt.AlignmentFlag.AlignLeft)

            time_slot_config_layout = QHBoxLayout()
            time_slot_config_layout.setContentsMargins(0, 0, 0, 0)
            time_slot_config_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            time_slot_config_layout.setSpacing(10)

            time_slot_config_layout.addWidget(time_increment_label)
            time_slot_config_layout.addLayout(time_increment_layout)

            self.generate_time_slots_btn = ButtonWithLoader("Generate Time Slots", size=QSize(160, 34))
            self.generate_time_slots_btn.setStyleSheet("""
            QPushButton {
                border:1px solid #D3D3D3;
                border-radius:3px;
                background-color:#F6F8FA;
                color:#2C2D33;
            }
            QPushButton:pressed {
                border:1px solid #D3D3D3;
                border-radius:3px;
                color:#2C2D33;
                padding-top: 2px;
                padding-left: 2px;
            }

            """)
            self.generate_time_slots_btn.clicked.connect(self.render_generated_time_slots)

            self.rendered_time_slots = QLabel()
            self.rendered_time_slots.setFixedSize(10, 10)
            self.rendered_time_slots.hide()

            self.layout = QVBoxLayout()
            self.layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            self.layout.setContentsMargins(0, 0, 0, 0)
            self.layout.setSpacing(30)

            self.layout.addWidget(day_label)
            self.layout.addLayout(time_picker_layout)
            self.layout.addLayout(time_slot_config_layout)
            self.layout.addWidget(self.generate_time_slots_btn)
            self.layout.addWidget(self.rendered_time_slots)

            self.setStyleSheet("""
            QWidget {
                background-color:white;
            }
            QLabel {
                background-color:transparent;
            }
            """)

            self.setLayout(self.layout)

        def get_day_data(self):
            return self.day_data

        async def generate_time_slots(self):
            slots = []

            try:
                start_time_slot = QTime(self.time_picker.from_time_picker.time().toPyTime())

                current_time = start_time_slot

                end_time_slot = QTime(self.time_picker.to_time_picker.time().toPyTime())

                time_increment_value = int(self.time_increment_value.text())
                time_increment_unit = self.time_unit.currentText()

                if time_increment_unit == "Minutes":
                    increment_secs = time_increment_value * 60  # 60 seconds in a minute
                else:
                    increment_secs = time_increment_value * 3600  # 3600 seconds in an hour

                loop_counter = 0
                max_iterations = 1000

                while current_time != end_time_slot.addSecs(increment_secs) and loop_counter < max_iterations:
                    slots.append(current_time.toString("HH:mm"))
                    current_time = current_time.addSecs(increment_secs)
                    if current_time > QTime(23, 59):
                        current_time = QTime(0, 0)
                    loop_counter += 1

                    if loop_counter >= max_iterations:
                        slots = []
                        QMessageBox.critical(self, "Title", "Exceeded maximum time slot generation iterations")

                self.generated_time_slots = slots
                return slots

            except Exception as e:
                logger.error(e, exc_info=True)

        @pyqtSlot()
        def on_time_increment_changed(self):
            QTimer.singleShot(500, self.render_generated_time_slots)

        @pyqtSlot()
        @asyncSlot()
        async def render_generated_time_slots(self):
            generated_slots_label = CustomLabel(name="Generated Time Slots")

            layout = QVBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(20)

            layout.addWidget(generated_slots_label)

            widget = QWidget()
            widget.setLayout(layout)

            h_layout = FlowLayout(h_spacing=5, v_spacing=5)
            h_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            h_layout.setSpacing(10)

            label_style_sheet = """
                    QLabel {
                       color:#4B4E58;
                       border:1px solid #D5D5D5;
                       border-radius:3px;
                    }"""

            if self.validate_time_slots():

                await self.generate_time_slots()

                if self.generated_time_slots:
                    self.generate_time_slots_btn.start()
                    self.layout.removeWidget(self.rendered_time_slots)

                    for slot in self.generated_time_slots:
                        label = QLabel(slot)
                        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        label.setContentsMargins(5, 5, 5, 5)
                        label.setFixedSize(80, 30)
                        label.setStyleSheet(label_style_sheet)
                        h_layout.addWidget(label)

                    layout.addLayout(h_layout)

                    self.rendered_time_slots = widget

                    self.layout.addWidget(self.rendered_time_slots)
                    # self.updateGeometry()
                    self.signals.doctorServiceFormWidgetNewContentIsAddedSignal.emit()
                    self.dayActivatedSignal.emit(self.day)

                    self.day_data["time_slots"] = self.generated_time_slots
                    self.day_data["time_increment"] = int(self.time_increment_value.text())
                    self.day_data["time_increment_unit"] = self.time_unit.currentText()
                    self.day_data["start_time"] = QTime(self.time_picker.from_time_picker.time().toPyTime()).toString()
                    self.day_data["end_time"] = QTime(self.time_picker.to_time_picker.time().toPyTime()).toString()

                    self.generate_time_slots_btn.stop()
                else:
                    self.validation_error_reset()
                    QMessageBox.warning(self, "Warning", "Invalid time range from here.")

            self.generate_time_slots_btn.stop()

        def validate_time_slots(self):
            time_increment_value = self.time_increment_value.text()
            start_time_slot = self.time_picker.from_time_picker.time()
            end_time_slot = self.time_picker.to_time_picker.time()

            if not time_increment_value:
                QMessageBox.warning(self, "Warning", "Invalid Time Increment.")
                self.validation_error_reset()
                return False

            if start_time_slot == QTime(0, 0) and end_time_slot == QTime(0, 0):
                QMessageBox.warning(self, "Warning", "Invalid Time Range.")
                self.validation_error_reset()
                return False

            if start_time_slot == end_time_slot:
                QMessageBox.warning(self, "Warning", "Invalid Time Range: Start and end times cannot be the same.")
                self.validation_error_reset()
                return False

            if start_time_slot > end_time_slot:
                QMessageBox.warning(self, "Warning",
                                    "Invalid Time Range: Start time cannot be later than end time.")
                self.validation_error_reset()
                return False

            return True

        def validation_error_reset(self):
            layout = QVBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(20)

            widget = QWidget()
            widget.setLayout(layout)

            self.layout.removeWidget(self.rendered_time_slots)
            self.rendered_time_slots = widget

            self.day_data["time_slots"] = []
            self.dayDisActivatingSignal.emit(self.day)


def apply_default_style(button: QPushButton):
    button.setStyleSheet("""
            QPushButton {
                border:1px solid #C7C7C7;
                border-radius:25px;
                background-color:transparent;
                color:#4B4E58;
            }
            """)
    button.setProperty("is_active", False)


def apply_focus_button_style(button: QPushButton):
    button.setStyleSheet("""
            QPushButton {
                border:1px solid #d97706;
                border-radius:24px;
                background-color:transparent;
                color:#4B4E58;
            }
            """)


def apply_active_button_style(button: QPushButton):
    font = button.font()
    font.setPixelSize(14)
    font.setWeight(QFont.Weight.DemiBold)
    button.setFont(font)

    button.setStyleSheet("""
            QPushButton {
                border:0;
                border-radius:24px;
                background-color:#fbbf24;
                color:white;
            }
            """)
    button.setProperty("is_active", True)


def apply_active_and_focused_button_style(button: QPushButton):
    font = button.font()
    font.setPixelSize(14)
    font.setWeight(QFont.Weight.DemiBold)
    button.setFont(font)

    button.setStyleSheet("""
            QPushButton {
                border:1px solid #d97706;
                border-radius:24px;
                background-color:#fbbf24;
                color:white;
            }
            """)

# class TimeIncrementWidget(QWidget):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#
#         every_label = CustomLabel(name="Every")
#         every_label.setFixedWidth(50)
#
#         self.time_increment_value = CustomLineEdit(placeholder_text="", parent=self)
#         self.time_increment_value.setValidator(AgeIntValidator())
#         self.time_increment_value.setFixedSize(QSize(50, 30))
#
#         self.time_unit = CustomComboBox()
#         self.time_unit.setFixedSize(QSize(100, 30))
#
#         self.time_unit.addItem("Hours")
#         self.time_unit.addItem("Minutes")
#
#         time_increment_layout = QHBoxLayout()
#         time_increment_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
#         time_increment_layout.setSpacing(10)
#
#         time_increment_layout.addWidget(every_label)
#         time_increment_layout.addWidget(self.time_increment_value)
#         time_increment_layout.addWidget(self.time_unit, Qt.AlignmentFlag.AlignLeft)
#
#         layout = QVBoxLayout()
#         layout.setContentsMargins(0, 0, 0, 0)
#         layout.addLayout(time_increment_layout)
#         self.setLayout(layout)
