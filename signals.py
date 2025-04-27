# signals.py
from PyQt6.QtCore import QObject, pyqtSignal


class SignalRepository(QObject):

    # Layouts
    signalForUserLayout = pyqtSignal(bool)
    signalForUserAuthLayout = pyqtSignal(bool)
    signalForUserLoginCompleted = pyqtSignal()
    signalParentViewStackedChange = pyqtSignal(str)

    setSideBarButtonActive = pyqtSignal(str)

    # Notifications Signals
    globalCreateLoadingNotificationSignal = pyqtSignal(str)
    globalLoadingNotificationControllerSignal = pyqtSignal(str)
    globalCreateMessageNotificationSignal = pyqtSignal(dict)

    # Patients Signals
    updatePatientsTableSignal = pyqtSignal()
    updatePatientsTrashTableSignal = pyqtSignal()

    # Doctors Signals
    doctorServiceFormWidgetNewContentIsAddedSignal = pyqtSignal()

    # Appointments Signals
    appointmentHeaderInternalLoaderSignal = pyqtSignal(bool)
    globalAppointmentStateManagementTabSignal = pyqtSignal(str)
    globalAppointmentUpdateTableViewSignal = pyqtSignal()
    globalAppointmentUpComingSessionCardClickedSignal = pyqtSignal(int)
    refreshAppointmentsTableSignal = pyqtSignal()

    # Templates Signals
    globalCreateTemplateEditorViewSignal = pyqtSignal()
    templateHeaderInternalLoaderSignal = pyqtSignal(bool)

    # Reports Signals
    reportHeaderInternalLoaderSignal = pyqtSignal(bool)
    globalReportStateManagementTabSignal = pyqtSignal(str)
    globalReportUpdateTableViewSignal = pyqtSignal()
    globalRecentReportCardClickedSignal = pyqtSignal(int)
    globalRefreshReportTableSignal = pyqtSignal()
    updateReportsTrashTableSignal = pyqtSignal()
    refreshReportsAllTabSignal = pyqtSignal()

    # Dashboard
    updateAnalyticBasedOnYearSignal = pyqtSignal(str)

    # Editor Signals
    fontFamilyChangedSignal = pyqtSignal(str)


class SignalRepositorySingleton:
    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = SignalRepository()
        return cls._instance
