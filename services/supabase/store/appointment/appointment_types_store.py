from PyQt6.QtCore import QObject


class AppointmentTypesStore(QObject):

    def __init__(self):
        super().__init__()
        self._data = []
        self.appointment_type = {}

    def get_data(self):
        return self._data

    def set_data(self, data):
        self._data = data

    def get_status(self):
        return self.appointment_type

    def set_status(self, appointment_type):
        self.appointment_type = appointment_type
