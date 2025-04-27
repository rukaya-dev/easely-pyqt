import requests
from PyQt6.QtCore import QObject


class TemplateStore(QObject):

    def __init__(self):
        super().__init__()
        self._data = []
        self._template = {}
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
        return self._data

    def set_data(self, data):
        self._data = data

    def set_search_text(self, search_text):
        self._search_text = search_text

    def get_search_text(self):
        return self._search_text

    def get_template(self):
        return self._template

    def set_template(self, category):
        self._template = category

    def get_search_data(self):
        return self._search_data

    def set_search_data(self, data):
        self._search_data = data

    def get_filter_preferences(self):
        return self._filter_preferences

    def set_filter_preferences(self, filter_preferences):
        self._filter_preferences = filter_preferences

    @property
    def get(self):
        return self._get
