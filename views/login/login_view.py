from PyQt6.QtCore import QSize, Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QMessageBox
from PyQt6 import QtWidgets
import re

from qasync import asyncSlot

from signals import SignalRepositorySingleton
from services.supabase.controllers.settings.user_auth_controller import UserAuthController
from utils.validator import email_validator
from views.componenets.customsComponents.buttons.button_with_loader import ButtonWithLoader
from views.componenets.customsComponents.loaders.internal_loader import InternalLoader
from views.login.login_custom_email_line_edit import LoginCustomLineEditWithIcon


class LoginView(QWidget):
    loginCompleted = pyqtSignal(object)

    def __init__(self):
        super().__init__()

        self.email = ''
        self.password = ''

        self.setObjectName("login_widget")

        self.signals = SignalRepositorySingleton.instance()
        self.user_controller = UserAuthController()

        font = QFont()
        font.setPointSize(16)

        self.logo = QLabel()
        self.logo.setObjectName("logo")
        self.logo.setStyleSheet("background-color: transparent; padding:10px;color:black;")

        logo_path = QPixmap(":/resources/images/application_icon.png")
        self.logo.setPixmap(logo_path)
        self.logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        login_label = QLabel()
        login_label.setStyleSheet("border:0;color:black;")
        login_label.setText("Sign in")
        login_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        login_font = login_label.font()
        login_font.setPointSize(30)
        login_font.setWeight(login_font.Weight.DemiBold)
        login_label.setFont(login_font)

        login_label_layout = QVBoxLayout()
        login_label_layout.setContentsMargins(20, 20, 20, 20)
        login_label_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        login_label_layout.addWidget(self.logo)
        login_label_layout.addWidget(login_label)
        # ---------------------------------------

        self.email_input = LoginCustomLineEditWithIcon(":/resources/icons/mail.svg", placeholder_text="E-mail")
        self.email_input.line_edit.setValidator(email_validator)

        self.password_input = LoginCustomLineEditWithIcon(":/resources/icons/lock.svg", placeholder_text="password")
        self.password_input.line_edit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)

        email_password_layout = QVBoxLayout()
        email_password_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        email_password_layout.addWidget(self.email_input)
        email_password_layout.addWidget(self.password_input)
        # ---------------------------------------

        self.login_btn = ButtonWithLoader(text="Sign in", size=QSize(314, 45), parent=self)
        self.login_btn.setStyleSheet("""
            QPushButton {
                border:0;
                border-radius:3px;
                font-size:13pt;
                font-weight:bold;
                background-color:#282624;
                color:white;
            }
            QPushButton:pressed {
                border:0;
                border-radius:3px;
                font-size:13pt;
                font-weight:bold;
                color:white
                padding-top: 2px;
                padding-left: 2px;
            }
        
        """)
        self.login_btn.clicked.connect(self.sign_in)

        login_btn_layout = QHBoxLayout()
        login_btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        login_btn_layout.addWidget(self.login_btn)

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(login_label_layout)
        layout.addLayout(email_password_layout)
        layout.addLayout(login_btn_layout)

        self.setFixedSize(1366, 768)
        self.setStyleSheet("""
        QWidget#login_widget {
          background-color: white;
        }
        """)
        self.setLayout(layout)

    @asyncSlot()
    async def sign_in(self):
        if self.validate() and self.validate_email_address():
            email = self.email_input.line_edit.text()
            password = self.password_input.line_edit.text()
            self.login_btn.start()

            self.login_btn.setText("")
            self.login_btn.setEnabled(
                False)

            res = await self.user_controller.login_user(email, password)
            if res["status_code"] == 400:
                self.on_invalid_login_credentials_error(res["message"])
            elif res["status_code"] == 500:
                self.on_invalid_login_credentials_error(res["message"])
            elif res["status_code"] == 200:
                self.on_login_task_completed()

        self.login_btn.setEnabled(True)
        self.login_btn.setText("Sign in")
        self.login_btn.stop()

    @pyqtSlot(str)
    def on_login_task_completed(self):
        self.user_controller.get_user_profile_data()
        self.signals.signalForUserLayout.emit(True)

    @pyqtSlot(str)
    def on_invalid_login_credentials_error(self, message):
        self.login_btn.setEnabled(True)
        self.login_btn.setText("Sign in")
        QMessageBox.critical(self, "Error", message)

    def validate_email_address(self):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", self.email_input.line_edit.text()):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("Invalid email address")
            msg.setInformativeText("format: username@gmail.com")
            msg.exec()
            return
        return True

    def validate(self):
        if not self.email_input.line_edit.text():
            QMessageBox.warning(self, "Warning", "Email is required")
            return None

        if not self.password_input.line_edit.text():
            QMessageBox.warning(self, "Warning", "Password is required")
            return None

        return True


class LoginButton(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("login_btn_widget")

        self.btn = QPushButton()
        self.btn.setFixedSize(300, 40)
        self.btn.setText("Sign in")
        self.btn.setStyleSheet("""
        QPushButton {
            border:0;
            color:black;
            background-color:transparent;
        }
        """)

        login_font = self.btn.font()
        login_font.setPointSizeF(16)
        self.btn.setFont(login_font)

        self.internal_loader = InternalLoader(height=20, parent=self)

        login_btn_layout = QHBoxLayout()
        login_btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        login_btn_layout.addWidget(self.internal_loader)
        login_btn_layout.addWidget(self.btn)

        widget = QWidget()
        widget.setStyleSheet("""
        QWidget {
            border:0;
            border-radius:7px;
            background-color:red;
        }
        """)
        widget.setLayout(login_btn_layout)

        self.internal_loader.start()

        layout = QVBoxLayout()
        layout.addWidget(widget)

        self.setLayout(layout)
