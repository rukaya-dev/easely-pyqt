from PyQt6.QtCore import Qt, QSize, QObject, QEvent
from PyQt6.QtGui import QColor, QCursor, QPainter
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QSpacerItem, QSizePolicy, \
    QGraphicsDropShadowEffect

from signals import SignalRepositorySingleton
from views.componenets.customsComponents.custom_scroll_area import CustomScrollArea

signals = SignalRepositorySingleton.instance()


class RecentReports(QWidget):

    def __init__(self, data, controller, parent=None):
        super().__init__(parent)

        self.data = data
        self.report_controller = controller

        recent_label = QLabel("Recent Reports")
        recent_label.setStyleSheet("background-color:transparent;color:#354F66;")

        font = recent_label.font()
        font.setWeight(font.Weight.Normal)
        font.setPointSize(14)
        recent_label.setFont(font)

        main_vertical_layout = QVBoxLayout()
        main_vertical_layout.setSpacing(20)
        main_vertical_layout.setContentsMargins(0, 0, 0, 0)
        main_vertical_layout.addWidget(recent_label)

        if self.data:
            self.recent_report_widget = self.render_recent_reports_widgets()
            main_vertical_layout.addWidget(self.recent_report_widget)

        central_widget = QWidget()
        central_widget.setLayout(main_vertical_layout)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(30, 20, 0, 0)
        layout.addWidget(central_widget)

        self.setLayout(layout)

    def render_recent_reports_widgets(self):
        main_card_widget = QWidget()

        scroll_area = CustomScrollArea(self)
        scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setWidget(main_card_widget)

        main_v_layout = QVBoxLayout()
        main_v_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_v_layout.setSpacing(20)
        main_v_layout.setContentsMargins(0, 0, 0, 0)

        for report in self.data["data"]:
            card_main_content_widget = CardMainContentWidget(report)
            main_v_layout.addWidget(card_main_content_widget)

        main_card_layout = QVBoxLayout(main_card_widget)
        main_card_layout.setContentsMargins(0, 0, 15, 0)
        main_card_layout.addLayout(main_v_layout)

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
        self.widget.setMaximumWidth(270)
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

        # Absolute widget
        self.overlay = OverlayWidget(self.widget)
        self.overlay.setProperty("id", data["report_id"])
        self.overlay.setFixedSize(self.widget.sizeHint())
        self.overlay.raise_()

        # Layout to hold the main widget
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self.widget)

        self.setLayout(layout)

        pointer_cursor = QCursor()
        pointer_cursor.setShape(Qt.CursorShape.PointingHandCursor)
        self.setCursor(pointer_cursor)

        self.setMouseTracking(True)

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
            signals.globalRecentReportCardClickedSignal.emit(obj.property("id"))
        return super().eventFilter(obj, event)


class CardTopContentWidget(QWidget):
    def __init__(self, data, parent=None):
        super().__init__(parent)

        avatar_name_label = QLabel(data["patient_name"][:1])
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

        name_label = QLabel(data["patient_name"])
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

        gender_label = QLabel(data["patient_gender"])
        gender_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        gender_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        gender_label.setStyleSheet("""
         QLabel {
             background-color:transparent;
             color:#626262;
             letter-spacing:1px;
         }
         """)

        gender_font = gender_label.font()
        gender_font.setPointSize(8)
        gender_label.setFont(gender_font)

        age_label = QLabel(str(data["patient_age"]) + " " + data["patient_age_unit"])
        age_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        age_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        age_label.setStyleSheet("""
         QLabel {
             background-color:transparent;
             color:#626262;
             letter-spacing:1px;
         }
         """)
        age_label.setFont(gender_font)

        gender_and_age_layout = QHBoxLayout()
        gender_and_age_layout.setContentsMargins(0, 0, 0, 0)
        gender_and_age_layout.setSpacing(10)

        gender_and_age_layout.addWidget(gender_label)
        gender_and_age_layout.addWidget(age_label)
        # -----------------------------------------------------------

        gender_and_time_and_name_layout = QVBoxLayout()
        gender_and_time_and_name_layout.setSpacing(10)
        gender_and_time_and_name_layout.setContentsMargins(0, 0, 0, 0)

        gender_and_time_and_name_layout.addWidget(name_label)
        gender_and_time_and_name_layout.addLayout(gender_and_age_layout)

        avatar_and_gender_and_time_and_name_layout = QHBoxLayout()
        avatar_and_gender_and_time_and_name_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar_and_gender_and_time_and_name_layout.setSpacing(10)
        avatar_and_gender_and_time_and_name_layout.setContentsMargins(0, 0, 0, 0)

        avatar_and_gender_and_time_and_name_layout.addWidget(avatar_name_label)
        avatar_and_gender_and_time_and_name_layout.addLayout(gender_and_time_and_name_layout)

        spacer = QSpacerItem(10, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        context_menu_and_avatar_and_gender_and_time_and_name_layout = QHBoxLayout()
        context_menu_and_avatar_and_gender_and_time_and_name_layout.setSpacing(10)
        context_menu_and_avatar_and_gender_and_time_and_name_layout.setContentsMargins(0, 0, 0, 0)

        context_menu_and_avatar_and_gender_and_time_and_name_layout.addLayout(
            avatar_and_gender_and_time_and_name_layout)
        context_menu_and_avatar_and_gender_and_time_and_name_layout.addSpacerItem(spacer)

        line_seperator_widget = QWidget()
        line_seperator_widget.setStyleSheet("border:0;background-color:#E9EBEE;")
        line_seperator_widget.setFixedHeight(1)

        top_card_layout = QVBoxLayout()
        top_card_layout.setSpacing(10)
        top_card_layout.addLayout(context_menu_and_avatar_and_gender_and_time_and_name_layout)
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

        self.event_handled = False

        report_title_label = QLabel(data["report_title"])
        report_title_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        report_title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        report_title_label.setStyleSheet("""
         QLabel {
             background-color:transparent;
             color:#283B45;
         }
         """)

        report_title_font = report_title_label.font()
        report_title_font.setWeight(report_title_font.Weight.Medium)
        report_title_font.setPointSize(11)
        report_title_label.setFont(report_title_font)
        # -----------------------------------------------------------

        report_category_label = QLabel(data["category"])
        report_category_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        report_category_label.setContentsMargins(5, 0, 5, 0)
        report_category_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        report_category_label.setFixedHeight(25)
        report_category_label.setStyleSheet("""
            QLabel {
                border-radius:10px;
                background-color:#FFF2DF;
                color:#794B00;
            }
        """)

        report_category_font = report_category_label.font()
        report_category_font.setWeight(report_category_font.Weight.Medium)
        report_category_font.setPointSize(10)
        report_category_label.setFont(report_category_font)
        # -----------------------------------------------------------

        status_label = QLabel(data["status"])
        status_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        status_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        status_label.setStyleSheet("""
         QLabel {
             background-color:transparent;
             color:#66747E;
         }
         """)

        report_status_font = status_label.font()
        report_status_font.setWeight(report_status_font.Weight.Medium)
        report_status_font.setPointSize(10)
        status_label.setFont(report_status_font)

        # -----------------------------------------------------------

        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(0, 0, 0, 0)

        main_layout.addWidget(report_title_label)
        main_layout.addWidget(report_category_label)
        main_layout.addWidget(status_label)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 10, 0, 10)

        layout.addLayout(main_layout)

        self.setLayout(layout)
