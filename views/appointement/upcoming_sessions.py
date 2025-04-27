from PyQt6.QtCore import Qt, QSize, QObject, QEvent
from PyQt6.QtGui import QColor, QCursor, QPainter
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QSpacerItem, QSizePolicy, \
    QGraphicsDropShadowEffect

from signals import SignalRepositorySingleton
from views.componenets.customsComponents.custom_scroll_area import CustomScrollArea

signals = SignalRepositorySingleton.instance()


class UpComingSessions(QWidget):

    def __init__(self, data, controller, parent=None):
        super().__init__(parent)

        self.data = data
        self.appointment_controller = controller

        upcoming_label = QLabel("Upcoming")
        upcoming_label.setStyleSheet("background-color:transparent;color:#354F66;")

        font = upcoming_label.font()
        font.setWeight(font.Weight.Normal)
        font.setPointSize(14)
        upcoming_label.setFont(font)

        main_vertical_layout = QVBoxLayout()
        main_vertical_layout.setSpacing(20)
        main_vertical_layout.setContentsMargins(0, 0, 0, 0)
        main_vertical_layout.addWidget(upcoming_label)

        if self.data:
            self.upcoming_sessions_widget = self.render_up_coming_widgets()
            main_vertical_layout.addWidget(self.upcoming_sessions_widget)

        central_widget = QWidget()
        central_widget.setLayout(main_vertical_layout)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(30, 20, 0, 0)
        layout.addWidget(central_widget)

        self.setLayout(layout)

    def render_up_coming_widgets(self):
        main_card_widget = QWidget()

        scroll_area = CustomScrollArea(self)
        scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setWidget(main_card_widget)

        main_h_layout = QVBoxLayout()
        main_h_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_h_layout.setSpacing(20)
        main_h_layout.setContentsMargins(0, 0, 0, 0)

        for appointment in self.data["data"]:
            card_main_content_widget = CardMainContentWidget(appointment)
            main_h_layout.addWidget(card_main_content_widget)

        main_card_layout = QVBoxLayout(main_card_widget)
        main_card_layout.setContentsMargins(0, 0, 15, 0)
        main_card_layout.addLayout(main_h_layout)

        return scroll_area


class CardLeftBorderWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        widget = QWidget()
        widget.setStyleSheet("background-color:#FD9E06;")
        widget.setMinimumHeight(180)
        widget.setFixedWidth(6)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(widget)
        self.setLayout(layout)


class CardMainContentWidget(QWidget):
    def __init__(self, data, parent=None):
        super().__init__(parent)

        self.widget = QWidget()

        self.data = data

        self.widget.setObjectName("card_main_content_widget")

        self.widget_enter_event_stylesheet = """
        QWidget#card_main_content_widget {
            border:1px solid #D4DDE0;
            border-radius:10px;
            background-color:transparent;
        }
        QLabel {
            border:0;
        }
        """
        self.widget_leave_event_stylesheet = """
            QWidget#card_main_content_widget {
                border:1px solid #D4DDE0;
                border-radius:7px;
                background-color:white;
            }
            QLabel {
                border:0;
            }
            """

        self.widget.setStyleSheet(self.widget_leave_event_stylesheet)

        card_left_border_widget = CardLeftBorderWidget()

        self.card_top_content_widget = CardTopContentWidget(data)

        self.card_lower_content_widget = CardLowerContentWidget(data)

        card_top_and_down_layout = QVBoxLayout()
        card_top_and_down_layout.setContentsMargins(10, 10, 10, 10)
        card_top_and_down_layout.addWidget(self.card_top_content_widget)
        card_top_and_down_layout.addWidget(self.card_lower_content_widget)

        main_h_layout = QHBoxLayout(self.widget)
        main_h_layout.setSpacing(10)
        main_h_layout.setContentsMargins(0, 0, 0, 0)
        main_h_layout.addWidget(card_left_border_widget)
        main_h_layout.addLayout(card_top_and_down_layout)

        # Absolute widget that should overlay the main widget
        self.overlay = OverlayWidget(self.widget)
        self.overlay.setProperty("id", data["appointment_id"])
        self.overlay.setFixedSize(self.widget.sizeHint())
        self.overlay.raise_()

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.widget)

        self.setLayout(layout)
        self.setMouseTracking(True)

        pointer_cursor = QCursor()
        pointer_cursor.setShape(Qt.CursorShape.PointingHandCursor)
        self.setCursor(pointer_cursor)

    def enterEvent(self, e):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(shadow)
        return super().enterEvent(e)

    def leaveEvent(self, e):
        self.setGraphicsEffect(None)
        return super().leaveEvent(e)


class OverlayWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.card_event_filter = CardEventFilter(parent=self)
        self.installEventFilter(self.card_event_filter)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)


class CardEventFilter(QObject):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_widget = parent

    def eventFilter(self, obj: QWidget, event):
        if event.type() == QEvent.Type.MouseButtonPress:
            signals.globalAppointmentUpComingSessionCardClickedSignal.emit(obj.property("id"))
        return super().eventFilter(obj, event)


class CardTopContentWidget(QWidget):
    def __init__(self, data, parent=None):
        super().__init__(parent)

        avatar_name_label = QLabel(data["patient_first_name"][:1] + data["patient_last_name"][:1])
        avatar_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar_name_label.setFixedSize(QSize(40, 40))
        avatar_name_label.setStyleSheet("""
        QLabel {
            border-radius:20px;
            background-color:#E5F3FC;
            color:#307BBE;
        }
        """)

        avatar_name_font = avatar_name_label.font()
        avatar_name_font.setWeight(avatar_name_font.Weight.DemiBold)
        avatar_name_label.setFont(avatar_name_font)
        # -----------------------------------------------------------

        name_label = QLabel(data["patient_first_name"] + " " + data["patient_last_name"])
        name_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        name_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        name_label.setStyleSheet("""
         QLabel {
             background-color:transparent;
             color:#283B45;
         }
         """)

        name_font = name_label.font()
        name_font.setWeight(name_font.Weight.DemiBold)
        name_font.setPointSize(12)
        name_label.setFont(name_font)
        # -----------------------------------------------------------

        date_label = QLabel(data["appointment_date"])
        date_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        date_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        date_label.setStyleSheet("""
         QLabel {
             background-color:transparent;
             color:#81858E;
         }
         """)

        date_font = date_label.font()
        date_font.setPointSize(8)
        date_label.setFont(date_font)

        time_label = QLabel(data["appointment_time"])
        time_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        time_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        time_label.setStyleSheet("""
         QLabel {
             background-color:transparent;
             color:#81858E;
         }
         """)
        time_label.setFont(date_font)

        date_and_time_layout = QHBoxLayout()
        date_and_time_layout.setContentsMargins(0, 0, 0, 0)
        date_and_time_layout.setSpacing(10)

        date_and_time_layout.addWidget(date_label)
        date_and_time_layout.addWidget(time_label)
        # -----------------------------------------------------------

        date_and_time_and_name_layout = QVBoxLayout()
        date_and_time_and_name_layout.setSpacing(10)
        date_and_time_and_name_layout.setContentsMargins(0, 0, 0, 0)

        date_and_time_and_name_layout.addWidget(name_label)
        date_and_time_and_name_layout.addLayout(date_and_time_layout)

        avatar_and_date_and_time_and_name_layout = QHBoxLayout()
        avatar_and_date_and_time_and_name_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar_and_date_and_time_and_name_layout.setSpacing(10)
        avatar_and_date_and_time_and_name_layout.setContentsMargins(0, 0, 0, 0)

        avatar_and_date_and_time_and_name_layout.addWidget(avatar_name_label)
        avatar_and_date_and_time_and_name_layout.addLayout(date_and_time_and_name_layout)

        spacer = QSpacerItem(10, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        context_menu_and_avatar_and_date_and_time_and_name_layout = QHBoxLayout()
        context_menu_and_avatar_and_date_and_time_and_name_layout.setSpacing(10)
        context_menu_and_avatar_and_date_and_time_and_name_layout.setContentsMargins(0, 0, 0, 0)

        context_menu_and_avatar_and_date_and_time_and_name_layout.addLayout(avatar_and_date_and_time_and_name_layout)
        context_menu_and_avatar_and_date_and_time_and_name_layout.addSpacerItem(spacer)

        line_seperator_widget = QWidget()
        line_seperator_widget.setStyleSheet("border:0;background-color:#E9EBEE;")
        line_seperator_widget.setFixedHeight(1)

        top_card_layout = QVBoxLayout()
        top_card_layout.setSpacing(10)
        top_card_layout.addLayout(context_menu_and_avatar_and_date_and_time_and_name_layout)
        top_card_layout.addWidget(line_seperator_widget)

        widget = QWidget()

        main_h_layout = QHBoxLayout(widget)
        main_h_layout.setContentsMargins(0, 0, 0, 0)
        main_h_layout.addLayout(top_card_layout)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.addWidget(widget)
        self.setLayout(layout)


class CardLowerContentWidget(QWidget):
    def __init__(self, data, parent=None):
        super().__init__(parent)

        service_name_label = QLabel(data["service_name"])
        service_name_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        service_name_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        service_name_label.setStyleSheet("""
         QLabel {
             background-color:transparent;
             color:#283B45;
         }
         """)

        service_name_font = service_name_label.font()
        service_name_font.setWeight(service_name_font.Weight.Medium)
        service_name_font.setPointSize(11)
        service_name_label.setFont(service_name_font)
        # -----------------------------------------------------------

        appointment_type_label = QLabel(data["appointment_type"])
        appointment_type_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        appointment_type_label.setContentsMargins(5, 0, 5, 0)
        appointment_type_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        appointment_type_label.setFixedHeight(25)
        appointment_type_label.setStyleSheet("""
        QLabel {
            border-radius:8px;
            background-color:#FFF2DF;
            color:#794B00;
        }
        """)

        appointment_type_font = appointment_type_label.font()
        appointment_type_font.setPointSize(10)
        appointment_type_font.setWeight(appointment_type_font.Weight.Medium)
        appointment_type_label.setFont(appointment_type_font)
        # -----------------------------------------------------------

        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(0, 0, 0, 0)

        main_layout.addWidget(service_name_label)
        main_layout.addWidget(appointment_type_label)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 10, 0, 10)

        layout.addLayout(main_layout)

        self.setLayout(layout)
