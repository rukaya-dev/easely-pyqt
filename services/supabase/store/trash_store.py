from PyQt6.QtCore import QObject


class TrashStore(QObject):

    def __init__(self):
        super().__init__()
        self._data = []
        self._trash_record = {}
        self._search_text = ""
        self._filter_preferences = None
        self._search_data = []
        self._filtered_data = []

    def set_search_text(self, search_text):
        self._search_text = search_text

    def get_search_text(self):
        return self._search_text

    def get_filter_preferences(self):
        return self._filter_preferences

    def set_filter_preferences(self, filter_preferences):
        self._filter_preferences = filter_preferences

    def get_data(self):
        return self._data

    def set_data(self, data):
        self._data = data

    def get_filtered_data(self):
        return self._filtered_data

    def set_filtered_data(self, filtered_data):
        self._filtered_data = filtered_data

    def get_trash_record(self):
        return self._trash_record

    def set_trash_record(self, history):
        self._trash_record = history

    def get_search_data(self):
        return self._search_data

    def set_search_data(self, data):
        self._search_data = data
