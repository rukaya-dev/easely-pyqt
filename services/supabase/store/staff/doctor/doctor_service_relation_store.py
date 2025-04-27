from PyQt6.QtCore import QObject


class DoctorServiceRelationStore(QObject):

    def __init__(self):
        super().__init__()
        self._data = []
        self._doctor_service_relation = {}
        self._search_text = ""
        self._filter_preferences = None
        self._search_data = []
        self._filtered_data = []

    def set_search_text(self, search_text):
        """Set the data """
        self._search_text = search_text

    def get_search_text(self):
        """Return the current data."""
        return self._search_text

    def get_filter_preferences(self):
        """Return the current data."""
        return self._filter_preferences

    def set_filter_preferences(self, filter_preferences):
        """Set the data """
        self._filter_preferences = filter_preferences

    def get_data(self):
        """Return the current data."""
        return self._data

    def set_data(self, data):
        """Set the data """
        self._data = data

    def get_filtered_data(self):
        """Return the current filtered data."""
        return self._filtered_data

    def set_filtered_data(self, filtered_data):
        """Set the filtered data """
        self._filtered_data = filtered_data

    def get_doctor_service_relation(self):
        """Return the current patient."""
        return self._doctor_service_relation

    def set_doctor_service_relation(self, doctor_service_relation):
        """Set the patient"""
        self._doctor_service_relation = doctor_service_relation

    def get_search_data(self):
        """Return the current data."""
        return self._search_data

    def set_search_data(self, data):
        """Set the data """
        self._search_data = data
