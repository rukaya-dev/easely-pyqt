from PyQt6.QtCore import Qt, QSize, QObject, QEvent, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import QLineEdit, QWidget, QHBoxLayout, QToolButton, QVBoxLayout


class LoginCustomLineEditWithIcon(QWidget):
    def __init__(self, icon_path, placeholder_text, parent=None):
        super().__init__(parent)

        self.placeholder_text = placeholder_text
        self.icon_path = icon_path

        self.base_style_sheet = """
        QWidget {
            border:1px solid #C7C7C7;
            border-radius: 3px;
        }
        """
        self.focus_style_sheet = """
        QWidget {
            border:1px solid #8D8D8D;
            border-radius: 3px;
        }
        """

        self.line_edit = CustomLineEdit(self.placeholder_text)
        self.line_edit.lineEditFocusInSignal.connect(self.apply_focus_in_style)
        self.line_edit.lineEditFocusOutSignal.connect(self.apply_focus_out_style)

        icon = QIcon(self.icon_path)

        icon_button = QToolButton()
        icon_button.setIcon(icon)
        icon_button.setIconSize(QSize(20, 20))
        icon_button.setStyleSheet("border: 0;")
        icon_button.raise_()

        # Container widget
        self.container_widget = QWidget()
        self.container_widget.setStyleSheet(self.base_style_sheet)
        self.container_widget.setFixedSize(314, 50)

        container_layout = QHBoxLayout(self.container_widget)
        container_layout.setContentsMargins(15, 5, 5, 5)
        container_layout.setSpacing(10)
        container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        container_layout.addWidget(icon_button)
        container_layout.addWidget(self.line_edit)

        self.container_widget.setLayout(container_layout)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.container_widget)
        self.setLayout(layout)
        # self.setStyleSheet("background-color:red;")

    @pyqtSlot()
    def apply_focus_in_style(self):
        self.container_widget.setStyleSheet(self.focus_style_sheet)

    @pyqtSlot()
    def apply_focus_out_style(self):
        self.container_widget.setStyleSheet(self.base_style_sheet)


class WidgetEventFilter(QObject):
    def eventFilter(self, obj: QLineEdit, event):
        if event.type() == QEvent.Type.FocusIn:
            obj.setStyleSheet(
                """
                    QWidget {
                        border:1px solid #8D8D8D;
                        border-radius:2px;
                        background-color:white;
                        color:#2C2D33;
                        padding-left:10px;
                        padding-right:5px;
                    }
                    """
            )

        elif event.type() == QEvent.Type.FocusOut:
            obj.setStyleSheet(
                """
            QWidget {
            border: 1px solid #A1AEB4;
            border-radius: 7px;
            }
            """
            )

        return super().eventFilter(obj, event)


class CustomLineEdit(QLineEdit):
    lineEditFocusInSignal = pyqtSignal()
    lineEditFocusOutSignal = pyqtSignal()

    def __init__(self, placeholder_text, parent=None):
        super().__init__(parent)

        self.placeholder_text = placeholder_text

        self.setStyleSheet("border:0;color:#2C2D33;")
        self.setFixedSize(QSize(260, 30))
        self.setPlaceholderText(self.placeholder_text)

    def focusInEvent(self, event):
        self.lineEditFocusInSignal.emit()
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        self.lineEditFocusOutSignal.emit()
        super().focusOutEvent(event)
