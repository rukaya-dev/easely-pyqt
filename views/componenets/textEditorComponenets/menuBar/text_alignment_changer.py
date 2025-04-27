from PyQt6.QtCore import QSize, pyqtSlot
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QButtonGroup, QAbstractButton


class TextAlignmentChanger(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.border_style = "border-radius:3px;"

        self.text_alignment_btn_group = QButtonGroup()

        self.align_left_btn = QPushButton()
        self.align_left_btn.setIcon(QIcon(":resources/icons/align_left.svg"))
        self.align_left_btn.setIconSize(QSize(20, 20))
        self.align_left_btn.setFixedSize(QSize(30, 30))
        self.align_left_btn.setStyleSheet("border-radius:5px;")
        self.align_left_btn.setToolTip("Left Align")
        self.align_left_btn.setCheckable(True)

        self.align_center_btn = QPushButton()
        self.align_center_btn.setIcon(QIcon(":resources/icons/align_center.svg"))
        self.align_center_btn.setIconSize(QSize(20, 20))
        self.align_center_btn.setFixedSize(QSize(30, 30))
        self.align_center_btn.setCheckable(True)
        self.align_center_btn.setToolTip("Center Align")

        self.align_right_btn = QPushButton()
        self.align_right_btn.setFixedSize(QSize(30, 30))
        self.align_right_btn.setIcon(QIcon(":resources/icons/align_right.svg"))
        self.align_right_btn.setIconSize(QSize(20, 20))
        self.align_right_btn.setCheckable(True)
        self.align_right_btn.setToolTip("Right Align")

        self.align_justify_btn = QPushButton()
        self.align_justify_btn.setFixedSize(QSize(30, 30))
        self.align_justify_btn.setIcon(QIcon(":resources/icons/align_justify.svg"))
        self.align_justify_btn.setIconSize(QSize(20, 20))
        self.align_justify_btn.setCheckable(True)
        self.align_justify_btn.setToolTip("Justify")

        self.text_alignment_btn_group.addButton(self.align_left_btn)
        self.text_alignment_btn_group.addButton(self.align_right_btn)
        self.text_alignment_btn_group.addButton(self.align_center_btn)
        self.text_alignment_btn_group.addButton(self.align_justify_btn)

        self.text_alignment_btn_group.buttonClicked.connect(self.on_button_clicked)

        text_alignment_h_layout = QHBoxLayout()
        text_alignment_h_layout.setContentsMargins(0, 0, 0, 0)
        text_alignment_h_layout.setSpacing(0)

        text_alignment_h_layout.addWidget(self.align_left_btn)
        text_alignment_h_layout.addWidget(self.align_center_btn)
        text_alignment_h_layout.addWidget(self.align_right_btn)
        text_alignment_h_layout.addWidget(self.align_justify_btn)

        self.setLayout(text_alignment_h_layout)

        self.setStyleSheet("""
            QPushButton {
                border-radius:3px;
            }
        """)

    @pyqtSlot(QAbstractButton)
    def on_button_clicked(self, clicked_button):
        for button in self.text_alignment_btn_group.buttons():
            if button != clicked_button:
                button.setStyleSheet(self.border_style)
            else:
                button.setStyleSheet(
                    """QPushButton { background-color:#edeeee;border-radius:3px;}""")

    def set_active_alignment(self, checked_button):
        for button in self.text_alignment_btn_group.buttons():
            button.setStyleSheet(self.border_style)

        if checked_button.isChecked():
            checked_button.setStyleSheet(
                """QPushButton { background-color: #edeeee; border-radius:3px;}""")
