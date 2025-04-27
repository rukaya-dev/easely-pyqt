from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QButtonGroup


class CustomTabWidget(QWidget):
    def __init__(self, tabs_buttons_data):
        super().__init__()

        self.tabs_buttons_data = tabs_buttons_data
        self.button_group = QButtonGroup()

        self.button_group.buttonClicked.connect(self.change_btn_style_when_selected)

        self.layout = QHBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignBottom)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(50)

        self.setStyleSheet("background-color:yellow;")

        self.setLayout(self.layout)
        # self.set_up_buttons()

    def create_tab_button(self, name):
        button = QPushButton(name)
        button.setFixedHeight(40)
        button.setStyleSheet("""
            QPushButton {
                border: 0;
                border-bottom: 1px solid transparent;
                background-color: transparent;
                color: #445C9E;
                margin-top:5px;
                padding-left: 5px;
                padding-right: 5px;
                background-color:transparent;
                
            }
        """)

        font = button.font()
        font.setPointSize(12)
        font.setWeight(font.Weight.Normal)

        button.setFont(font)
        return button

    def set_up_buttons(self):
        for tab_button in self.tabs_buttons_data:
            button = self.create_tab_button(tab_button["button_name"])
            button.pageName = tab_button["page_name"]
            self.button_group.addButton(button)
            self.layout.addWidget(button)

    def change_btn_style_when_selected(self, button):
        button.setChecked(True)
        button.setStyleSheet("""
             QPushButton {
                border:0;
                border-bottom: 1px solid #989FA8;
                color: #445C9E;
                padding-left: 5px;
                padding-right: 5px;
                margin-top:5px;
                background-color:transparent;

            }
        """)

        # Optionally, reset the other buttons to their default stylesheet
        for btn in self.button_group.buttons():
            if btn != button:
                btn.setStyleSheet("""
               QPushButton {
                    border: 0;
                    border-bottom: 1px solid transparent;
                    color: #445C9E;
                    padding-left: 5px;
                    padding-right: 5px;
                    margin-top:5px;
                    background-color:transparent;
                }
                """)
