from PyQt6.QtWidgets import QMainWindow, QStackedWidget

from signals import SignalRepositorySingleton
from services.supabase.controllers.settings.user_auth_controller import UserAuthController
from views.layouts.user_auth_layout import UserAuthLayout
from views.layouts.user_layout import UserLayout


class MainWindowView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(1920, 1080)
        self.installEventFilter(self)
        self.stacked_content_widget = QStackedWidget()
        self.signals = SignalRepositorySingleton.instance()
        self.signals.signalForUserLayout.connect(self.show_user_layout)
        self.signals.signalForUserAuthLayout.connect(self.show_user_auth_layout)
        self.user_layout = None
        self.user_auth_layout = None

        self.setCentralWidget(self.stacked_content_widget)
        self.user_auth_controller = UserAuthController()

    async def check_user_authentication(self):
        # check if a user exists (logged in before)
        user_exist = self.user_auth_controller.check_if_user_exist()
        if not user_exist:
            self.signals.signalForUserAuthLayout.emit(True)
        else:
            # check user session
            res = await self.user_auth_controller.check_user_token()
            if not res:
                self.signals.signalForUserAuthLayout.emit(True)
            else:
                self.signals.signalForUserLayout.emit(True)

    def set_main_content(self, content_widget):
        self.stacked_content_widget.addWidget(content_widget)
        self.stacked_content_widget.setCurrentWidget(content_widget)

    def show_user_layout(self):
        self.user_layout = UserLayout()
        self.set_main_content(self.user_layout)

    def show_user_auth_layout(self):
        self.user_auth_layout = UserAuthLayout()
        self.set_main_content(self.user_auth_layout)
