import asyncio

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QVBoxLayout, QSpacerItem, QSizePolicy
from PyQt6.QtGui import QCursor, QIcon

from services.supabase.controllers.clinic.clinic_controller import ClinicController
from services.supabase.controllers.image.image_controller import ImageController
from views.navbar.profile_component import Profile


class NavBar(QWidget):
    def __init__(self):
        super().__init__()

        self.profile_widget = None
        self.data = None
        self.clinic_controller = ClinicController()
        self.image_controller = ImageController()

        self.setFixedHeight(55)

        # Page Tab
        self.page_tab = QVBoxLayout()
        self.page_tab.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.page_tab.setContentsMargins(0, 0, 0, 0)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.setLayout(self.layout)
        asyncio.create_task(self.get_initial_data())

    async def get_initial_data(self):
        self.data = await self.clinic_controller.get_data()
        if self.data and self.data["logo_image_path"]:
            logo_file = await self.image_controller.get_image_from_storage(self.data["logo_image_path"])

            if logo_file:
                self.data["logo_image_data"] = logo_file
        self.setup_table_ui()

    def setup_table_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        horizontal_widget = QWidget()
        horizontal_widget.setObjectName("navbar_widget")
        horizontal_widget.setStyleSheet("QWidget#navbar_widget {border-bottom:1px solid #EAEDEA;}")

        start_spacer = QSpacerItem(56, 88, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        page_tab_notification_spacer = QSpacerItem(358, 88, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        notification_profile_spacer = QSpacerItem(53, 88, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        # Profile
        self.profile_widget = Profile(clinic_data=self.data)

        horizontal_layout = QHBoxLayout(horizontal_widget)
        horizontal_layout.setContentsMargins(30, 0, 10, 0)

        horizontal_layout.addLayout(self.page_tab)
        horizontal_layout.addSpacerItem(start_spacer)
        horizontal_layout.addSpacerItem(page_tab_notification_spacer)
        horizontal_layout.addSpacerItem(notification_profile_spacer)
        horizontal_layout.addWidget(self.profile_widget)

        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(horizontal_widget)

        self.layout.addLayout(main_layout)

