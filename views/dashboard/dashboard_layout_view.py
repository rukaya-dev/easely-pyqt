import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy

from signals import SignalRepositorySingleton
from views.componenets.customsComponents.custom_combobox import CustomComboBox
from views.componenets.customsComponents.custom_scroll_area import CustomScrollArea
from views.dashboard.appointments_analytic import TotalAppointmentsCard, AppointmentsAnalyticView
from views.dashboard.patients_analytic import PatientPercentageChangeCard, PatientsAnalyticView
# from views.dashboard.appointments_analytic import TotalAppointmentsCard, AppointmentsAnalyticView
# from views.dashboard.revenue_analytic import TotalRevenueCard, RevenueAnalyticView
# from views.dashboard.patients_analytic import PatientPercentageChangeCard, PatientsAnalyticView
from views.dashboard.report_analytic import TotalReportsCard, ReportsAnalyticView
from views.dashboard.revenue_analytic import TotalRevenueCard, RevenueAnalyticView


class DashboardLayoutView(QWidget):
    def __init__(self):
        super().__init__()

        self.tab_buttons = None

        self.signals = SignalRepositorySingleton.instance()

        current_year = datetime.datetime.now().year

        self.current_year = current_year

        self.year_picker = CustomComboBox()
        self.year_picker.setFixedWidth(100)

        for year in range(current_year, current_year + 30):
            self.year_picker.addItem(str(year))

        self.year_picker.currentIndexChanged.connect(self.set_year_picker)

        self.total_patients_card = PatientPercentageChangeCard(
            data={"trend_type": "decreased", "trend_value": 0, "total_patients": 0})
        self.total_revenue_card = TotalRevenueCard(
            data={"trend_type": "decreased", "trend_value": 0, "total_revenue": 0})
        self.total_reports_card = TotalReportsCard(
            data={"trend_type": "decreased", "trend_value": 0, "total_reports": 0})
        self.total_appointments_card = TotalAppointmentsCard(
            data={"trend_type": "decreased", "trend_value": 0, "total_appointments": 0})

        spacer = QSpacerItem(56, 88, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        cards_layout = QHBoxLayout()
        cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        cards_layout.setContentsMargins(0, 0, 0, 0)
        cards_layout.setSpacing(20)

        cards_layout.addWidget(self.total_patients_card)
        cards_layout.addWidget(self.total_revenue_card)
        cards_layout.addWidget(self.total_reports_card)
        cards_layout.addWidget(self.total_appointments_card)
        cards_layout.addSpacerItem(spacer)
        cards_layout.addWidget(self.year_picker, 1, Qt.AlignmentFlag.AlignTop)

        self.patient_analytic_widget = PatientsAnalyticView(parent=self)
        self.patient_analytic_widget.update_analytic_based_on_year(current_year)

        self.revenue_analytic_view = RevenueAnalyticView(parent=self)
        self.revenue_analytic_view.update_analytic_based_on_year(current_year)

        self.appointment_analytic_view = AppointmentsAnalyticView(parent=self)
        self.appointment_analytic_view.update_analytic_based_on_year(current_year)

        self.report_analytic_view = ReportsAnalyticView(parent=self)
        self.report_analytic_view.update_analytic_based_on_year(current_year)

        central_widget = QWidget()

        main_layout = QVBoxLayout(central_widget)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.setContentsMargins(20, 10, 20, 20)

        main_layout.addLayout(cards_layout)
        main_layout.addWidget(self.patient_analytic_widget)
        main_layout.addWidget(self.revenue_analytic_view)
        main_layout.addWidget(self.appointment_analytic_view)
        main_layout.addWidget(self.report_analytic_view)

        scroll_area = CustomScrollArea()
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setWidget(central_widget)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(0, 20, 3, 3)

        layout.addWidget(scroll_area)

        self.setLayout(layout)

    def set_year_picker(self, year):
        print("")
        self.current_year = str(self.year_picker.currentText())
        self.signals.updateAnalyticBasedOnYearSignal.emit(self.current_year)
