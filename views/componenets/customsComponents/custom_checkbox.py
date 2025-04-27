from PyQt6.QtWidgets import QCheckBox


class CustomCheckBox(QCheckBox):
    def __init__(self, name, parent=None):
        super().__init__(parent)

        self.setText(name)

        font = self.font()
        font.setPointSize(11)
        font.setWeight(font.Weight.Normal)
        self.setFont(font)

        self.setStyleSheet("""
            QCheckBox {
                spacing: 10px;
                color:black;
                background-color:transparent;
            }
            
            QCheckBox::indicator {
                width: 14px;
                height: 14px;
                border:1px solid #A1AEB4;
                border-radius: 3px;
            }
            
            QCheckBox::indicator:checked {
                width: 14px;
                height: 14px;
                border-radius: 3px;
                image: url(:/resources/icons/active_check.svg);
            }
            
            QCheckBox::indicator:checked:pressed {
                image: url(:/resources/icons/active_check.svg);
            }
        """)
