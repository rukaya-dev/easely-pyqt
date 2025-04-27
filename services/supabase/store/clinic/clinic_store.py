from PyQt6.QtCore import QObject


class ClinicStore(QObject):

    def __init__(self):
        super().__init__()
        self.data = None
    def get_data(self):
        return self.data

    def set_data(self, data):
        self.data = data
