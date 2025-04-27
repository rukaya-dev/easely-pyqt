from PyQt6.QtCore import QSize
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QTimeEdit


class CustomTimePicker(QTimeEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

        font = self.font()
        font.setPointSize(10)
        self.setFont(font)

        self.setStyleSheet("""
            QTimeEdit  { 
                width: 50px;
                color: #4B4E58; 
                background-color: white; 
                selection-background-color:white ;
                selection-color: #2C2D33;
            }
            QTimeEdit QSpinBox::up-button {
                subcontrol-origin: border;
                subcontrol-position: top right;
                width:16px;
                border:0;
            }
            QTimeEdit QSpinBox::down-button {
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width:16px;
                border:0;
            }
            QTimeEdit QSpinBox::up-arrow {
                width:20px;
                height:20px;
                image: url(:/resources/icons/spin_up.svg);
            }
            QTimeEdit QSpinBox::down-arrow {
                width:20px;
                height:20px;
                image: url(:/resources/icons/spin_down.svg);
            }
        """)

        self.setFixedSize((QSize(100, 30)))
