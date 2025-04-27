from PyQt6.QtCore import QObject


class DoctorsTimeSlotsAvailabilitiesStore(QObject):

    def __init__(self):
        super().__init__()
        self._data = []
        self._available_doctor_time_slot = {}

    def get_data(self):
        """Return the current data."""
        return self._data

    def set_data(self, data):
        """Set the data """
        self._data = data

    def get_available_doctor_time_slot(self):
        """Return the current patient."""
        return self._available_doctor_time_slot

    def set_available_doctor_time_slot(self, available_doctor_time_slot):
        """Set the patient"""
        self._available_doctor_time_slot = available_doctor_time_slot
