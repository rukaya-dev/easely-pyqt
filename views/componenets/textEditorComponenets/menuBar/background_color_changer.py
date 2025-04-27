from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon, QColor
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QColorDialog, QDialog, QHBoxLayout


class BackgroundColorChanger(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.background_text_color_changer_btn = QPushButton()
        self.background_text_color_changer_btn.setStyleSheet("border:0;padding-left:20px;")
        self.background_text_color_changer_btn.setIcon(QIcon(":resources/icons/paint.svg"))
        self.background_text_color_changer_btn.setIconSize(QSize(24, 24))
        self.background_text_color_changer_btn.setFixedSize(QSize(30,30))

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.background_text_color_changer_btn)
        self.setLayout(layout)


class ColorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.selected_color = QColor()
        self.color_widget = QColorDialog()
        self.color_widget.setOptions(
            QColorDialog.ColorDialogOption.DontUseNativeDialog |
            QColorDialog.ColorDialogOption.NoButtons)

        hbox = QHBoxLayout()
        self.no_color = QPushButton('No Color')
        self.cancel = QPushButton('Cancel')
        self.ok = QPushButton('Ok')

        # Connect signals to slots
        self.ok.clicked.connect(self.acceptColor)
        self.cancel.clicked.connect(self.reject)
        self.no_color.clicked.connect(self.selectNoColor)

        hbox.addWidget(self.no_color)
        hbox.addWidget(self.cancel)
        hbox.addWidget(self.ok)

        layout = QVBoxLayout(self)
        layout.addWidget(self.color_widget)
        layout.addLayout(hbox)
        self.setLayout(layout)

        self.setModal(True)

    def acceptColor(self):
        self.selected_color = self.color_widget.currentColor()
        self.accept()

    def selectNoColor(self):
        self.selected_color = QColor()
        self.accept()

    def getColor(self):
        return self.selected_color

