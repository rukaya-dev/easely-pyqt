from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QLabel

from loggers.logger_configs import set_up_logger
from services.supabase.controllers.settings.user_auth_controller import UserAuthController
from services.supabase.models.settings.user_auth_model import UserAuthModel
from signals import SignalRepositorySingleton
from views.layouts.user_auth_layout import UserAuthLayout
from views.layouts.user_layout import UserLayout
from views.report_editor_test import ReportEditorTest

logger = set_up_logger('main.views.layouts.main_window_layout')


class MainWindowView(QMainWindow):
    def __init__(self, app_runner):
        super().__init__()
        self.app_runner = app_runner

        self.setMinimumSize(1920, 1080)
        self.installEventFilter(self)

        self.user_layout = None
        self.user_auth_layout = None
        self.splash_label = None

        self.stacked_content_widget = QStackedWidget()

        self.signals = SignalRepositorySingleton.instance()

        self.signals.signalForUserLayout.connect(self.show_user_layout)
        self.signals.signalForUserAuthLayout.connect(self.show_user_auth_layout)
        self.signals.signalParentViewStackedChange.connect(self.show_content_view)

        self.setCentralWidget(self.stacked_content_widget)

        # Initialize the splash screen
        self.show_splash_screen()

        # Start async initialization
        QTimer.singleShot(1000, self.initialize_app)

    def closeEvent(self, event):
        self.app_runner.stop_application()
        super().closeEvent(event)

    def show_splash_screen(self):

        self.splash_label = QLabel("Loading...", self)
        self.splash_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # self.splash_label.setGeometry(0, 0, 1920, 1080)

        # Load the image with QPixmap
        pixmap = QPixmap(":resources/images/splash-logo.png")
        self.splash_label.setPixmap(
            pixmap.scaled(364, 364, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.stacked_content_widget.addWidget(self.splash_label)

        self.splash_label.showMaximized()
        self.splash_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def initialize_app(self):

        # Proceed with async user authentication check
        self.check_user_authentication()

    def check_user_authentication(self):
        try:
            user_exist = UserAuthModel.check_if_user_exist()
            if not user_exist:
                self.signals.signalForUserAuthLayout.emit(True)
                self.splash_label.hide()
            else:
                UserAuthController.get_user_profile_data()
        #
                self.signals.signalForUserLayout.emit(True)
                self.splash_label.hide()
        except Exception as e:
            logger.error(e, exc_info=True)
            self.signals.signalForUserAuthLayout.emit(True)

    def set_main_content(self, content_widget):
        self.stacked_content_widget.addWidget(content_widget)
        self.stacked_content_widget.setCurrentWidget(content_widget)

    def show_user_layout(self):
        self.user_layout = UserLayout()
        self.set_main_content(self.user_layout)

        # Active
        if len(self.user_layout.sidebar_view.allowed_button_data) > 0:
            self.show_content_view(self.user_layout.sidebar_view.allowed_button_data[0]["object_name"])

    def show_user_auth_layout(self):
        self.user_auth_layout = UserAuthLayout()
        self.set_main_content(self.user_auth_layout)

    def show_content_view(self, view_name):

        if view_name == "dashboard_button":
            self.show_dashboard()

        if view_name == "report_workshop_button":
            self.show_report_workshop()

        if view_name == "patients_button":
            self.show_patients()

        if view_name == "activity_center_button":
            self.show_activity_center()

        if view_name == "staff_button":
            self.show_staff()

        if view_name == "settings_button":
            self.show_settings()

        if view_name == "appointments_button":
            self.show_appointments()

        if view_name == "billings_button":
            self.show_billings()

        if view_name == "reports_button":
            self.show_reports()

    def show_dashboard(self):
        from views.dashboard.dashboard_layout_view import DashboardLayoutView
        dashboard_view = DashboardLayoutView()
        self.user_layout.set_main_content(dashboard_view)
        print("dashboard")

    def show_report_workshop(self):
        from views.report_workshop.report_workshop_layout_view import ReportWorkshopLayoutView
        report_workshop_view = ReportWorkshopLayoutView()
        self.user_layout.set_main_content(report_workshop_view)
        print("repor_workshop")


    def show_patients(self):
        print("dddd")
        # from views.patient.patient_layout_view import PatientsLayoutView
        # patients_view = PatientsLayoutView()
        # self.user_layout.set_main_content(patients_view)
        # patients_view.update()


    def show_activity_center(self):
        from views.activity_center.activity_center import ActivityCenterLayoutView
        activity_center_view = ActivityCenterLayoutView()
        self.user_layout.set_main_content(activity_center_view)
        activity_center_view.update()

    def show_settings(self):
        from views.settings.settings_layout_view import SettingsLayoutView
        settings_view = SettingsLayoutView()
        self.user_layout.set_main_content(settings_view)

    def show_staff(self):
        from views.staff.staff_layout_view import StaffLayoutView
        settings_view = StaffLayoutView()
        self.user_layout.set_main_content(settings_view)

    def show_appointments(self):
        from views.appointement.appointments_layout_view import AppointmentsLayoutView
        appointments_view = AppointmentsLayoutView()
        self.user_layout.set_main_content(appointments_view)

    def show_billings(self):
        from views.billing.billings_management_view import BillingsManagementView
        billings_view = BillingsManagementView()
        self.user_layout.set_main_content(billings_view)

    def show_reports(self):
        pass
        from views.report.reports_layout_view import ReportsLayoutView
        reports_view = ReportsLayoutView()
        self.user_layout.set_main_content(reports_view)

    def show_report_editor_test(self):
        pass
        # reports_view = ReportEditorTest()
        # self.user_layout.set_main_content(reports_view)
