from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QPushButton, QWidget, QHBoxLayout

from views.componenets.customsComponents.buttons.button_with_loader import ButtonWithLoader


class SaveAndCancelButtonsWithLoader(QWidget):
    def __init__(self, text="Save", parent=None):
        super().__init__(parent)

        btn_size = QSize(82, 34)

        self.save_btn = ButtonWithLoader(text, size=QSize(95, 34))

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setFixedSize(btn_size)
        self.cancel_btn.setStyleSheet("""
        QPushButton {
            border:0;
            border-radius:3px;
            font-size:13pt;
            background-color:#e2e8f0;
            color:#4B4E58;
        }
        QPushButton:pressed {
            padding-top: 2px;
            padding-left: 2px;
            border:0;
            border-radius:3px;
            font-size:13pt;
            color:#4B4E58;
        }
        """)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.setSpacing(10)

        layout.addWidget(self.cancel_btn)
        layout.addWidget(self.save_btn)

        self.setFixedSize(QSize(350, 50))

        self.setLayout(layout)
