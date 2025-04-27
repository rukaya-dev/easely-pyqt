from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout


class QuickNotifier(QWidget):
    ICONS = {
        "error": ":/resources/icons/error_notification.svg",
        "success": ":/resources/icons/success_notification.svg"
    }
    STYLES = {
        "error": "border:1px solid red; border-radius:3px;",
        "success": "border:1px solid #CECECE; border-radius:3px;"
    }
    COLORS = {
        "error": "#EF4444",
        "success": "#F6F8FA"
    }

    def __init__(self, message_type, message, duration, parent=None):
        super().__init__(parent)

        self.setFixedWidth(400)
        self.setMinimumHeight(100)

        self.parent = parent
        self.central_widget = None
        self.message = message
        self.duration = duration
        self.init_ui(message_type)

    def init_ui(self, message_type):
        # Create layouts
        main_layout = QHBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        main_layout.setSpacing(20)

        # central_widget
        self.central_widget = QWidget()
        self.central_widget.setObjectName("central_widget")
        self.central_widget.setLayout(main_layout)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.central_widget)

        self.setLayout(layout)

        # Create icon label
        icon_label = QLabel()
        icon_pixmap = QIcon(self.ICONS[message_type]).pixmap(50, 50)
        icon_label.setPixmap(icon_pixmap)
        icon_label.setFixedSize(QSize(50, 50))

        # Create message header

        message_header = QLabel("Error" if message_type == "error" else "Success")
        message_header.setAlignment(Qt.AlignmentFlag.AlignLeft)
        message_header.setStyleSheet("background-color:transparent;")

        font = message_header.font()
        font.setPointSize(14)
        font.setWeight(font.Weight.Medium)
        message_header.setFont(font)

        # Create message content
        message_content = QLabel(self.message)
        message_content.setAlignment(Qt.AlignmentFlag.AlignLeft)
        message_content.setStyleSheet("background-color:transparent;")
        # message_content.setWordWrap(True)

        message_content_font = message_content.font()
        message_content_font.setPointSize(12)
        message_content_font.setWeight(font.Weight.Normal)
        message_content.setFont(message_content_font)

        # Create vertical layout for the text
        text_layout = QVBoxLayout()
        text_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        text_layout.setSpacing(10)
        # text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.addWidget(message_header)
        text_layout.addWidget(message_content)

        # Add widgets to the main layout
        main_layout.addWidget(icon_label)
        main_layout.addLayout(text_layout)

        # Set styles
        self.setStyleSheet(f"""
            QWidget#central_widget {{
                background-color: {self.COLORS[message_type]};
                {self.STYLES[message_type]}
            }}
            QLabel {{
                color:black;
            }}
      
        """)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        QTimer.singleShot(self.duration, self.deleteLater)
