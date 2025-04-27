import asyncio

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget
from qasync import asyncSlot

from services.supabase.controllers.appointment.appointment_statuses_controller import AppointmentStatusesController
from services.supabase.controllers.appointment.appointment_types_controller import AppointmentTypesController
from services.supabase.controllers.appointment.apponitment_controller import AppointmentController
from services.supabase.controllers.settings.service_controller import ServiceController
from signals import SignalRepositorySingleton
from views.appointement.appointments_management_view import AppointmentManagementView
from views.appointement.upcoming_sessions import UpComingSessions


class AppointmentsListView(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # Signals
        self.upcoming_data = None
        self.central_widget = None
        self.appointment_table_management_view = None
        self.upcoming_sessions = None
        self.data = None
        self.signals = SignalRepositorySingleton.instance()

        self.appointment_controller = AppointmentController()
        self.appointment_types_controller = AppointmentTypesController()
        self.appointment_statuses_controller = AppointmentStatusesController()
        self.service_controller = ServiceController()

        self.stacked_content_widget = QStackedWidget()

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stacked_content_widget)

        self.setLayout(layout)
        asyncio.create_task(self.get_initial_data())

    async def get_initial_data(self):
        self.signals.globalCreateLoadingNotificationSignal.emit("GET_APPOINTMENTS_LIST")

        self.data = await self.appointment_controller.get_items_by_tabs("all", page_number=1, item_per_page=20)

        self.upcoming_data = await self.appointment_controller.get_items_by_tabs("upcoming", 1, 10)
        print(self.upcoming_data)

        if not self.appointment_types_controller.store.get_data():
            await self.populate_appointment_types()

        if not self.appointment_statuses_controller.store.get_data():
            await self.populate_appointment_statuses()

        await self.populate_services()

        await self.setup_table_ui()

        self.signals.globalLoadingNotificationControllerSignal.emit("GET_APPOINTMENTS_LIST")

    async def setup_table_ui(self):
        self.upcoming_sessions = UpComingSessions(self.upcoming_data, controller=self.appointment_controller)
        self.appointment_table_management_view = AppointmentManagementView(self.data,
                                                                           appointment_controller=self.appointment_controller,
                                                                           appointment_types_controller=self.appointment_types_controller,
                                                                           appointment_status_controller=self.appointment_statuses_controller,
                                                                           service_controller=self.service_controller,
                                                                           parent=self)

        self.central_widget = QWidget()

        main_h_layout = QHBoxLayout(self.central_widget)
        main_h_layout.setSpacing(30)
        main_h_layout.setContentsMargins(0, 0, 0, 0)
        main_h_layout.addWidget(self.upcoming_sessions)
        main_h_layout.addWidget(self.appointment_table_management_view, 1)

        self.set_main_content(self.central_widget)

    def set_main_content(self, content_widget):
        self.stacked_content_widget.addWidget(content_widget)
        self.stacked_content_widget.setCurrentWidget(content_widget)

    @asyncSlot()
    async def populate_appointment_types(self):
        await self.appointment_types_controller.get_items()

    @asyncSlot()
    async def populate_appointment_statuses(self):
        await self.appointment_statuses_controller.get_items()

    @asyncSlot()
    async def populate_services(self):
        await self.service_controller.get_all_services()
