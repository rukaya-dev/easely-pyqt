import datetime

from PyQt6.QtCore import QObject


class UserAuthStore(QObject):
    def __init__(self):
        super().__init__()
        self.data = {}
        self.user = {}
        self.is_authenticated = False
        self.is_authenticated_expired = None

    def get_data(self):
        return self.data

    def set_data(self, data):
        self.data = data

    def set_is_authenticated(self, data):
        self.is_authenticated = data
        if data:
            self.is_authenticated_expired = datetime.datetime.now() + datetime.timedelta(minutes=40)
        else:
            self.is_authenticated_expired = None

    def get_is_authenticated(self):
        # Check if the current time is before the expiration time
        if self.is_authenticated and self.is_authenticated_expired:
            if datetime.datetime.now() < self.is_authenticated_expired:
                return True
            else:
                # If the current time is after the expiration time, reset the authentication
                self.is_authenticated = False
                self.is_authenticated_expired = None
        return False

    def set_user(self, user):
        self.user = user

    def get_user(self):
        return self.user

