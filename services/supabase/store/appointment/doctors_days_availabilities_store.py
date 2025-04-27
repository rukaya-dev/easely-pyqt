from PyQt6.QtCore import QObject


class DoctorsDaysAvailabilitiesStore(QObject):

    def __init__(self):
        super().__init__()
        self._data = []
        self.available_doctor_days = {}

    def get_data(self):
        return self._data

    def set_data(self, data):
        self._data = data

    def get_available_doctor_days(self):
        return self.available_doctor_days

    def set_available_doctor_days(self, available_doctor_days):
        self.available_doctor_days = available_doctor_days
