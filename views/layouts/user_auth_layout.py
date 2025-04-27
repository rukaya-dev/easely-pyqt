from PyQt6.QtWidgets import QWidget, QHBoxLayout

from views.login.login_view import LoginView


class UserAuthLayout(QWidget):
    def __init__(self):
        super().__init__()
        self.login_view = LoginView()

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        main_layout.addWidget(self.login_view)
        self.setLayout(main_layout)
