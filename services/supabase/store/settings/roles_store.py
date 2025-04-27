import requests
from PyQt6.QtCore import QObject, pyqtSignal


class RolesStore(QObject):
    def __init__(self):
        super().__init__()
        self._data = []
        self._role = {}
        self._search_data = []

    def get_data(self):
        """Return the current data."""
        return self._data

    def set_data(self, data):
        """Set the data """
        self._data = data

    def get_role(self):
        """Return the current role."""
        return self._role

    def set_role(self, role):
        """Set the role"""
        self._role = role

    def get_search_data(self):
        """Return the current data."""
        return self._search_data

    def set_search_data(self, data):
        """Set the data """
        self._search_data = data

    @property
    def get(self):
        return self._get
