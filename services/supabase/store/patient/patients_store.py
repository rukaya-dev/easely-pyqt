from PyQt6.QtCore import QObject


class PatientsStore(QObject):

    def __init__(self):
        super().__init__()
        self.data = []
        self.patient = {}
        self.search_text = ""
        self.filter_preferences = None
        self.searched_data = {}
        self.filtered_data = {}

    def set_search_text(self, search_text):
        self.search_text = search_text

    def get_search_text(self):
        return self.search_text

    def set_searched_data(self, data):
        self.searched_data = data

    def get_searched_data(self):
        return self.searched_data

    def get_filter_preferences(self):
        return self.filter_preferences

    def set_filter_preferences(self, filter_preferences):
        self.filter_preferences = filter_preferences

    def set_filtered_data(self, data):
        self.filtered_data = data

    def get_filtered_data(self):
        return self.filtered_data

    def get_data(self):
        return self.data

    def set_data(self, data):
        self.data = data

    def get_patient(self):
        return self.patient

    def set_patient(self, patient):
        self.patient = patient

