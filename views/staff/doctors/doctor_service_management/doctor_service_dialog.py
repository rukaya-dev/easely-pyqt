import datetime
import json

from PyQt6.QtCore import Qt, pyqtSlot, QSize
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QWidget, QMessageBox, QSpacerItem, QSizePolicy
from qasync import asyncSlot

from loggers.logger_configs import set_up_logger
from services.supabase.controllers.settings.log_controller import LogController
from services.supabase.controllers.staff.assistant.doctor_service_assistants_controller import \
    DoctorServiceAssistantsRelationController
from services.supabase.controllers.staff.doctor.doctor_schedule_controller import DoctorScheduleController
from services.supabase.controllers.staff.doctor.doctor_service_relation_controller import \
    DoctorServiceRelationController
from services.supabase.controllers.settings.user_auth_controller import UserAuthController
from signals import SignalRepositorySingleton
from views.componenets.customsComponents.buttons.button_with_loader import ButtonWithLoader
from views.componenets.customsComponents.custom_scroll_area import CustomScrollArea
from views.componenets.customsComponents.table.save_and_cancel_buttons import SaveAndCancelButtonsWithLoader
from views.staff.doctors.doctor_service_management.doctor_service_form import DoctorServiceForm

logger = set_up_logger('main.views.staff.doctors.doctor_service_management.doctor_service_dialog')


class DoctorServiceDialog(QDialog):
    def __init__(self, action_type, parent=None):
        super().__init__(parent)

        self.action_type = action_type
        self.setStyleSheet("background-color:#f3f4f6;")

        self.parent = parent
        self.generated_time_slots = None

        self.error_message = "An error occurred while creating, please contact your service provider."

        self.doctor_service_controller = DoctorServiceRelationController()
        self.doctor_schedule_controller = DoctorScheduleController()
        self.doctor_service_assistants_controller = DoctorServiceAssistantsRelationController()

        self.log_controller = LogController()
        self.user_auth_controller = UserAuthController()
        self.auth_user = self.user_auth_controller.user_auth_store.get_user()

        # Signals
        self.signals = SignalRepositorySingleton.instance()

        central_widget = QWidget(self)
        central_widget.setObjectName("central_widget")

        main_doctor_data_vertical_layout = QVBoxLayout()
        main_doctor_data_vertical_layout.setContentsMargins(0, 0, 0, 0)

        self.form_widget = DoctorServiceForm(self.action_type, parent=self)

        self.save_and_cancel_btns = SaveAndCancelButtonsWithLoader(text="Save")
        self.save_and_cancel_btns.save_btn.clicked.connect(self.add_new_doctor_service_relation)
        self.save_and_cancel_btns.cancel_btn.clicked.connect(self.close)

        self.update_btn = ButtonWithLoader("Update", size=QSize(95, 34))
        self.update_btn.clicked.connect(self.update_doctor_service_relation)

        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)
        controls_layout.setContentsMargins(20, 20, 20, 20)
        controls_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        controls_layout.addWidget(self.save_and_cancel_btns)
        controls_layout.addWidget(self.update_btn)

        main_doctor_data_vertical_layout.addWidget(self.form_widget)

        main_vertical_layout = QHBoxLayout()
        main_vertical_layout.setContentsMargins(0, 0, 0, 0)

        spacer = QSpacerItem(10, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        main_vertical_layout.addLayout(main_doctor_data_vertical_layout)
        main_vertical_layout.addSpacerItem(spacer)

        central_widget.setLayout(main_vertical_layout)

        scroll_area = CustomScrollArea(self)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setWidget(central_widget)

        self.v_scrollbar = scroll_area.verticalScrollBar()
        self.signals.doctorServiceFormWidgetNewContentIsAddedSignal.connect(self.scroll_to_bottom_if_needed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 5, 20)
        layout.addWidget(scroll_area)
        layout.addLayout(controls_layout)

        self.setLayout(layout)

        self.setMinimumWidth(800)
        self.setMinimumHeight(600)

    def validate_data(self):
        doctor_service_cost = self.form_widget.cost_input.text()
        duration = self.form_widget.duration_input.text()
        days_widget_and_time_slots_data = self.form_widget.days_widget_and_time_slots_widget.get_days_and_time_slots_data()
        assistants_data = self.form_widget.assistants_selection_widget.selected_assistants_content_widgets.selected_assistants_data

        if not doctor_service_cost:
            QMessageBox.warning(self, "Warning", "Service cost is required.")
            return False

        if not duration or duration == ' ':
            QMessageBox.warning(self, "Warning", "Service duration range is required.")
            return False

        if not days_widget_and_time_slots_data:
            QMessageBox.warning(self, "Warning", "Doctor days and time slots are required.")
            return False

        if not assistants_data:
            QMessageBox.warning(self, "Warning", "Doctor Service Assistants are required.")
            return False

        return True

    @pyqtSlot()
    def scroll_to_bottom_if_needed(self):
        assistants_widget_geometry = self.form_widget.assistants_widget.geometry()
        self.v_scrollbar.setValue(assistants_widget_geometry.bottom())

    def scroll_top(self):
        form_widget_geometry = self.form_widget.geometry()
        self.v_scrollbar.setValue(form_widget_geometry.top())

    @pyqtSlot()
    @asyncSlot()
    async def add_new_doctor_service_relation(self):
        def show_error_message():
            msg = QMessageBox()
            msg.setText('Could not create a new doctor service')
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setDetailedText(self.error_message)
            msg.exec()

        if not self.validate_data():
            return

        self.save_and_cancel_btns.save_btn.start()
        doctor_service_data = self.get_doctor_service_data()
        print(doctor_service_data)
        res = await self.doctor_service_controller.create_doctor_service_relation(doctor_service_data)

        if not res:
            self.save_and_cancel_btns.save_btn.stop()
            show_error_message()
            return

        doctor_schedule_data = {
            "doctor_id": self.parent.doctor_id,
            "doctor_service_relation_id": res["doctor_service_relation_id"],
        }
        days_and_time_slots_data = self.form_widget.days_widget_and_time_slots_widget.get_days_and_time_slots_data()
        doctor_service_assistants_data = self.form_widget.assistants_selection_widget.selected_assistants_content_widgets.selected_assistants_data

        try:
            for item in days_and_time_slots_data:
                item.update(doctor_schedule_data)
                print(item)
                await self.doctor_schedule_controller.create_doctor_schedule(item)

            for item_id in doctor_service_assistants_data:
                item_data = {
                    "doctor_service_relation_id": res["doctor_service_relation_id"],
                    "assistant_id": item_id,
                }
                print(item_data)
                await self.doctor_service_assistants_controller.create_doctor_service_assistants_relation(item_data)

            await self.parent.refresh_table()
            self.close()
            msg = QMessageBox()
            msg.setText('Doctor service successfully created.')
            msg.setIcon(QMessageBox.Icon.Information)
            msg.exec()
        except Exception as e:
            logger.error(e)
            show_error_message()
        finally:
            self.save_and_cancel_btns.save_btn.stop()

    @pyqtSlot()
    @asyncSlot()
    async def update_doctor_service_relation(self):
        if self.validate_data():
            doctor_service_data = self.get_doctor_service_data()
            self.update_btn.start()

            modified_data = {"updated_at": datetime.datetime.now().isoformat()}
            modified_data.update(doctor_service_data)

            res = await self.doctor_service_controller.update_doctor_service_relation(
                self.parent.table_view.get_current_id(),
                modified_data)
            if not res:
                msg = QMessageBox()
                msg.setText('Could not update doctor service')
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.setDetailedText("error occurred while updating, please contact your service provider.")
                msg.exec()
                self.update_btn.stop()
            else:
                doctor_schedule_data = {
                    "doctor_id": self.parent.doctor_id,
                    "doctor_service_relation_id": res["doctor_service_relation_id"],
                }
                deleted_res = await self.doctor_schedule_controller.delete_doctor_schedule(doctor_schedule_data)
                if not deleted_res:
                    self.save_and_cancel_btns.save_btn.stop()
                    msg = QMessageBox()
                    msg.setText('Could not update doctor service')
                    msg.setIcon(QMessageBox.Icon.Critical)
                    msg.setDetailedText("error occurred while updating, please contact your service provider.")
                    msg.exec()
                else:
                    days_and_time_slots_data = self.form_widget.days_widget_and_time_slots_widget.get_days_and_time_slots_data()
                    try:
                        for item in days_and_time_slots_data:
                            item.update(doctor_schedule_data)
                            await self.doctor_schedule_controller.create_doctor_schedule(item)
                    except Exception as e:
                        self.save_and_cancel_btns.save_btn.stop()
                        msg = QMessageBox()
                        msg.setText('Could not update doctor service')
                        msg.setIcon(QMessageBox.Icon.Critical)
                        msg.setDetailedText("error occurred while updating, please contact your service provider.")
                        msg.exec()
                        logger.error(e)
                    finally:
                        deleted_res = await self.doctor_service_assistants_controller.delete_doctor_service_assistants_relation(res["doctor_service_relation_id"])
                        if not deleted_res:
                            self.save_and_cancel_btns.save_btn.stop()
                            msg = QMessageBox()
                            msg.setText('Could not update doctor service')
                            msg.setIcon(QMessageBox.Icon.Critical)
                            msg.setDetailedText("error occurred while updating, please contact your service provider.")
                            msg.exec()
                        else:
                            # Insert Doctor Service Assistants
                            doctor_service_assistants_data = self.form_widget.assistants_selection_widget.selected_assistants_content_widgets.selected_assistants_data
                            try:
                                for item_id in doctor_service_assistants_data:
                                    item_data = {
                                        "doctor_service_relation_id": res["doctor_service_relation_id"],
                                        "assistant_id": item_id,
                                    }

                                    await self.doctor_service_assistants_controller.create_doctor_service_assistants_relation(
                                        item_data)
                            except Exception as e:
                                self.save_and_cancel_btns.save_btn.stop()
                                msg = QMessageBox()
                                msg.setText('Could not update doctor service')
                                msg.setIcon(QMessageBox.Icon.Critical)
                                msg.setDetailedText(
                                    "error occurred while updating, please contact your service provider.")
                                msg.exec()
                                logger.error(e)
                            finally:
                                await self.parent.refresh_table()
                                self.update_btn.stop()
                                self.close()
                                msg = QMessageBox()
                                msg.setText('Doctor service successfully updated.')
                                msg.setIcon(QMessageBox.Icon.Information)
                                msg.exec()

    def get_doctor_service_data(self):
        return {
            "doctor_id": self.parent.doctor_id,
            "service_name": self.form_widget.service_name_selection_widget.currentText(),
            "doctor_service_cost": self.form_widget.cost_input.text(),
            "doctor_service_duration": self.form_widget.duration_input.text(),
            "doctor_service_status": self.form_widget.status_selection_widget.currentText(),
            "additional_data": json.dumps(self.form_widget.additional_data_input.toPlainText())
        }
