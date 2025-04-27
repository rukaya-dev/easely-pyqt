import json
import mimetypes
import os

from PyQt6.QtCore import QSize, pyqtSignal, Qt
from PyQt6.QtGui import QIcon, QAction, QPixmap
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QMenu, QPushButton
from qasync import asyncSlot

from loggers.logger_configs import set_up_logger
from signals import SignalRepositorySingleton
from views.componenets.customsComponents.circular_avatar import mask_image
from views.componenets.customsComponents.menus.drop_down_menu_component import CustomDropDownMenuComponent
from utils.utlis import trim_text, extract_file_extension
from services.supabase.controllers.settings.user_auth_controller import UserAuthController

logger = set_up_logger('main.views.navbar.profile_component')


class Profile(QWidget):
    userLoggedOut = pyqtSignal()

    def __init__(self, clinic_data, parent=None):
        super().__init__(parent)

        self.clinic_data = clinic_data

        self.toggle_menu_button = None
        self.profile_drop_down_widget = None

        self.drop_down_menu = None
        self.sign_out_action = None
        self.settings_action = None

        self.avatar = None
        self.user_role = None
        self.username_label = None

        self.username = "User"

        self.user_auth_controller = UserAuthController()

        self.set_up_ui()

        # Signals
        self.signals = SignalRepositorySingleton.instance()
        self.signals.signalForUserLayout.connect(self.set_user_info)

    def set_up_ui(self):
        profile_menu = QMenu()

        profile_menu.setStyleSheet("""
                      QMenu {
                          border: 1px solid #A1AEB4;
                          padding:0;
                          color:black;
                      }
                      QMenu::item {
                          padding-bottom:10px;
                          padding-top:10px;
                          padding-left:30px;
                      }
                      QMenu::icon {
                          padding-left: 20px;
                      }
                      QMenu::item:selected {
                          background-color:#ebf2f8;
                      }
                     QMenu::separator {
                          height: 1px;
                          background: #A1AEB4; /* Gray color */

                      }
                      """)
        profile_menu.setFixedSize(150, 45)

        sign_out_action = QAction(QIcon(":/resources/icons/sign_out.svg"), "Sign out", self)

        sign_out_action.triggered.connect(self.sign_out_user)

        profile_menu.addAction(sign_out_action)

        self.toggle_menu_button = QPushButton()

        self.toggle_menu_button.setStyleSheet("""
            QPushButton {
                border:0;
                background-color:transparent;
            }
            """)

        icon_pixmap = QPixmap(":resources/icons/expand_more.svg")
        icon = QIcon(icon_pixmap)

        self.toggle_menu_button.setIcon(icon)
        self.toggle_menu_button.setIconSize(QSize(15, 15))
        self.setFixedSize(QSize(150, 30))

        self.drop_down_menu = CustomDropDownMenuComponent(menu_button=self.toggle_menu_button,
                                                          menu_pos="bottom-left",
                                                          menu_widget=profile_menu)

        self.setFixedSize(QSize(182, 50))

        profile_layout = QHBoxLayout(self)
        profile_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        profile_layout.setContentsMargins(0, 0, 0, 0)

        self.avatar = QLabel()
        self.avatar.setFixedHeight(35)

        names_layout = QVBoxLayout()
        names_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        names_layout.setContentsMargins(10, 10, 10, 10)

        self.username_label = QLabel(self)
        self.username_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.username_label.setText(trim_text(self.username))
        self.username_label.setMinimumHeight(20)
        self.username_label.setStyleSheet("color:#3E3E3F;")

        user_name_font = self.username_label.font()
        user_name_font.setPointSize(10)
        user_name_font.setWeight(user_name_font.Weight.Medium)
        self.username_label.setFont(user_name_font)

        self.user_role = QLabel("Admin Manager", self)
        self.user_role.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.user_role.setMinimumHeight(20)
        # self.user_role.setFixedSize(QSize(100, 20))
        self.user_role.setStyleSheet("color:#A3A4A6;")

        user_role_font = self.username_label.font()
        user_role_font.setPointSize(9)
        user_role_font.setWeight(user_role_font.Weight.Medium)
        self.user_role.setFont(user_role_font)

        names_layout.addWidget(self.username_label)
        names_layout.addWidget(self.user_role)

        profile_layout.addLayout(names_layout)
        profile_layout.addWidget(self.avatar)
        profile_layout.addWidget(self.drop_down_menu)

        self.setLayout(profile_layout)
        self.set_user_info()
        self.set_clinic_data()

    def set_user_info(self):
        user = self.user_auth_controller.user_auth_store.get_user()
        if user:
            role_json_data = json.loads(user["role"])
            self.username_label.setText(trim_text(user["first_name"] + " " + user["last_name"]))
            self.user_role.setText(role_json_data["role_name"])
            self.username_label.update()
            self.user_role.update()

    def set_clinic_data(self):
        if not self.clinic_data or not self.clinic_data.get("logo_image_path"):

            logo_data = {'file_path': '',
                         'image_type': "jpg",
                         "file": None,
                         "mime_type": 'jpg'
                         }

        else:
            mime_type, _ = mimetypes.guess_type(self.clinic_data["logo_image_path"])
            file_extension = extract_file_extension(self.clinic_data["logo_image_path"])

            logo_data = {'file_path': self.clinic_data["logo_image_path"],
                         'image_type': file_extension,
                         "file": self.clinic_data["logo_image_data"],
                         "mime_type": mime_type
                         }

        pixmap = mask_image(logo_data["file"], size=35, img_type=logo_data["image_type"].replace(".", ""),
                            border=True, border_color="#E9E9E9")

        self.avatar.setPixmap(pixmap)

    def redirect_to_settings(self):
        self.drop_down_menu.menu.close()
        self.signals.setSideBarButtonActive.emit("settings_button")

    @asyncSlot()
    async def sign_out_user(self):
        self.signals.globalCreateLoadingNotificationSignal.emit("LOG_OUT")
        try:
            await self.user_auth_controller.sign_out_user()
            self.signals.signalForUserAuthLayout.emit(True)
        except Exception as e:
            logger.error(e, exc_info=True)
            self.signals.globalCreateLoadingNotificationSignal.emit("LOG_OUT")
            self.signals.signalForUserAuthLayout.emit(True)

        self.drop_down_menu.menu.close()
