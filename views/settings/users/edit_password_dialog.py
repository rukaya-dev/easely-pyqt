from qasync import asyncSlot

from views.componenets.customsComponents.table.form_componenets.custom_input import CustomLineEdit
from views.componenets.customsComponents.table.form_componenets.custom_label import CustomLabel
from PyQt6.QtCore import Qt, QSize, pyqtSlot
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QLabel

from loggers.logger_configs import set_up_logger
from services.supabase.controllers.settings.user_controller import UserController
from signals import SignalRepositorySingleton
from views.componenets.customsComponents.buttons.button_with_loader import ButtonWithLoader
from views.componenets.customsComponents.table.save_and_cancel_buttons import SaveAndCancelButtonsWithLoader

logger = set_up_logger('main.view.user_dialog')


class EditPasswordDialog(QDialog):

    def __init__(self, user_id, parent=None):
        super().__init__(parent)

        self.setStyleSheet("background-color:#f3f4f6;")

        self.parent = parent
        self.user_id = user_id

        self.user_controller = UserController()

        # Signals
        self.signals = SignalRepositorySingleton.instance()

        central_widget = QWidget(self)
        central_widget.setObjectName("central_widget")

        # # Vertical Layout for the Role data components
        main_data_vertical_layout = QVBoxLayout()
        main_data_vertical_layout.setContentsMargins(20, 20, 20, 20)

        self.form_widget = self.PasswordForm(parent=self)

        # # Controls Buttons for Adding User
        self.save_and_cancel_btns = SaveAndCancelButtonsWithLoader(text="Save")
        self.save_and_cancel_btns.save_btn.hide()
        self.save_and_cancel_btns.cancel_btn.clicked.connect(self.close)

        self.update_btn = ButtonWithLoader("Update", size=QSize(95, 34))
        self.update_btn.clicked.connect(self.update_password)
        self.disable_update_button()

        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)
        controls_layout.setContentsMargins(20, 20, 20, 20)
        controls_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        controls_layout.addWidget(self.save_and_cancel_btns)
        controls_layout.addWidget(self.update_btn)

        main_data_vertical_layout.addWidget(self.form_widget)

        main_vertical_layout = QHBoxLayout()
        main_vertical_layout.setContentsMargins(0, 0, 0, 0)

        main_vertical_layout.addLayout(main_data_vertical_layout)
        central_widget.setLayout(main_vertical_layout)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.layout.addWidget(central_widget, 1)
        self.layout.addLayout(controls_layout)
        self.setLayout(self.layout)

        self.setFixedSize(500, 380)

        self.setModal(True)

    @pyqtSlot()
    @asyncSlot()
    async def update_password(self):
        self.update_btn.start()
        try:
            await self.user_controller.update_password(self.user_id, self.form_widget.new_password_input.text())
        except Exception as e:
            self.signals.globalCreateMessageNotificationSignal.emit({
                "message_type": "error",
                "message": f"An unexpected error occurred: {e}",
                "duration": 2000,
            })
            logger.error(e, exc_info=True)
            self.update_btn.stop()
        finally:
            self.update_btn.stop()
            self.close()
            self.signals.globalCreateMessageNotificationSignal.emit({
                "message_type": "success",
                "message": "Password Successfully Updated.",
                "duration": 2000,
            })

    def enable_update_button(self):
        self.update_btn.setStyleSheet("""
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
        self.update_btn.setEnabled(True)

    def disable_update_button(self):
        self.update_btn.setStyleSheet("""
        QPushButton {
            border:0;
            border-radius:3px;
            font-size:13pt;
            background-color:#ebebeb;
            color:#a4a4a4;
        }
        """)
        self.update_btn.setDisabled(True)

    class PasswordForm(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)

            self.parent = parent

            new_password_label = CustomLabel(name="New Password")

            self.new_password_input = CustomLineEdit(placeholder_text="", parent=self)
            self.new_password_input.textChanged.connect(self.validate_new_password)
            self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)


            self.new_password_validation_error_msg_stylesheet = """
                color:#ef4444;
                font-weight:400;
                border:0;
            """
            self.password_validation_msg_stylesheet = """
                color:black;
                border:0;
            """

            self.new_password_validation_msg = QLabel()
            self.new_password_validation_msg.setAlignment(Qt.AlignmentFlag.AlignTop)
            self.new_password_validation_msg.setFixedHeight(30)
            self.new_password_validation_msg.setStyleSheet(self.password_validation_msg_stylesheet)

            new_password_vertical_layout = QVBoxLayout()
            new_password_vertical_layout.setSpacing(10)

            new_password_vertical_layout.addWidget(new_password_label)
            new_password_vertical_layout.addWidget(self.new_password_input)
            new_password_vertical_layout.addWidget(self.new_password_validation_msg)

            confirm_password_label = CustomLabel(name="Confirm Password")

            self.confirm_password_input = CustomLineEdit(placeholder_text="", parent=self)
            self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.confirm_password_input.setDisabled(True)
            self.confirm_password_input.textChanged.connect(self.validate_confirm_password)

            self.confirm_password_validation_msg = QLabel()
            self.confirm_password_validation_msg.setAlignment(Qt.AlignmentFlag.AlignTop)
            self.confirm_password_validation_msg.setFixedHeight(30)
            self.confirm_password_validation_msg.setStyleSheet(self.password_validation_msg_stylesheet)

            confirm_password_vertical_layout = QVBoxLayout()
            confirm_password_vertical_layout.setSpacing(10)

            confirm_password_vertical_layout.addWidget(confirm_password_label)
            confirm_password_vertical_layout.addWidget(self.confirm_password_input)
            confirm_password_vertical_layout.addWidget(self.confirm_password_validation_msg)

            layout = QVBoxLayout()
            layout.setContentsMargins(20, 20, 20, 0)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.setSpacing(10)

            layout.addLayout(new_password_vertical_layout)
            layout.addLayout(confirm_password_vertical_layout)

            self.setLayout(layout)

        @pyqtSlot(str)
        def validate_new_password(self, text):
            if len(text) < 6:
                self.set_validation_message(
                    self.new_password_validation_msg,
                    "password length must be at least 6 characters.",
                    self.new_password_validation_error_msg_stylesheet,
                    False
                )
                self.confirm_password_input.setDisabled(True)
            else:
                self.confirm_password_input.setDisabled(False)
                self.new_password_validation_msg.setText("")
                self.check_passwords_match()

        @pyqtSlot(str)
        def validate_confirm_password(self, text):
            self.check_passwords_match()

        def set_validation_message(self, label, message, stylesheet, enable_button):
            label.setText(message)
            label.setStyleSheet(stylesheet)
            if enable_button:
                self.parent.enable_update_button()
            else:
                self.parent.disable_update_button()

        def check_passwords_match(self):
            if self.new_password_input.text() != self.confirm_password_input.text():
                self.set_validation_message(
                    self.confirm_password_validation_msg,
                    "passwords do not match !",
                    self.new_password_validation_error_msg_stylesheet,
                    False
                )
            else:
                self.confirm_password_validation_msg.setText("")
                self.parent.enable_update_button()
