import requests
from PyQt6.QtCore import QObject, pyqtSignal


class ReportLayoutStore(QObject):

    def __init__(self):
        super().__init__()
        self.data = []
        self.report_header_layout = {}
        self.report_footer_layout = {}

    def get_data(self):
        return self.data

    def set_data(self, data):
        self.data = data

    def get_report_header_layout(self):
        return self.report_header_layout

    def set_report_header_layout(self, layout):
        self.report_header_layout = layout

    def get_report_footer_layout(self):
        return self.report_footer_layout

    def set_report_footer_layout(self, layout):
        self.report_footer_layout = layout
