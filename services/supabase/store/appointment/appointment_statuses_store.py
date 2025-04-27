from PyQt6.QtCore import QObject


class AppointmentStatusesStore(QObject):

    def __init__(self):
        super().__init__()
        self._data = []
        self.status = {}

    def get_data(self):
        return self._data

    def set_data(self, data):
        self._data = data

    def get_status(self):
        return self.status

    def set_status(self, status):
        self.status = status
