import requests
from PyQt6.QtCore import QObject, pyqtSignal


class CategoryStore(QObject):

    def __init__(self):
        super().__init__()
        self._data = []
        self._category = {}
        self._search_data = []
        self._search_text = ""

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


    def get_category(self):
        """Return the current data."""
        return self._category

    def set_category(self, category):
        """Set the category"""
        self._category = category

    def get_search_data(self):
        """Return the current data."""
        return self._search_data

    def set_search_data(self, data):
        """Set the data and emit the dataChanged signal."""
        self._search_data = data

    @property
    def get(self):
        return self._get
