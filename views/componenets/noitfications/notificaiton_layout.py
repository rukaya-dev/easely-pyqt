from PyQt6.QtCore import Qt, QEvent, QObject
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy

from signals import SignalRepositorySingleton
from views.componenets.noitfications.quick_notifier import QuickNotifier
from views.componenets.noitfications.spinner_loading import SpinnerLoading


class NotificationLayout(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.parent = parent

        self.array_of_loading_widget = {}
        self.array_of_message_widget = []

        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.layout.addStretch(1)
        self.setLayout(self.layout)

        notification_event_filter = LayoutEventFilter(self)
        self.installEventFilter(notification_event_filter)

        # Signals
        self.signals = SignalRepositorySingleton.instance()

        self.signals.globalCreateLoadingNotificationSignal.connect(self.create_loading_notification)
        self.signals.globalLoadingNotificationControllerSignal.connect(self.__destroy_loading)
        self.signals.globalCreateMessageNotificationSignal.connect(self.create_message_notification)

    def create_loading_notification(self, identifier):
        spinner = SpinnerLoading()
        spinner.loading_spinner.start()
        self.array_of_loading_widget[identifier] = spinner
        self.layout.addWidget(spinner)
        self.layout.setAlignment(spinner, Qt.AlignmentFlag.AlignRight)

    def create_message_notification(self, object_data):
        quick_notifier = QuickNotifier(message_type=object_data["message_type"], message=object_data["message"],
                                       duration=object_data["duration"])
        self.layout.addWidget(quick_notifier)
        self.layout.setAlignment(quick_notifier, Qt.AlignmentFlag.AlignRight)

    def __destroy_loading(self, identifier):
        if identifier in self.array_of_loading_widget:
            widget = self.array_of_loading_widget[identifier]

            if widget.loading_spinner.isSpinning():
                widget_to_delete = self.array_of_loading_widget.pop(identifier)
                self.layout.removeWidget(widget_to_delete)
                widget_to_delete.deleteLater()

    def re_position_notification_widget(self):
        window_size = self.parent.size()
        notification_widget_size = self.size()
        x = window_size.width() - notification_widget_size.width() - 10
        y = window_size.height() - notification_widget_size.height() - 10
        self.move(x, y)


class LayoutEventFilter(QObject):
    def eventFilter(self, obj: NotificationLayout, event):
        if event.type() == QEvent.Type.ChildAdded:
            if obj.layout.count() >= 1:
                obj.setFixedSize(600, 1000)
                obj.raise_()
                obj.re_position_notification_widget()

        elif event.type() == QEvent.Type.ChildRemoved:
            # if isinstance(obj, QVBoxLayout):
            obj.setFixedSize(0, 0)
            obj.lower()
            if isinstance(obj, QVBoxLayout):
                obj.re_position_notification_widget()

        return super().eventFilter(obj, event)
