import asyncio
import json
from PyQt6.QtCore import Qt, pyqtSlot, QTime
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QMessageBox, QStackedWidget, QDialog
from qasync import asyncSlot

from loggers.logger_configs import set_up_logger
from services.supabase.controllers.staff.doctor.doctor_service_relation_controller import \
    DoctorServiceRelationController
from signals import SignalRepositorySingleton
from views.componenets.customsComponents.loaders.internal_loader import InternalLoader
from views.componenets.customsComponents.menus.custom_view_option_menu import CustomViewOptionMenu
from views.componenets.table.mangement.table_header_filtration_component import TableHeaderFiltration
from views.componenets.table.mangement.table_layout import TableLayout
from views.staff.doctors.doctor_service_management.doctor_service_dialog import DoctorServiceDialog
from views.staff.doctors.doctors_management.available_days_widget import apply_active_button_style, apply_default_style
from views.staff.doctors.doctors_management.doctor_filter_widget import FilterWidget

logger = set_up_logger('main.views.staff.doctors.doctor_service_management_view')


@asyncSlot()
async def set_doctor_data(form_widget, data):
    form_widget.service_name_selection_widget.setCurrentText(data["service_name"])
    form_widget.cost_input.setText(str(data["doctor_service_cost"]))
    form_widget.duration_input.setText(str(data["doctor_service_duration"]))
    form_widget.status_selection_widget.setCurrentText(str(data["doctor_service_status"]))
    if not data["additional_data"]:
        form_widget.additional_data_input.setText("")
    else:
        form_widget.additional_data_input.setText(json.loads(data["additional_data"]))


def configure_ui_elements_for_state(form_widget, dialog, is_editable):
    state = not is_editable
    form_widget.service_name_selection_widget.setDisabled(state)
    form_widget.cost_input.setReadOnly(state)
    form_widget.duration_input.setReadOnly(state)
    form_widget.status_selection_widget.setDisabled(state)
    form_widget.additional_data_input.setReadOnly(state)
    dialog.update_btn.setVisible(is_editable)
    dialog.save_and_cancel_btns.save_btn.hide()


@asyncSlot()
async def set_doctor_schedule(form_widget, doctor_schedule_days, state):
    days_widget = form_widget.days_widget_and_time_slots_widget
    buttons_group = days_widget.days_buttons_group
    stacked_widget = days_widget.stacked_widget

    # Disable all buttons initially
    all_buttons = buttons_group.buttons()
    for button in all_buttons:
        apply_default_style(button)
        if not state:
            button.setDisabled(True)

    # Update button styles and enable them based on the matching day
    for day_button in all_buttons:
        if any(day_button.objectName() == schedule["day"] for schedule in doctor_schedule_days):
            apply_active_button_style(day_button)
            day_button.setDisabled(False)

    # Process each stacked widget item
    for i in range(stacked_widget.count()):
        widget = stacked_widget.widget(i)
        day_data = widget.day_data
        matching_schedule = next(
            (schedule for schedule in doctor_schedule_days if schedule["day"] == day_data["day"]), None)

        if matching_schedule:
            widget.time_picker.from_time_picker.setTime(matching_schedule["start_time"])
            widget.time_picker.to_time_picker.setTime(matching_schedule["end_time"])
            widget.time_increment_value.setText(str(matching_schedule["time_increment"]))
            widget.time_unit.setCurrentText(matching_schedule["time_increment_unit"])

            day_data["day"] = matching_schedule["day"]
            day_data["time_slots"] = matching_schedule["time_slots"]
            day_data["time_increment"] = matching_schedule["time_increment"]
            day_data["start_time"] = matching_schedule["start_time"]
            day_data["end_time"] = matching_schedule["end_time"]

            await widget.generate_time_slots()
            await widget.render_generated_time_slots()

            # Disable components after setting values
            if not state:
                widget.time_picker.from_time_picker.setDisabled(True)
                widget.time_picker.to_time_picker.setDisabled(True)
                widget.time_increment_value.setReadOnly(True)
                widget.time_unit.setDisabled(True)
                widget.generate_time_slots_btn.hide()

            days_widget.set_main_content(matching_schedule["day"])


@asyncSlot()
async def set_doctor_assistants(form_widget, doctor_assistants_data, state):
    form_widget.assistants_selection_widget.re_render_assistant_content_widget(doctor_assistants_data)
    state = not state
    form_widget.assistants_selection_widget.setDisabled(state)

    all_options_menus = form_widget.assistants_selection_widget.assistants_content_widgets.findChildren(CustomViewOptionMenu)
    for menu in all_options_menus:
        menu.menu_button.setDisabled(False)

    form_widget.assistants_selection_widget.search_bar.setVisible(not state)
    form_widget.assistants_selection_widget.filter_widget.setVisible(not state)
    if state:
        form_widget.assistants_selection_widget.setMinimumHeight(200)


class DoctorServiceManagementView(QDialog):

    def __init__(self, doctor_id, parent=None):
        super().__init__(parent)

        self.setStyleSheet("background-color:white;")
        self.tab_buttons = None
        self.parent = parent
        self.doctor_id = doctor_id

        self.is_search_enabled = False
        self.is_filter_enabled = False
        self.doctor_edit_dialog = None

        self.central_widget = None
        self.table_view = None
        self.table_header_filtration = None
        self.add_doctor_dialog_view = None
        self.doctor_view_dialog = None
        self.view_doctor_information_widget = None
        self.edit_doctor_information_widget = None
        self.edit_doctor_dialog_view = None
        self.filter_widget = None
        self.data = []

        self.stacked_content_widget = QStackedWidget()

        # Signals
        self.signals = SignalRepositorySingleton.instance()

        # API model
        self.doctor_service_controller = DoctorServiceRelationController()

        # Loading animation layout
        self.main_h_layout = QHBoxLayout()
        self.main_h_layout.setContentsMargins(0, 0, 0, 0)
        self.main_h_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.main_h_layout.addWidget(self.stacked_content_widget)

        # Set Layouts
        self.setLayout(self.main_h_layout)
        self.setMinimumSize(1366, 768)

        asyncio.create_task(self.get_initial_data())

    async def get_initial_data(self):
        self.data = await self.doctor_service_controller.get_items(doctor_id=self.doctor_id, page_number=1,
                                                                   item_per_page=10)
        self.setup_table_ui()

    def setup_table_ui(self):
        self.table_view = TableLayout(table_name="doctors_services_relation",
                                      data_controller=self.doctor_service_controller,
                                      data_columns=[
                                          "doctor_service_relation_id",
                                          "service_name",
                                          "doctors",
                                          "doctor_service_assistants_relation",
                                          "doctors_schedules",
                                          "doctor_service_cost",
                                          "doctor_service_status",
                                          "created_at",
                                          "updated_at"

                                      ], column_display_names=
                                      {
                                          "doctor_service_relation_id": "ID",
                                          "service_name": "Service name",
                                          "doctors": "Doctor name",
                                          "doctor_service_assistants_relation": "Doctor Assistants",
                                          "doctors_schedules": "Doctor days",
                                          "doctor_service_cost": "Service cost",
                                          "doctor_service_status": "Service status",
                                          "created_at": "Created at",
                                          "updated_at": "Updated at",

                                      },
                                      is_pagination=True, parent=self)

        self.table_view.update_table_view()

        self.filter_widget = FilterWidget(parent=self)

        self.table_header_filtration = TableHeaderFiltration(add_btn_name="Service",
                                                             controller=self.doctor_service_controller,
                                                             apply_filter=False, page_filter_widget=self.filter_widget,
                                                             apply_search=True,
                                                             search_place_holder="search by service name,status",
                                                             parent=self)

        self.internal_loader = InternalLoader(height=35, parent=self)
        self.table_header_filtration.left_layout.addWidget(self.internal_loader, 0, Qt.AlignmentFlag.AlignLeft)

        self.central_widget = QWidget()

        table_content_v_layout = QVBoxLayout()
        self.central_widget.setLayout(table_content_v_layout)
        table_content_v_layout.setContentsMargins(0, 0, 0, 0)
        table_content_v_layout.setSpacing(0)

        table_header_with_table_layout = QVBoxLayout()
        table_header_with_table_layout.setContentsMargins(0, 20, 0, 0)
        table_header_with_table_layout.setSpacing(0)

        table_header_with_table_layout.addWidget(self.table_header_filtration)
        table_header_with_table_layout.addWidget(self.table_view)

        table_content_v_layout.addLayout(table_header_with_table_layout)

        self.table_header_filtration.add_btn.clicked.connect(self.show_add_doctor_dialog)

        self.table_view.viewSignal.connect(self.view_doctor_service_and_schedule)
        self.table_view.editSignal.connect(self.edit_doctor_service_and_schedule)
        self.table_view.deleteSignal.connect(self.delete_doctor)

        self.set_main_content(self.central_widget)

    def set_main_content(self, content_widget):
        self.stacked_content_widget.addWidget(content_widget)
        self.stacked_content_widget.setCurrentWidget(content_widget)

    def fetch_and_update_table_view(self):
        self.table_view.update_table_view()
        self.activateWindow()

    @pyqtSlot()
    @asyncSlot()
    async def refresh_table(self):
        self.data = await self.doctor_service_controller.get_items(doctor_id=self.doctor_id, page_number=1,
                                                                   item_per_page=10)
        self.fetch_and_update_table_view()

    @pyqtSlot()
    @asyncSlot()
    async def view_doctor_service_and_schedule(self):
        self.internal_loader.start()
        if self.table_view.get_current_id():
            data = await self.fetch_doctor_service_data()
            if not data:
                return

            self.doctor_view_dialog = DoctorServiceDialog("view", parent=self)
            form_widget = self.doctor_view_dialog.form_widget

            await form_widget.populate_services()

            await set_doctor_data(form_widget, data)

            doctor_schedule_days = [
                {
                    "day": schedule["day"],
                    "start_time": QTime.fromString(schedule["start_time"], "HH:mm:ss"),
                    "end_time": QTime.fromString(schedule["end_time"], "HH:mm:ss"),
                    "time_increment": schedule["time_increment"],
                    "time_increment_unit": schedule["time_increment_unit"],
                    "time_slots": schedule["time_slots"]
                } for schedule in data["doctors_schedules"]
            ]
            await set_doctor_schedule(form_widget, doctor_schedule_days, False)

            doctor_assistants_data = [
                {
                    "assistant_id": assistant["assistant_id"],
                    "first_name": assistant["first_name"],
                    "last_name": assistant["last_name"],
                } for assistant in data["doctor_service_assistants_relation"]
            ]
            await set_doctor_assistants(form_widget, doctor_assistants_data, False)

            configure_ui_elements_for_state(form_widget, self.doctor_view_dialog, False)
            self.doctor_view_dialog.scroll_top()

            self.doctor_view_dialog.show()
        self.internal_loader.stop()

    @pyqtSlot()
    def show_add_doctor_dialog(self):
        self.internal_loader.start()
        add_doctor_dialog_view = DoctorServiceDialog("add", parent=self)
        add_doctor_dialog_view.update_btn.hide()
        self.internal_loader.stop()
        add_doctor_dialog_view.show()

    @pyqtSlot()
    @asyncSlot()
    async def edit_doctor_service_and_schedule(self):
        self.internal_loader.start()

        if self.table_view.get_current_id():
            data = await self.fetch_doctor_service_data()
            if not data:
                return

            self.doctor_edit_dialog = DoctorServiceDialog("edit", parent=self)
            form_widget = self.doctor_edit_dialog.form_widget

            await form_widget.populate_services()

            await set_doctor_data(form_widget, data)

            doctor_schedule_days = [
                {
                    "day": schedule["day"],
                    "start_time": QTime.fromString(schedule["start_time"], "HH:mm:ss"),
                    "end_time": QTime.fromString(schedule["end_time"], "HH:mm:ss"),
                    "time_increment": schedule["time_increment"],
                    "time_increment_unit": schedule["time_increment_unit"],
                    "time_slots": schedule["time_slots"]
                } for schedule in data["doctors_schedules"]
            ]
            await set_doctor_schedule(form_widget, doctor_schedule_days, True)

            doctor_assistants_data = [
                {
                    "assistant_id": assistant["assistant_id"],
                    "first_name": assistant["first_name"],
                    "last_name": assistant["last_name"],
                } for assistant in data["doctor_service_assistants_relation"]
            ]
            await set_doctor_assistants(form_widget, doctor_assistants_data, True)

            configure_ui_elements_for_state(form_widget, self.doctor_edit_dialog, True)
            self.doctor_edit_dialog.scroll_top()

            self.doctor_edit_dialog.show()
        self.internal_loader.stop()

    @pyqtSlot()
    @asyncSlot()
    async def delete_doctor(self):
        if self.table_view.get_current_id():
            msg = QMessageBox()
            msg.setText('Are you sure you want to delete?')
            msg.setDetailedText("This will delete doctor service and all it related schedules.")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            reply = msg.exec()

            if reply == QMessageBox.StandardButton.Ok:
                self.internal_loader.start()
                data = await self.doctor_service_controller.delete_doctor_service_relation(
                    self.table_view.get_current_id())
                if not data:
                    self.internal_loader.stop()
                    msg = QMessageBox()
                    msg.setText('Could not delete doctor service')
                    msg.setIcon(QMessageBox.Icon.Critical)
                    msg.setDetailedText("error occurred while deleting, please contact your service provider.")
                    msg.exec()
                else:
                    await self.refresh_table()
                    self.internal_loader.stop()
                    msg = QMessageBox()
                    msg.setText('Doctor successfully deleted.')
                    msg.setIcon(QMessageBox.Icon.Information)
                    msg.exec()

    @pyqtSlot()
    @asyncSlot()
    async def fetch_doctor_service_data(self):
        if self.table_view.get_current_id():
            data = await self.doctor_service_controller.get_doctor_service_relation_and_schedule_by_id(
                self.table_view.get_current_id())
            if not data:
                self.signals.globalCreateMessageNotificationSignal.emit({
                    "message_type": "error",
                    "message": "Error while getting doctor data.",
                    "duration": 2000,
                })
                return None
            return data

    def setup_dialog(self, dialog_type):
        self.doctor_view_dialog = DoctorServiceDialog(dialog_type, parent=self)
        form_widget = self.doctor_view_dialog.form_widget
        return self.doctor_view_dialog, form_widget
