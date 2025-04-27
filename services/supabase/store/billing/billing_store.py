from PyQt6.QtCore import QObject

from signals import SignalRepositorySingleton


class BillingStore(QObject):

    def __init__(self):
        super().__init__()
        # Signals
        self.signals = SignalRepositorySingleton.instance()

        self.searched_data = {}
        self.billing = {}
        self._search_text = ""
        self._filter_preferences = {}
        self.active_billing_tab = "all"
        self.fallback_active_billing_tab = "all"
        self.all_tab_data = {}
        self.scheduled_data = {}
        self.upcoming_tab_data = {}
        self.expired_tab_data = {}
        self.canceled_tab_data = {}
        self.search_filter_tab_data = {}

    def get_active_billing_tab(self):
        return self.active_billing_tab

    def get_fallback_active_billing_tab(self):
        return self.fallback_active_billing_tab

    def set_active_billing_tab(self, tab):
        if tab != "search_filter":
            self.fallback_active_billing_tab = tab
        self.active_billing_tab = tab
        self.signals.globalbillingStateManagementTabSignal.emit(tab)

    def get_scheduled_data(self):
        return self.scheduled_data

    def set_scheduled_data(self, data):
        self.scheduled_data = data

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

    def get_upcoming_tab_data(self):
        return self.upcoming_tab_data

    def set_upcoming_tab_data(self, data):
        self.upcoming_tab_data = data

    def get_expired_tab_data(self):
        return self.expired_tab_data

    def set_expired_tab_data(self, data):
        self.expired_tab_data = data

    def get_canceled_tab_data(self):
        return self.canceled_tab_data

    def set_canceled_tab_data(self, data):
        self.canceled_tab_data = data

    def get_billing(self):
        return self.billing

    def set_billing(self, billing):
        self.billing = billing
        self.billing = billing

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
