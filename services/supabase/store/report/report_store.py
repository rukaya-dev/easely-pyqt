from PyQt6.QtCore import QObject

from signals import SignalRepositorySingleton


class ReportStore(QObject):

    def __init__(self):
        super().__init__()
        # Signals
        self.signals = SignalRepositorySingleton.instance()

        self.searched_data = {}
        self.report = {}
        self._search_text = ""
        self._filter_preferences = {}
        self.active_report_tab = "all"
        self.fallback_active_report_tab = "all"
        self.all_tab_data = {}
        self.drafted_tab_reports = {}
        self.recent_tab_reports = {}
        self.archived_tab_reports = {}
        self.finalized_tab_reports = {}
        self.search_filter_tab_data = {}

    def get_active_report_tab(self):
        return self.active_report_tab

    def get_fallback_active_report_tab(self):
        return self.fallback_active_report_tab

    def set_active_report_tab(self, tab):
        if tab != "search_filter":
            self.fallback_active_report_tab = tab
        self.active_report_tab = tab
        self.signals.globalReportStateManagementTabSignal.emit(tab)

    def get_drafted_tab_reports(self):
        return self.drafted_tab_reports

    def set_drafted_tab_reports(self, data):
        self.drafted_tab_reports = data

    def get_data(self):
        return self._data

    def set_data(self, data):
        self._data = data

    def get_search_filter_tab_data(self):
        return self.search_filter_tab_data

    def set_search_filter_tab_data(self, data):
        self.search_filter_tab_data = data

    def get_searched_data(self):
        return self.searched_data

    def set_searched_data(self, data):
        self.searched_data = data

    def get_all_tab_data(self):
        return self.all_tab_data

    def set_all_tab_data(self, data):
        self.all_tab_data = data

    def get_recent_tab_reports(self):
        return self.recent_tab_reports

    def set_recent_tab_reports(self, data):
        self.recent_tab_reports = data

    def get_archived_tab_reports(self):
        return self.archived_tab_reports

    def set_archived_tab_reports(self, data):
        self.archived_tab_reports = data

    def get_finalized_tab_reports(self):
        return self.finalized_tab_reports

    def set_finalized_tab_reports(self, data):
        self.finalized_tab_reports = data

    def get_report(self):
        return self.report

    def set_report(self, report):
        self.report = report
        self.report = report

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
