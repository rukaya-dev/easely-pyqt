from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon, QPalette
from PyQt6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QApplication


class ListStyleChanger(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.ordered_list_btn = QPushButton()
        self.ordered_list_btn.setObjectName("ordered_list_btn")
        self.ordered_list_btn.setIcon(QIcon(":resources/icons/ordered_list.svg"))
        self.ordered_list_btn.setIconSize(QSize(20, 20))
        self.ordered_list_btn.setFixedSize(QSize(30, 30))
        self.ordered_list_btn.setStyleSheet("border-radius:3px;")
        self.ordered_list_btn.setCheckable(True)

        self.un_ordered_list_btn = QPushButton()
        self.un_ordered_list_btn.setObjectName("un_ordered_list_btn")
        self.un_ordered_list_btn.setIcon(QIcon(":resources/icons/un_ordered_list.svg"))
        self.un_ordered_list_btn.setIconSize(QSize(20, 20))
        self.un_ordered_list_btn.setFixedSize(QSize(30, 30))
        self.un_ordered_list_btn.setCheckable(True)
        self.un_ordered_list_btn.setStyleSheet("border-radius:3px;")

        self.text_alignment_h_layout = QHBoxLayout()
        self.text_alignment_h_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.text_alignment_h_layout.setContentsMargins(0, 0, 0, 0)
        self.text_alignment_h_layout.setSpacing(10)

        self.text_alignment_h_layout.addWidget(self.ordered_list_btn)
        self.text_alignment_h_layout.addWidget(self.un_ordered_list_btn)

        self.setLayout(self.text_alignment_h_layout)

    def set_active_list_btn(self, button: QPushButton, checked):
        base_style = "border-radius: 3px;"

        if checked:
            base_style += f"background-color: #eceff7;"

        if button.objectName() == "ordered_list_btn":
            button.setStyleSheet(f"QPushButton {{ {base_style} }}")
            self.deactivate_other_button(self.un_ordered_list_btn)
        else:
            button.setStyleSheet(base_style)
            self.deactivate_other_button(self.ordered_list_btn)

    def deactivate_other_button(self, other_button: QPushButton):
        base_style = "border-radius: 3px;"
        other_button.setChecked(False)
        other_button.setStyleSheet(base_style)

