from PyQt6.QtCore import QObject


class UserStore(QObject):
    def __init__(self):
        super().__init__()
        self.data = {}
        self.user = {}

    def get_data(self):
        return self.data

    def set_data(self, data):
        self.data = data

    def set_user(self, user):
        self.user = user

    def get_user(self):
        return self.user
