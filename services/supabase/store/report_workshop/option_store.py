import requests
from PyQt6.QtCore import QObject, pyqtSignal


class OptionStore(QObject):

    def __init__(self):
        super().__init__()
        self._data = []
        self._option = {}
        self._search_data = []
        self._search_text = ""
        self._filter_preferences = None

        self._get = {
            'isSuccess': False,
            'isError': False,
            'message': '',
        }
        self._search_get = {
            'isSuccess': False,
            'isError': False,
            'message': '',
        }

    def get_data(self):
        """Return the current data."""
        return self._data

    def set_data(self, data):
        """Set the data"""
        self._data = data

    def set_search_text(self, search_text):
        """Set the data """
        self._search_text = search_text

    def get_search_text(self):
        """Return the current data."""
        return self._search_text

    def get_option(self):
        """Return the current data."""
        return self._option

    def set_option(self, category):
        """Set the category"""
        self._option = category

    def get_search_data(self):
        """Return the current data."""
        return self._search_data

    def set_search_data(self, data):
        """Set the data and emit the dataChanged signal."""
        self._search_data = data

    def get_filter_preferences(self):
        """Return the current data."""
        return self._filter_preferences

    def set_filter_preferences(self, filter_preferences):
        """Set the data """
        self._filter_preferences = filter_preferences

    @property
    def get(self):
        return self._get
