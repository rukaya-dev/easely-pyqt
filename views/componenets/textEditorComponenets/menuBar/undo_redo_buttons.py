from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget, QPushButton, QHBoxLayout


class UndoRedoButtons(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.undo_btn = QPushButton()
        self.undo_btn.setIcon(QIcon(":resources/icons/undo.svg"))
        self.undo_btn.setIconSize(QSize(20, 20))
        self.undo_btn.setFixedSize(QSize(30, 30))
        self.undo_btn.setStyleSheet("border-radius:5px;")
        self.undo_btn.setToolTip("Undo")

        self.redo_btn = QPushButton()
        self.redo_btn.setIcon(QIcon(":resources/icons/redo.svg"))
        self.redo_btn.setIconSize(QSize(20, 20))
        self.redo_btn.setFixedSize(QSize(30, 30))
        self.redo_btn.setStyleSheet("border-radius:5px;")
        self.redo_btn.setToolTip("Redo")


        text_alignment_h_layout = QHBoxLayout()
        text_alignment_h_layout.setContentsMargins(0, 0, 0, 0)
        text_alignment_h_layout.setSpacing(0)

        text_alignment_h_layout.addWidget(self.undo_btn)
        text_alignment_h_layout.addWidget(self.redo_btn)

        self.setLayout(text_alignment_h_layout)

        self.setStyleSheet("""
            QPushButton:hover {
                background-color:#edeeee;
            }
            QPushButton:pressed {
                background-color:white;
            }
        
        """)

    def toggle_undo_status(self, status):
        self.undo_btn.setEnabled(status)

    def toggle_redo_status(self, status):
        self.redo_btn.setEnabled(status)

