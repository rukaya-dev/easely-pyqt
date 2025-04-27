import datetime
import re

from PyQt6.QtCore import Qt, pyqtSlot, QSize
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QWidget, QMessageBox, QSpacerItem, QSizePolicy
from qasync import asyncSlot

from configs.supa_base_configs import SUPER_ADMIN_EMAIL
from loggers.logger_configs import set_up_logger
from services.supabase.controllers.settings.user_controller import UserController
from signals import SignalRepositorySingleton
from views.componenets.customsComponents.buttons.button_with_loader import ButtonWithLoader
from views.componenets.customsComponents.table.save_and_cancel_buttons import SaveAndCancelButtonsWithLoader
from views.settings.users.user_form import UserForm

logger = set_up_logger('main.view.user_dialog')


class UserDialog(QDialog):

    def __init__(self, action_type, parent=None):
        super().__init__(parent)

        self.action_type = action_type

        self.setStyleSheet("background-color:#f3f4f6;")

        self.parent = parent
        self.is_data_widget = None

        self.user_controller = UserController()

        # Signals
        self.signals = SignalRepositorySingleton.instance()

        central_widget = QWidget(self)
        central_widget.setObjectName("central_widget")

        # # Vertical Layout for the Role data components
        main_data_vertical_layout = QVBoxLayout()
        main_data_vertical_layout.setContentsMargins(20, 20, 20, 20)

        # Data Component
        self.form_widget = UserForm()

        # # Controls Buttons for Adding User
        self.save_and_cancel_btns = SaveAndCancelButtonsWithLoader(text="Save")
        self.save_and_cancel_btns.save_btn.clicked.connect(self.add_new_user)
        self.save_and_cancel_btns.cancel_btn.clicked.connect(self.close)

        self.update_btn = ButtonWithLoader("Update", size=QSize(95, 34))
        self.update_btn.setObjectName("update_save_btn")
        self.update_btn.clicked.connect(self.update_user)

        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)
        controls_layout.setContentsMargins(20, 50, 20, 20)
        controls_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        controls_layout.addWidget(self.save_and_cancel_btns)
        controls_layout.addWidget(self.update_btn)

        main_data_vertical_layout.addWidget(self.form_widget)

        spacer = QSpacerItem(10, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        main_vertical_layout = QHBoxLayout()
        main_vertical_layout.setContentsMargins(0, 0, 0, 0)

        main_vertical_layout.addLayout(main_data_vertical_layout)
        main_vertical_layout.addSpacerItem(spacer)
        central_widget.setLayout(main_vertical_layout)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.layout.addWidget(central_widget)
        self.layout.addLayout(controls_layout)
        self.setLayout(self.layout)

        self.setModal(True)

    def close_pop_up(self):
        self.close()

    def validate_data(self, action):
        email = self.form_widget.email_input.text()
        user_role = self.form_widget.role_comboBox.currentText()
        first_name = self.form_widget.firstname_input.text()
        if not email:
            QMessageBox.warning(self, "Warning", "E-mail is required.")
            return False

        if not user_role:
            QMessageBox.warning(self, "Warning", "User Role is required")
            return False

        if not first_name:
            QMessageBox.warning(self, "Warning", "User First name is required")
            return False

        if not re.match("[^@]+@[^@]+\.[^@]+", self.form_widget.email_input.text()):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("Invalid email address")
            msg.setInformativeText("format: username@gmail.com")
            msg.exec()
            return False

        if action == "create":
            password = self.form_widget.password_input.text()
            if not password:
                QMessageBox.warning(self, "Warning", "Password is required.")
                return False

            if len(password) < 6:
                QMessageBox.warning(self, "Warning", "Password should be at least 6 characters.")
                return False

        return True

    @pyqtSlot()
    @asyncSlot()
    async def add_new_user(self):
        if self.validate_data("create"):
            form_insert_data = {
                "email": self.form_widget.email_input.text(),
                "password": self.form_widget.password_input.text(),
                "options": {
                    "data": {
                        "first_name": self.form_widget.firstname_input.text(),
                        "last_name": self.form_widget.lastname_input.text(),
                        "username": '',
                        "user_role": self.form_widget.role_comboBox.currentText(),
                        "image_id": 1
                    }
                },
            }
            self.save_and_cancel_btns.save_btn.start()

            users_data = self.user_controller.store.get_data()
            is_exist = [user for user in users_data["data"] if user["email"] == self.form_widget.email_input.text()]
            if is_exist:
                QMessageBox.warning(None, "Warning", f"""User with email {form_insert_data["email"]} already exist.""")
                self.save_and_cancel_btns.save_btn.stop()
            else:
                try:
                    # Attempt to execute some async operation
                    await self.user_controller.create_user(form_insert_data)
                except Exception as e:
                    self.signals.globalCreateMessageNotificationSignal.emit({
                        "message_type": "error",
                        "message": f"An unexpected error occurred: {e}",
                        "duration": 2000,
                    })
                    logger.error(e, exc_info=True)
                    self.save_and_cancel_btns.save_btn.stop()
                finally:
                    await self.parent.refresh_table()

                    self.save_and_cancel_btns.save_btn.stop()
                    self.close()
                    self.signals.globalCreateMessageNotificationSignal.emit({
                        "message_type": "success",
                        "message": "User Successfully Added",
                        "duration": 2000,
                    })

    @pyqtSlot()
    @asyncSlot()
    async def update_user(self):
        if self.validate_data("update"):
            form_insert_data = {
                "email": self.form_widget.email_input.text(),
                "options": {
                    "data": {
                        "first_name": self.form_widget.firstname_input.text(),
                        "last_name": self.form_widget.lastname_input.text(),
                        "username": '',
                        "user_role": self.form_widget.role_comboBox.currentText(),
                        "image_id": 1
                    }
                },
                'updated_at': datetime.datetime.now().isoformat()

            }
            self.update_btn.start()

            current_user = self.user_controller.store.get_user()
            email = self.form_widget.email_input.text()
            is_exist = self.check_email_exist(email, current_user["id"])

            if is_exist:
                QMessageBox.warning(None, "Warning", f"""User with email {form_insert_data["email"]} already exist.""")
                self.update_btn.stop()
            else:
                try:
                    # Attempt to execute some async operation
                    await self.user_controller.update_user(self.parent.table_view.current_id, form_insert_data)
                except Exception as e:
                    self.signals.globalCreateMessageNotificationSignal.emit({
                        "message_type": "error",
                        "message": f"An unexpected error occurred: {e}",
                        "duration": 2000,
                    })
                    logger.error(e, exc_info=True)
                    self.update_btn.stop()
                finally:
                    await self.parent.refresh_table()
                    self.update_btn.stop()
                    self.close()
                    self.signals.globalCreateMessageNotificationSignal.emit({
                        "message_type": "success",
                        "message": "User Successfully Updated",
                        "duration": 2000,
                    })

    def check_email_exist(self, email, user_id):

        if email == SUPER_ADMIN_EMAIL:
            return True

        users_data = self.user_controller.store.get_data()

        email_exists_among_others = any(
            user["email"] == email and user["id"] != user_id for user in users_data["data"])

        if not email_exists_among_others:
            return False

        return True

    def toggle_inputs_state(self, action):
        if action == "view":
            # set ReadOnly
            self.form_widget.firstname_input.setReadOnly(True)
            self.form_widget.lastname_input.setReadOnly(True)
            self.save_and_cancel_btns.save_btn.hide()
            self.update_btn.hide()

            self.form_widget.firstname_input.setReadOnly(True)
            self.form_widget.lastname_input.setReadOnly(True)
            self.form_widget.email_input.setReadOnly(True)
            self.form_widget.role_comboBox.setDisabled(True)
        else:
            self.save_and_cancel_btns.save_btn.hide()

        self.form_widget.password_input.hide()
        self.form_widget.password_label.hide()
