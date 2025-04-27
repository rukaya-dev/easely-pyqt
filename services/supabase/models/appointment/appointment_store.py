from PyQt6.QtCore import QObject


class AppointmentStore(QObject):

    def __init__(self):
        super().__init__()
        self._data = []
        self.appointment = {}

    def get_data(self):
        return self._data

    def set_data(self, data):
        self._data = data

    def get_appointment(self):
        return self.appointment

    def set_appointment(self, appointment):
        self.appointment = appointment
        self.appointment = appointment
