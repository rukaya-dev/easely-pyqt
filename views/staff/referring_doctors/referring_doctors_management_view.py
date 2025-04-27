import asyncio

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QMessageBox, QStackedWidget
from qasync import asyncSlot

from loggers.logger_configs import set_up_logger
from services.supabase.controllers.settings.log_controller import LogController
from services.supabase.controllers.staff.referring_doctor.referring_doctor_controller import ReferringDoctorController
from services.supabase.controllers.settings.user_auth_controller import UserAuthController
from signals import SignalRepositorySingleton
from views.componenets.table.mangement.table_header_filtration_component import TableHeaderFiltration
from views.componenets.table.mangement.table_layout import TableLayout
from views.staff.referring_doctors.referring_doctor_dialog import ReferringDoctorDialog
from views.staff.referring_doctors.referring_doctor_filter_widget import FilterWidget

logger = set_up_logger('main.views.staff.referring_doctors.referring_doctors_management.referring_doctors_management_view')


class ReferringDoctorManagementView(QWidget):

    def __init__(self):
        super().__init__()

        self.setStyleSheet("background-color:white;")
        self.tab_buttons = None

        self.is_search_enabled = False
        self.is_filter_enabled = False

        self.central_widget = None
        self.table_view = None
        self.table_header_filtration = None
        self.add_referring_doctor_dialog_view = None
        self.referring_doctor_view_dialog = None
        self.view_referring_doctor_information_widget = None
        self.edit_referring_doctor_information_widget = None
        self.edit_referring_doctor_dialog_view = None
        self.filter_widget = None
        self.data = []

        self.stacked_content_widget = QStackedWidget()

        # Signals
        self.signals = SignalRepositorySingleton.instance()

        # API model
        self.referring_doctor_controller = ReferringDoctorController()
        self.log_controller = LogController()
        self.user_auth_controller = UserAuthController()
        self.auth_user = self.user_auth_controller.user_auth_store.get_user()

        # Loading animation layout
        self.main_h_layout = QHBoxLayout()
        self.main_h_layout.setContentsMargins(0, 0, 0, 0)
        self.main_h_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.main_h_layout.addWidget(self.stacked_content_widget)

        # Set Layouts
        self.setLayout(self.main_h_layout)

        asyncio.create_task(self.get_initial_data())

    async def get_initial_data(self):
        self.data = await self.referring_doctor_controller.get_items(1, 20)
        self.setup_table_ui()


    def setup_table_ui(self):
        self.table_view = TableLayout(table_name="referring_doctors", data_controller=self.referring_doctor_controller,
                                      data_columns=[
                                          "doctor_id",
                                          "first_name",
                                          "last_name",
                                          "category",
                                          "specialty",
                                          "phone_number",
                                          "created_at",
                                          "updated_at"

                                      ], column_display_names=
                                      {
                                          "doctor_id": "ID",
                                          "first_name": "First name",
                                          "last_name": "Last name",
                                          "category": "Category",
                                          "specialty": "Specialty",
                                          "phone_number": "Phone number",
                                          "created_at": "Created at",
                                          "updated_at": "Updated at",

                                      },
                                      is_pagination=True, parent=self)

        self.table_view.update_table_view()

        self.filter_widget = FilterWidget(parent=self)

        self.table_header_filtration = TableHeaderFiltration(add_btn_name="Doctor",
                                                             controller=self.referring_doctor_controller,
                                                             apply_filter=True, page_filter_widget=self.filter_widget,
                                                             apply_search=True,
                                                             search_place_holder="search by name,category,speciality and phone number",
                                                             parent=self)
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

        self.table_header_filtration.add_btn.clicked.connect(self.show_add_referring_doctor_dialog)

        self.table_view.viewSignal.connect(self.view_referring_doctor)
        self.table_view.editSignal.connect(self.edit_referring_doctor)
        self.table_view.deleteSignal.connect(self.delete_referring_doctor)
        # self.table_view.serviceManagementSignal.connect(self.view_service_management)

        self.set_main_content(self.central_widget)

    def set_main_content(self, content_widget):
        self.stacked_content_widget.addWidget(content_widget)
        self.stacked_content_widget.setCurrentWidget(content_widget)

    def fetch_and_update_table_view(self):
        self.table_view.update_table_view()

    @pyqtSlot()
    @asyncSlot()
    async def refresh_table(self):
        self.data = await self.referring_doctor_controller.get_items(self.data["current_page"], 10)
        self.fetch_and_update_table_view()

    @pyqtSlot()
    @asyncSlot()
    async def view_referring_doctor(self):
        if self.table_view.get_current_id():
            self.signals.globalCreateLoadingNotificationSignal.emit("VIEW_DOCTOR")
            data = await self.referring_doctor_controller.get_referring_doctor_by_id(self.table_view.get_current_id())
            if not data:
                self.signals.globalLoadingNotificationControllerSignal.emit("VIEW_DOCTOR")
                self.signals.globalCreateMessageNotificationSignal.emit({
                    "message_type": "error",
                    "message": "Error while getting referring_doctor data.",
                    "duration": 2000,
                })
            else:
                self.referring_doctor_view_dialog = ReferringDoctorDialog("view", parent=self)
                self.view_referring_doctor_information_widget = self.referring_doctor_view_dialog.form_widget

                await self.referring_doctor_view_dialog.populate_categories()

                # setting referring_doctor data
                self.view_referring_doctor_information_widget.first_name_input.setText(data["first_name"])
                self.view_referring_doctor_information_widget.last_name_input.setText(data["last_name"])
                self.view_referring_doctor_information_widget.category_combo.setCurrentText(data["category"])
                self.view_referring_doctor_information_widget.specialty_input.setText(data["specialty"])
                self.view_referring_doctor_information_widget.email_input.setText(data["email"])
                self.view_referring_doctor_information_widget.phone_number_input.setText(data["phone_number"])
                self.view_referring_doctor_information_widget.address_input.setText(data["address"])
                self.view_referring_doctor_information_widget.notes_input.setText(data["address"])

                self.view_referring_doctor_information_widget.first_name_input.setReadOnly(True)
                self.view_referring_doctor_information_widget.last_name_input.setReadOnly(True)
                self.view_referring_doctor_information_widget.category_combo.setDisabled(True)
                self.view_referring_doctor_information_widget.specialty_input.setReadOnly(True)
                self.view_referring_doctor_information_widget.email_input.setReadOnly(True)
                self.view_referring_doctor_information_widget.phone_number_input.setReadOnly(True)
                self.view_referring_doctor_information_widget.address_input.setReadOnly(True)
                self.view_referring_doctor_information_widget.notes_input.setReadOnly(True)

                self.referring_doctor_view_dialog.update_btn.hide()
                self.referring_doctor_view_dialog.save_and_cancel_btns.save_btn.hide()

                self.signals.globalLoadingNotificationControllerSignal.emit("VIEW_DOCTOR")
                self.referring_doctor_view_dialog.show()

    @pyqtSlot()
    @asyncSlot()
    async def show_add_referring_doctor_dialog(self):
        self.signals.globalCreateLoadingNotificationSignal.emit("VIEW_ADD_DOCTOR")
        add_referring_doctor_dialog_view = ReferringDoctorDialog("add", parent=self)
        await add_referring_doctor_dialog_view.populate_categories()

        add_referring_doctor_dialog_view.update_btn.hide()
        self.signals.globalLoadingNotificationControllerSignal.emit("VIEW_ADD_DOCTOR")
        add_referring_doctor_dialog_view.show()

    @pyqtSlot()
    @asyncSlot()
    async def edit_referring_doctor(self):
        if self.table_view.get_current_id():
            self.signals.globalCreateLoadingNotificationSignal.emit("GET_REFERRING_DOCTOR")

            data = await self.referring_doctor_controller.get_referring_doctor_by_id(self.table_view.get_current_id())
            if not data:
                self.signals.globalLoadingNotificationControllerSignal.emit("GET_REFERRING_DOCTOR")
                self.signals.globalCreateMessageNotificationSignal.emit({
                    "message_type": "error",
                    "message": "Error while getting referring_doctor data.",
                    "duration": 2000,
                })
            else:
                self.edit_referring_doctor_dialog_view = ReferringDoctorDialog("edit", parent=self)
                self.edit_referring_doctor_information_widget = self.edit_referring_doctor_dialog_view.form_widget

                await self.edit_referring_doctor_dialog_view.populate_categories()

                # referring_doctor Info.
                self.edit_referring_doctor_information_widget.first_name_input.setText(data["first_name"])
                self.edit_referring_doctor_information_widget.last_name_input.setText(data["last_name"])
                self.edit_referring_doctor_information_widget.category_combo.setCurrentText(data["category"])
                self.edit_referring_doctor_information_widget.specialty_input.setText(data["specialty"])
                self.edit_referring_doctor_information_widget.email_input.setText(data["email"])
                self.edit_referring_doctor_information_widget.phone_number_input.setText(data["phone_number"])
                self.edit_referring_doctor_information_widget.address_input.setText(data["address"])
                self.edit_referring_doctor_information_widget.notes_input.setText(data["address"])

                self.edit_referring_doctor_dialog_view.save_and_cancel_btns.save_btn.hide()

                self.signals.globalLoadingNotificationControllerSignal.emit("GET_REFERRING_DOCTOR")
                self.edit_referring_doctor_dialog_view.show()

    @pyqtSlot()
    @asyncSlot()
    async def delete_referring_doctor(self):
        if self.table_view.get_current_id():
            msg = QMessageBox()
            msg.setText('Are you sure you want to delete?')
            msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            reply = msg.exec()

            if reply == QMessageBox.StandardButton.Ok:
                self.signals.globalCreateLoadingNotificationSignal.emit("DELETE_referring_doctor")
                data = await self.referring_doctor_controller.delete_referring_doctor(self.table_view.get_current_id())
                if not data:
                    self.signals.globalCreateMessageNotificationSignal.emit({
                        "message_type": "error",
                        "message": "Could not delete referring_doctor.",
                        "duration": 3000,
                    })
                    self.signals.globalLoadingNotificationControllerSignal.emit("DELETE_referring_doctor")
                else:
                    await self.refresh_table()
                    self.signals.globalCreateMessageNotificationSignal.emit({
                        "message_type": "success",
                        "message": "referring_doctor successfully deleted",
                        "duration": 2000,
                    })
                self.signals.globalLoadingNotificationControllerSignal.emit("DELETE_referring_doctor")
